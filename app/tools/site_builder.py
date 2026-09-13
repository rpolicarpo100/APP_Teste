"""
Site/App Builder — Ferramenta REAL para construir sites e apps via chat
Gera HTML/CSS/JS completo, bonito e leve, guarda em data/workspace
"""
from pathlib import Path
from app.tools.registry import register_tool
from app.config.settings import settings, ROOT_DIR
import uuid
import re

def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text[:40] or "site"

def _generate_landing_html(objective: str, style: str = "moderno minimalista", brand: str = "BRAIN", features: list = None) -> str:
    """Gera HTML bonito e leve para landing page / app"""
    features = features or ["Rápido e leve", "100% local", "Sem cloud", "Bonito por defeito"]
    
    # Detecta tipo de site pelo objectivo
    obj_lower = objective.lower()
    if "trading" in obj_lower:
        title = "Trading Tools — Leve & Bonito"
        subtitle = "Ferramentas curadas, sem ruído. Só o que funciona."
        cta = "Começar agora"
        features = ["Ferramentas gratuitas verificadas", "Sem spam, sem paywall", "100% local", "Actualizado semanalmente"]
        accent = "#ff4d1a"
    elif "loja" in obj_lower or "ecommerce" in obj_lower or "shop" in obj_lower:
        title = "Loja Minimalista"
        subtitle = "Produtos essenciais, design essencial."
        cta = "Ver produtos"
        accent = "#1a1a1a"
    elif "portfolio" in obj_lower or "portfólio" in obj_lower:
        title = "Portfolio — Leve & Bonito"
        subtitle = "Trabalho que fala por si."
        cta = "Ver projectos"
        accent = "#2563eb"
    elif "app" in obj_lower:
        title = "App Leve & Bonita"
        subtitle = "Rápida, bonita, funciona offline."
        cta = "Abrir app"
        accent = "#7c3aed"
    else:
        title = objective[:50] if len(objective) < 50 else "Landing Page — Leve & Bonita"
        subtitle = "Criado pelo Brain via chat — 100% local, sem cloud."
        cta = "Começar"
        accent = "#ff4d1a"

    html = f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root{{--accent:{accent};--bg:#fbf9f6;--card:#fff;--border:#efe6dc;--text:#1e1c1a;--text2:#7a7068;--r:20px}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:ui-sans-system,-apple-system,Inter,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}}
  .nav{{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;background:rgba(255,255,255,0.8);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);position:sticky;top:0}}
  .logo{{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:-0.3px}}
  .logo-mark{{width:32px;height:32px;background:var(--text);color:white;border-radius:9px;display:grid;place-items:center;font-size:13px}}
  .hero{{max-width:1120px;margin:0 auto;padding:80px 28px 60px;display:grid;grid-template-columns:1.2fr 0.8fr;gap:40px;align-items:center}}
  .hero h1{{font-size:48px;letter-spacing:-1.5px;line-height:0.95;margin-bottom:16px;font-weight:800}}
  .hero h1 span{{color:var(--accent)}}
  .hero p{{font-size:16px;color:var(--text2);max-width:480px;margin-bottom:24px;line-height:1.5}}
  .btns{{display:flex;gap:10px}}
  .btn{{padding:13px 20px;border-radius:12px;border:none;font-weight:700;font-size:13px;cursor:pointer;display:flex;align-items:center;gap:6px;transition:all .2s}}
  .btn-primary{{background:var(--text);color:white}} .btn-primary:hover{{background:black;transform:translateY(-1px)}}
  .btn-ghost{{background:var(--card);border:1px solid var(--border);color:var(--text2)}} .btn-ghost:hover{{border-color:var(--text)}}
  .mock{{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:18px;box-shadow:0 12px 40px rgba(30,28,26,0.08);transform:rotate(1deg)}}
  .mock-top{{display:flex;gap:6px;margin-bottom:14px}} .dot{{width:10px;height:10px;border-radius:50%;background:var(--border)}}
  .mock-card{{background:var(--bg);border:1px solid var(--border);border-radius:14px;padding:14px;margin-bottom:10px}}
  .mock-card b{{font-size:12px;display:block;margin-bottom:4px}} .mock-card span{{font-size:11px;color:var(--text2)}}
  .features{{max-width:1120px;margin:0 auto;padding:20px 28px 60px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
  .feat{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:18px}}
  .feat-ico{{width:36px;height:36px;border-radius:10px;background:var(--bg);display:grid;place-items:center;margin-bottom:10px;font-size:16px}}
  .feat b{{font-size:13px;display:block;margin-bottom:4px}} .feat span{{font-size:11px;color:var(--text2);line-height:1.4}}
  .footer{{max-width:1120px;margin:0 auto;padding:20px 28px 40px;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:11px;color:var(--text2)}}
  @media(max-width:900px){{.hero{{grid-template-columns:1fr;padding:40px 20px}} .hero h1{{font-size:36px}} .features{{grid-template-columns:repeat(2,1fr)}}}}
</style>
</head>
<body>
  <div class="nav">
    <div class="logo"><div class="logo-mark">B</div> {brand}</div>
    <div style="display:flex;gap:8px">
      <button class="btn btn-ghost" style="padding:8px 14px;font-size:12px">Docs</button>
      <button class="btn btn-primary" style="padding:8px 14px;font-size:12px">{cta}</button>
    </div>
  </div>

  <div class="hero">
    <div>
      <h1>{title.split(' — ')[0]} <span>{title.split(' — ')[1] if ' — ' in title else 'bonita.'}</span></h1>
      <p>{subtitle} — Criado via chat com Brain. Objectivo original: "{objective[:120]}" — Estilo: {style}.</p>
      <div class="btns">
        <button class="btn btn-primary">{cta} →</button>
        <button class="btn btn-ghost">Ver como foi feito</button>
      </div>
      <div style="margin-top:18px;display:flex;gap:8px;flex-wrap:wrap">
        {"".join([f'<span style="font-size:10px;font-weight:700;padding:5px 10px;background:var(--card);border:1px solid var(--border);border-radius:999px">✓ {f}</span>' for f in features[:4]])}
      </div>
    </div>
    <div class="mock">
      <div class="mock-top"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
      <div class="mock-card"><b>✦ Missão criada</b><span>{objective[:60]} — via chat</span></div>
      <div class="mock-card"><b>◍ Agentes</b><span>Research → Design → Coding — 3 tarefas</span></div>
      <div class="mock-card"><b>⚡ Build</b><span>HTML leve 12KB, sem dependências, 100% local</span></div>
      <div style="margin-top:12px;padding:10px;background:var(--text);color:white;border-radius:10px;font-size:11px;font-weight:700;text-align:center">Leve mas bonita — {style}</div>
    </div>
  </div>

  <div class="features">
    {"".join([f'<div class="feat"><div class="feat-ico">{"🔍" if i==0 else "🎨" if i==1 else "⚡" if i==2 else "♡"}</div><b>{f}</b><span>Criado automaticamente pelo Brain via chat, sem cloud.</span></div>' for i,f in enumerate(features)])}
  </div>

  <div class="footer">
    <span>© {brand} — Criado via chat com Brain • Leve & Bonita • 100% local</span>
    <span>Objectivo: {objective[:40]}... • Estilo: {style}</span>
  </div>
</body>
</html>
"""
    return html

@register_tool(
    id="site.builder",
    name="Site Builder",
    description="Constrói site/app completo HTML bonito e leve, guarda em data/workspace",
    risk_level="MEDIUM",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"objective": {"type": "string"}, "style": {"type": "string"}, "brand": {"type": "string"}}, "required": ["objective"]},
    output_schema={"type": "object", "properties": {"path": {"type": "string"}, "url": {"type": "string"}}}
)
def site_builder(objective: str, style: str = "moderno minimalista", brand: str = "BRAIN") -> dict:
    try:
        workspace = ROOT_DIR / settings.workspace_path
        workspace.mkdir(parents=True, exist_ok=True)

        slug = _slugify(objective)
        filename = f"{slug}-{uuid.uuid4().hex[:6]}.html"
        filepath = workspace / filename

        html = _generate_landing_html(objective=objective, style=style, brand=brand)

        filepath.write_text(html, encoding="utf-8")

        # URL para preview — via /workspace static mount
        url = f"/workspace/{filename}"

        return {
            "path": str(filepath),
            "filename": filename,
            "url": url,
            "preview_url": url,
            "size": len(html),
            "objective": objective,
            "style": style,
            "built": True,
            "message": f"Site construído: {filename} — {len(html)} bytes — leve e bonito"
        }
    except Exception as e:
        return {"error": str(e), "built": False, "objective": objective}
