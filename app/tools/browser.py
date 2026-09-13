"""
Browser tool — Playwright wrapper (CAPACIDADE NÃO DISPONÍVEL se playwright não instalado)
Local AI Brain §10 Browser Agent
Para MVP, implementação simulada com verificação de disponibilidade.
"""
from app.tools.registry import register_tool
import shutil

def _is_playwright_available():
    return shutil.which("playwright") is not None or _try_import_playwright()

def _try_import_playwright():
    try:
        import playwright
        return True
    except ImportError:
        return False

@register_tool(
    id="browser.open",
    name="Browser Open",
    description="Abre página no browser (Playwright)",
    risk_level="MEDIUM",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    output_schema={"type": "object", "properties": {"content": {"type": "string"}}}
)
def browser_open(url: str) -> dict:
    if not _is_playwright_available():
        return {
            "error": "Playwright não disponível neste ambiente",
            "url": url,
            "status": "CAPACIDADE NÃO DISPONÍVEL",
            "suggestion": "Instalar com: pip install playwright && playwright install chromium"
        }
    # Para MVP, usa web.fetch como fallback real
    try:
        from app.tools.web import web_fetch
        result = web_fetch(url)
        return {"url": url, "content": result.get("content", "")[:10000], "via": "web.fetch fallback", "playwright_available": True}
    except Exception as e:
        return {"error": str(e), "url": url}

@register_tool(
    id="browser.screenshot",
    name="Browser Screenshot",
    description="Captura screenshot (requer Playwright)",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
    output_schema={"type": "object", "properties": {}}
)
def browser_screenshot(url: str) -> dict:
    return {
        "error": "Screenshot não implementado no MVP sandbox",
        "url": url,
        "status": "PROPOSTA — NÃO IMPLEMENTADA",
        "note": "Requer ambiente com display e playwright chromium"
    }
