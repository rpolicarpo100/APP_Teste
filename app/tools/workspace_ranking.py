"""
Workspace Ranking — Após sessão fechada, analisa workspace do utilizador, dá ranking 0-100
Se bom (>=70) guarda, se não esquece totalmente (apaga)
"""
from pathlib import Path
from typing import Dict, Any, List
import re
from app.tools.registry import register_tool
from app.config.settings import ROOT_DIR, settings

def _analyze_html_quality(html: str) -> Dict[str, Any]:
    score = 0
    reasons = []
    
    # Tamanho
    size = len(html)
    if size < 500:
        reasons.append(f"Muito pequeno: {size} bytes (-20)")
        score -= 20
    elif size < 2000:
        reasons.append(f"Pequeno: {size} bytes (+10)")
        score += 10
    elif 2000 <= size <= 15000:
        reasons.append(f"Tamanho ideal: {size} bytes (+25)")
        score += 25
    elif size > 50000:
        reasons.append(f"Muito grande: {size} bytes (+10)")
        score += 10
    else:
        score += 15
    
    # Tem título?
    if re.search(r'<title>[^<]{5,}</title>', html, re.I):
        score += 15
        reasons.append("Tem título válido (+15)")
    else:
        reasons.append("Sem título (-10)")
        score -= 10
    
    # Tem conteúdo significativo?
    text = re.sub(r'<[^>]+>', '', html)
    text = text.strip()
    if len(text) < 100:
        reasons.append(f"Conteúdo muito curto: {len(text)} chars (-15)")
        score -= 15
    elif len(text) < 500:
        score += 10
        reasons.append(f"Conteúdo curto: {len(text)} chars (+10)")
    else:
        score += 20
        reasons.append(f"Conteúdo bom: {len(text)} chars (+20)")
    
    # Tem estrutura HTML válida?
    if '<!DOCTYPE html>' in html or '<!doctype html>' in html.lower():
        score += 10
        reasons.append("Tem DOCTYPE (+10)")
    if '<html' in html.lower() and '</html>' in html.lower():
        score += 10
        reasons.append("HTML completo (+10)")
    
    # Tem CSS?
    if '<style' in html.lower() or 'style=' in html.lower():
        score += 10
        reasons.append("Tem CSS (+10)")
    
    # Tem YouTube / Deadly Gods / conteúdo gamer?
    lower = html.lower()
    if 'youtube' in lower or 'deadly' in lower or 'gods' in lower:
        score += 15
        reasons.append("Conteúdo YouTube/Deadly Gods relevante (+15)")
    
    # Tem links, botões, CTA?
    if '<a ' in lower or '<button' in lower:
        score += 5
        reasons.append("Tem links/botões (+5)")
    
    # Penaliza se for placeholder vazio
    if 'lorem ipsum' in lower and len(text) < 300:
        score -= 15
        reasons.append("Lorem ipsum placeholder (-15)")
    
    # Normaliza 0-100
    score = max(0, min(100, score))
    
    return {"score": score, "reasons": reasons, "size": size, "text_len": len(text)}

@register_tool(
    id="workspace.ranking",
    name="Workspace Ranking",
    description="Analisa workspace do utilizador após sessão fechada, dá ranking 0-100, se bom guarda se não esquece",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"workspace_path": {"type": "string"}, "session_id": {"type": "string"}}, "required": []},
    output_schema={"type": "object", "properties": {"ranking": {"type": "number"}, "files": {"type": "array"}}}
)
def workspace_ranking(workspace_path: str = None, session_id: str = None) -> Dict[str, Any]:
    try:
        ws = Path(workspace_path) if workspace_path else ROOT_DIR / settings.workspace_path
        ws.mkdir(parents=True, exist_ok=True)
        
        files = list(ws.glob("*.html")) + list(ws.glob("*.svg")) + list(ws.glob("*.js")) + list(ws.glob("*.css"))
        results = []
        total_score = 0
        
        for f in files[-20:]:  # últimos 20 ficheiros
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                analysis = _analyze_html_quality(content)
                # Verifica se é recente (última sessão)
                import time
                mtime = f.stat().st_mtime
                age_hours = (time.time() - mtime) / 3600
                
                results.append({
                    "filename": f.name,
                    "path": str(f),
                    "size": analysis["size"],
                    "text_len": analysis["text_len"],
                    "score": analysis["score"],
                    "reasons": analysis["reasons"],
                    "age_hours": round(age_hours, 2),
                    "is_good": analysis["score"] >= 70
                })
                total_score += analysis["score"]
            except Exception as e:
                results.append({"filename": f.name, "error": str(e), "score": 0, "is_good": False})
        
        avg_score = total_score / len(results) if results else 0
        good_files = [r for r in results if r.get("is_good")]
        bad_files = [r for r in results if not r.get("is_good")]
        
        # Decide: se bom guarda, se não esquece totalmente
        action = "GUARDAR" if avg_score >= 70 or len(good_files) > 0 else "ESQUECER"
        
        return {
            "session_id": session_id,
            "workspace": str(ws),
            "total_files": len(files),
            "analyzed": len(results),
            "avg_score": round(avg_score, 2),
            "good_count": len(good_files),
            "bad_count": len(bad_files),
            "action": action,
            "ranking": round(avg_score, 2),
            "files": results,
            "message": f"Workspace ranking: {avg_score:.1f}/100 — {len(good_files)} bons, {len(bad_files)} maus — Ação: {action}"
        }
    except Exception as e:
        return {"error": str(e), "ranking": 0, "action": "ESQUECER"}

@register_tool(
    id="workspace.cleanup",
    name="Workspace Cleanup",
    description="Após ranking, se mau esquece totalmente (apaga ficheiros maus)",
    risk_level="MEDIUM",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"min_score": {"type": "number"}, "dry_run": {"type": "boolean"}}, "required": []},
    output_schema={"type": "object", "properties": {"deleted": {"type": "array"}}}
)
def workspace_cleanup(min_score: int = 70, dry_run: bool = True) -> Dict[str, Any]:
    try:
        ws = ROOT_DIR / settings.workspace_path
        ranking = workspace_ranking(str(ws))
        
        to_delete = [f for f in ranking.get("files", []) if f.get("score", 0) < min_score]
        deleted = []
        
        if not dry_run:
            for f in to_delete:
                try:
                    Path(f["path"]).unlink(missing_ok=True)
                    deleted.append(f["filename"])
                except Exception as e:
                    pass
        else:
            deleted = [f["filename"] for f in to_delete]
        
        return {
            "min_score": min_score,
            "dry_run": dry_run,
            "to_delete_count": len(to_delete),
            "deleted": deleted,
            "kept": [f["filename"] for f in ranking.get("files", []) if f.get("score", 0) >= min_score],
            "message": f"{'Simulação' if dry_run else 'Apagados'} {len(deleted)} ficheiros maus (<{min_score}), mantidos {len(ranking.get('files', [])) - len(to_delete)} bons"
        }
    except Exception as e:
        return {"error": str(e), "deleted": []}
