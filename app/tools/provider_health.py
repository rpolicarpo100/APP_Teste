"""
Tools para Provider Health — check e ranking
"""
from app.tools.registry import register_tool
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"

def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@register_tool(
    id="provider.health_check",
    name="Verificar saúde providers",
    description="Verifica se todos os providers do cérebro estão a funcionar (APIs externas, Ollama, DB, filesystem)",
    risk_level="LOW"
)
def health_check_tool(provider_id: str = None) -> dict:
    """Verifica saúde de um ou todos os providers"""
    try:
        from app.agents.provider_health import ProviderHealthAgent, PROVIDERS_CONFIG
        from app.agents.base import TaskInput
        import uuid
        
        agent = ProviderHealthAgent()
        
        if provider_id:
            # Check específico
            if provider_id not in PROVIDERS_CONFIG:
                return {"error": f"Provider {provider_id} não encontrado", "available": list(PROVIDERS_CONFIG.keys())}
            config = PROVIDERS_CONFIG[provider_id]
            result = agent._check_provider(provider_id, config)
            agent._update_ranking(result)
            return {"provider": result, "status": "checked"}
        else:
            # Check todos
            task = TaskInput(
                task_id=str(uuid.uuid4()),
                mission_id=str(uuid.uuid4()),
                agent_id="provider_health",
                objective="verificar saúde de todos os providers"
            )
            output = agent.execute(task)
            return {
                "summary": output.summary,
                "health": [a["data"] for a in output.artifacts if a["type"] == "provider_health"][0] if output.artifacts else [],
                "ranking": [a["data"] for a in output.artifacts if a["type"] == "provider_ranking"][0] if len(output.artifacts) > 1 else []
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@register_tool(
    id="provider.ranking",
    name="Ranking providers por experiência",
    description="Retorna ranking de providers baseado em experiência (success rate, latência, fails)",
    risk_level="LOW"
)
def ranking_tool(category: str = None) -> dict:
    """Retorna ranking de providers"""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        if category:
            cur.execute("SELECT * FROM provider_rankings WHERE category=? ORDER BY score DESC, rank ASC", (category,))
        else:
            cur.execute("SELECT * FROM provider_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        
        # Agrupa por categoria e mostra preferência
        by_cat = {}
        for r in rankings:
            cat = r["category"]
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(r)
        
        # Melhor por categoria
        best_by_category = {}
        for cat, providers in by_cat.items():
            if providers:
                best = max(providers, key=lambda x: x["score"] or 0)
                best_by_category[cat] = {
                    "provider_id": best["provider_id"],
                    "name": best["name"],
                    "score": best["score"],
                    "experience": best["experience_points"],
                    "status": best["status"]
                }
        
        conn.close()
        
        return {
            "rankings": rankings,
            "by_category": by_cat,
            "best_by_category": best_by_category,
            "total": len(rankings)
        }
    except Exception as e:
        return {"error": str(e)}

@register_tool(
    id="provider.failover",
    name="Failover provider",
    description="Força failover de um provider para alternativa com base no ranking",
    risk_level="MEDIUM"
)
def failover_tool(provider_id: str, force_alternative: str = None) -> dict:
    """Força failover para alternativa"""
    try:
        from app.agents.provider_health import PROVIDERS_CONFIG
        conn = _get_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM provider_rankings WHERE provider_id=?", (provider_id,))
        row = cur.fetchone()
        if not row:
            return {"error": f"Provider {provider_id} não encontrado"}
        
        config = PROVIDERS_CONFIG.get(provider_id, {})
        alternatives = config.get("alternatives", [])
        
        if force_alternative:
            if force_alternative not in alternatives:
                return {"error": f"Alternativa {force_alternative} não válida", "available": alternatives}
            alternative = force_alternative
        else:
            # Escolhe melhor alternativa baseada em ranking
            if not alternatives:
                return {"error": "Sem alternativas configuradas"}
            # Procura alternativa com melhor score
            placeholders = ",".join(["?"] * len(alternatives))
            cur.execute(f"SELECT provider_id, score FROM provider_rankings WHERE provider_id IN ({placeholders}) ORDER BY score DESC", alternatives)
            alt_ranked = cur.fetchall()
            if alt_ranked:
                alternative = alt_ranked[0]["provider_id"]
            else:
                alternative = alternatives[0]
        
        cur.execute("""
        UPDATE provider_rankings SET alternative_in_use=?, status='failover', updated_at=?
        WHERE provider_id=?
        """, (alternative, datetime.utcnow().isoformat(), provider_id))
        conn.commit()
        conn.close()
        
        return {
            "provider_id": provider_id,
            "failed_over_to": alternative,
            "status": "failover",
            "message": f"Provider {provider_id} agora usa alternativa {alternative}"
        }
    except Exception as e:
        return {"error": str(e)}
