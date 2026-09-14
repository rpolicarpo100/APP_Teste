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
    
    # Detecta tipo de site pelo objectivo — melhorado para YouTube e AI
    obj_lower = objective.lower()
    if "youtube" in obj_lower or "deadly" in obj_lower or "gods" in obj_lower or "canal" in obj_lower:
        # Site para canal YouTube Deadly Gods Portugal
        title = "Deadly Gods Portugal — Canal YouTube"
        subtitle = "Gameplays épicos, análises e comunidade gamer portuguesa. Subscreve no YouTube."
        cta = "Ver no YouTube"
        features = ["Gameplays épicos", "Análises honestas", "Comunidade portuguesa", "Novos vídeos semanais"]
        accent = "#ff0000"  # YouTube red
        # HTML especial para YouTube
        is_youtube = True
    elif "ai" in obj_lower or "\bia\b" in obj_lower or "bot" in obj_lower or "assistente" in obj_lower:
        title = "AI Assistant — Criado via Chat"
        subtitle = "Assistente inteligente construído pelo Brain — 100% local, sem cloud, custo 0."
        cta = "Falar com AI"
        features = ["100% local", "Sem cloud", "Custo 0", "Groq + Gemini + Neon"]
        accent = "#7c3aed"
        is_youtube = False
    elif "trading" in obj_lower:
        title = "Trading Tools — Leve & Bonito"
        subtitle = "Ferramentas curadas, sem ruído. Só o que funciona."
        cta = "Começar agora"
        features = ["Ferramentas gratuitas verificadas", "Sem spam, sem paywall", "100% local", "Actualizado semanalmente"]
        accent = "#ff4d1a"
        is_youtube = False
    elif "loja" in obj_lower or "ecommerce" in obj_lower or "shop" in obj_lower:
        title = "Loja Minimalista"
        subtitle = "Produtos essenciais, design essencial."
        cta = "Ver produtos"
        accent = "#1a1a1a"
        is_youtube = False
    elif "portfolio" in obj_lower or "portfólio" in obj_lower:
        title = "Portfolio — Leve & Bonito"
        subtitle = "Trabalho que fala por si."
        cta = "Ver projectos"
        accent = "#2563eb"
        is_youtube = False
    elif "app" in obj_lower:
        title = "App Leve & Bonita"
        subtitle = "Rápida, bonita, funciona offline."
        cta = "Abrir app"
        accent = "#7c3aed"
        is_youtube = False
    else:
        title = objective[:50] if len(objective) < 50 else "Landing Page — Leve & Bonita"
        subtitle = "Criado pelo Brain via chat — 100% local, sem cloud."
        cta = "Começar"
        accent = "#ff4d1a"
        is_youtube = False

    # Se for YouTube, gera HTML gamer épico para Deadly Gods
    if 'is_youtube' in locals() and is_youtube:
        youtube_url = "https://www.youtube.com/@Deadly_Gods_Portugal"
        # Extrai URL do objectivo se existir
        import re as _re
        m = _re.search(r'https?://[^\s]+youtube[^\s]+', objective)
        if m:
            youtube_url = m.group(0)
        
        html = f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=Inter:wght@400;600;700&display=swap');
  :root{{--accent:{accent};--bg:#0a0a0b;--card:#151517;--border:#252529;--text:#f5f3f0;--text2:#9a9590;--r:20px}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:Inter,ui-sans-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}}
  .nav{{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;background:rgba(10,10,11,0.8);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:10}}
  .logo{{display:flex;align-items:center;gap:12px;font-weight:800;letter-spacing:-0.5px;font-family:'Space Grotesk',sans-serif;font-size:18px}}
  .logo-mark{{width:36px;height:36px;background:var(--accent);color:white;border-radius:10px;display:grid;place-items:center;font-size:18px;font-weight:800;box-shadow:0 0 20px rgba(255,0,0,0.4)}}
  .hero{{max-width:1200px;margin:0 auto;padding:80px 28px 60px;display:grid;grid-template-columns:1.2fr 0.8fr;gap:50px;align-items:center;position:relative}}
  .hero::before{{content:'';position:absolute;top:-100px;right:-100px;width:500px;height:500px;background:radial-gradient(circle, rgba(255,0,0,0.15) 0%, transparent 70%);pointer-events:none}}
  .hero h1{{font-family:'Space Grotesk',sans-serif;font-size:56px;letter-spacing:-2px;line-height:0.9;margin-bottom:20px;font-weight:800}}
  .hero h1 span{{color:var(--accent);text-shadow:0 0 30px rgba(255,0,0,0.5)}}
  .hero p{{font-size:17px;color:var(--text2);max-width:520px;margin-bottom:28px;line-height:1.6}}
  .btns{{display:flex;gap:12px;flex-wrap:wrap}}
  .btn{{padding:14px 24px;border-radius:12px;border:none;font-weight:700;font-size:14px;cursor:pointer;display:flex;align-items:center;gap:8px;transition:all .2s;text-decoration:none}}
  .btn-primary{{background:var(--accent);color:white;box-shadow:0 4px 20px rgba(255,0,0,0.3)}} .btn-primary:hover{{background:#cc0000;transform:translateY(-2px);box-shadow:0 8px 30px rgba(255,0,0,0.4)}}
  .btn-ghost{{background:var(--card);border:1px solid var(--border);color:var(--text)}} .btn-ghost:hover{{border-color:var(--text);background:#1e1e20}}
  .yt-embed{{background:var(--card);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);position:relative}}
  .yt-header{{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}}
  .yt-avatar{{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg, #ff0000, #990000);display:grid;place-items:center;font-weight:800;color:white}}
  .yt-info b{{display:block;font-size:14px}} .yt-info span{{font-size:12px;color:var(--text2)}}
  .yt-video{{aspect-ratio:16/9;background:#000;display:grid;place-items:center;position:relative;overflow:hidden}}
  .yt-video iframe{{width:100%;height:100%;border:none}}
  .yt-placeholder{{text-align:center;padding:40px 20px}}
  .yt-placeholder .play{{width:80px;height:80px;background:var(--accent);border-radius:50%;display:grid;place-items:center;margin:0 auto 16px;font-size:32px;cursor:pointer;box-shadow:0 0 40px rgba(255,0,0,0.5);transition:transform .2s}}
  .yt-placeholder .play:hover{{transform:scale(1.1)}}
  .features{{max-width:1200px;margin:0 auto;padding:40px 28px 60px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
  .feat{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:22px;transition:all .2s}} .feat:hover{{border-color:#333;transform:translateY(-2px)}}
  .feat-ico{{width:44px;height:44px;border-radius:12px;background:#1e1e20;display:grid;place-items:center;margin-bottom:14px;font-size:20px;border:1px solid var(--border)}}
  .feat b{{font-size:14px;display:block;margin-bottom:6px;font-family:'Space Grotesk',sans-serif}} .feat span{{font-size:12px;color:var(--text2);line-height:1.5}}
  .videos{{max-width:1200px;margin:0 auto;padding:0 28px 60px}}
  .videos h2{{font-family:'Space Grotesk',sans-serif;font-size:28px;margin-bottom:20px;letter-spacing:-0.5px}}
  .video-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
  .video-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;transition:all .2s}} .video-card:hover{{border-color:#333;transform:translateY(-2px)}}
  .video-thumb{{aspect-ratio:16/9;background:#0f0f10;display:grid;place-items:center;font-size:12px;color:var(--text2);position:relative}}
  .video-thumb::after{{content:'▶';position:absolute;width:48px;height:48px;background:rgba(255,0,0,0.9);border-radius:50%;display:grid;place-items:center;color:white;font-size:16px;top:50%;left:50%;transform:translate(-50%,-50%)}}
  .video-info{{padding:14px}} .video-info b{{font-size:13px;display:block;margin-bottom:4px;line-height:1.3}} .video-info span{{font-size:11px;color:var(--text2)}}
  .cta-section{{max-width:1200px;margin:0 auto 60px;padding:40px 28px;background:linear-gradient(135deg, #151517 0%, #1a0a0a 100%);border:1px solid #2a1a1a;border-radius:20px;text-align:center;position:relative;overflow:hidden}}
  .cta-section::before{{content:'';position:absolute;top:-50px;left:-50px;width:300px;height:300px;background:radial-gradient(circle, rgba(255,0,0,0.1) 0%, transparent 70%)}}
  .cta-section h2{{font-family:'Space Grotesk',sans-serif;font-size:32px;margin-bottom:12px;position:relative}} .cta-section p{{color:var(--text2);max-width:600px;margin:0 auto 24px;position:relative}}
  .footer{{max-width:1200px;margin:0 auto;padding:30px 28px 40px;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:11px;color:var(--text2);flex-wrap:wrap;gap:12px}}
  @media(max-width:900px){{.hero{{grid-template-columns:1fr;padding:50px 20px}} .hero h1{{font-size:40px}} .features{{grid-template-columns:repeat(2,1fr)}} .video-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
  <div class="nav">
    <div class="logo"><div class="logo-mark">DG</div> Deadly Gods Portugal</div>
    <div style="display:flex;gap:10px">
      <a href="{youtube_url}" target="_blank" class="btn btn-ghost" style="padding:10px 16px;font-size:13px">🔔 Subscrever</a>
      <a href="{youtube_url}" target="_blank" class="btn btn-primary" style="padding:10px 16px;font-size:13px">▶ Ver Canal</a>
    </div>
  </div>

  <div class="hero">
    <div>
      <h1>Deadly Gods <span>Portugal</span></h1>
      <p>{subtitle} Gameplays intensos, análises sem filtro e a melhor comunidade gamer portuguesa no YouTube. Junta-te a nós!</p>
      <div class="btns">
        <a href="{youtube_url}" target="_blank" class="btn btn-primary">▶ Ver no YouTube →</a>
        <a href="{youtube_url}/videos" target="_blank" class="btn btn-ghost">📺 Últimos Vídeos</a>
      </div>
      <div style="margin-top:22px;display:flex;gap:10px;flex-wrap:wrap">
        {"".join([f'<span style="font-size:11px;font-weight:700;padding:6px 12px;background:var(--card);border:1px solid var(--border);border-radius:999px;display:flex;align-items:center;gap:6px">✓ {f}</span>' for f in features])}
      </div>
    </div>
    <div class="yt-embed">
      <div class="yt-header">
        <div class="yt-avatar">DG</div>
        <div class="yt-info"><b>Deadly Gods Portugal</b><span>@Deadly_Gods_Portugal • 1.2K subscritores</span></div>
        <div style="margin-left:auto;width:8px;height:8px;background:#ff0000;border-radius:50%;box-shadow:0 0 10px #ff0000;animation:pulse 2s infinite"></div>
      </div>
      <div class="yt-video">
        <div class="yt-placeholder">
          <div class="play" onclick="window.open('{youtube_url}','_blank')">▶</div>
          <b style="display:block;margin-bottom:6px">Canal YouTube</b>
          <span style="font-size:12px;color:var(--text2)">Clica para abrir {youtube_url}</span>
          <div style="margin-top:16px">
            <iframe width="100%" height="200" src="https://www.youtube.com/embed?listType=user_uploads&list=Deadly_Gods_Portugal" frameborder="0" allowfullscreen style="border-radius:10px;max-width:360px"></iframe>
          </div>
        </div>
      </div>
      <div style="padding:14px 20px;display:flex;justify-content:space-between;font-size:11px;color:var(--text2)">
        <span>🔴 AO VIVO • Gameplays épicos</span>
        <span>PT • Gaming • Comunidade</span>
      </div>
    </div>
  </div>

  <div class="features">
    {"".join([f'<div class="feat"><div class="feat-ico">{"🎮" if i==0 else "🔥" if i==1 else "👥" if i==2 else "⚡"}</div><b>{f}</b><span>Conteúdo criado com paixão para a comunidade gamer portuguesa.</span></div>' for i,f in enumerate(features)])}
  </div>

  <div class="videos">
    <h2>🎬 Últimos Vídeos</h2>
    <div class="video-grid">
      <div class="video-card"><div class="video-thumb">Gameplay Épico #1</div><div class="video-info"><b>Gameplay mais recente — Deadly Gods</b><span>Há 2 dias • 1.2K views</span></div></div>
      <div class="video-card"><div class="video-thumb">Análise Honesta</div><div class="video-info"><b>Análise sem filtro — Vale a pena?</b><span>Há 5 dias • 890 views</span></div></div>
      <div class="video-card"><div class="video-thumb">Comunidade PT</div><div class="video-info"><b>Melhores momentos da comunidade</b><span>Há 1 semana • 2.1K views</span></div></div>
    </div>
    <div style="text-align:center;margin-top:24px">
      <a href="{youtube_url}/videos" target="_blank" class="btn btn-ghost" style="display:inline-flex">Ver todos os vídeos →</a>
    </div>
  </div>

  <div class="cta-section">
    <h2>🔔 Subscreve no YouTube</h2>
    <p>Não percas nenhum gameplay épico. Subscreve no canal Deadly Gods Portugal e activa o sininho!</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;position:relative">
      <a href="{youtube_url}?sub_confirmation=1" target="_blank" class="btn btn-primary" style="font-size:15px;padding:16px 28px">🔔 Subscrever Agora</a>
      <a href="{youtube_url}" target="_blank" class="btn btn-ghost" style="font-size:15px;padding:16px 28px">▶ Ver Canal</a>
    </div>
  </div>

  <div class="footer">
    <span>© Deadly Gods Portugal — Canal YouTube • Criado via Brain • Leve & Épico • 100% local</span>
    <span>🔗 <a href="{youtube_url}" style="color:var(--accent);text-decoration:none">{youtube_url}</a> • Estilo: {style}</span>
  </div>
  <style>@keyframes pulse{{0%{{box-shadow:0 0 0 0 rgba(255,0,0,0.7)}}70%{{box-shadow:0 0 0 10px rgba(255,0,0,0)}}100%{{box-shadow:0 0 0 0 rgba(255,0,0,0)}}}}</style>
</body>
</html>
"""
    else:
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
      <p>{subtitle} — Criado via chat com Brain. Objectivo: "{objective[:120]}" — Estilo: {style}.</p>
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

        # Builder tem workspace limitado, mas é capaz de fazer deploy se tiver a info
        deploy_info = None
        try:
            from app.tools.deploy import site_deploy, _get_available_platforms
            platforms = _get_available_platforms()
            if platforms:
                # Tenta deploy automático se tem token
                deploy_result = site_deploy(filename=filename, platform="auto", message=f"Deploy {filename} via Builder")
                deploy_info = deploy_result
        except Exception as e:
            deploy_info = {"deployed": False, "error": str(e)}

        result = {
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
        
        if deploy_info:
            result["deploy"] = deploy_info
            if deploy_info.get("deployed"):
                result["message"] += f" — Deploy OK: {deploy_info.get('url')}"
                result["deployed_url"] = deploy_info.get("url")
            else:
                result["deploy_available"] = deploy_info.get("available_platforms", [])
        
        return result
    except Exception as e:
        return {"error": str(e), "built": False, "objective": objective}
