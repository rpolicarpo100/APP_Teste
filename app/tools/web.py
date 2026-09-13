"""
Web tools — pesquisa e fetch
Conforme GOD §10 e Local AI Brain
Implementação real usando httpx, com fallback se não disponível.
"""
from typing import Dict, Any, List
import httpx
from app.tools.registry import register_tool

@register_tool(
    id="web.search",
    name="Web Search",
    description="Pesquisa web (simulada via DuckDuckGo / SearXNG quando disponível, fallback local)",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"query": {"type": "string"}, "count": {"type": "integer"}}, "required": ["query"]},
    output_schema={"type": "object", "properties": {"results": {"type": "array"}}}
)
def web_search(query: str, count: int = 5) -> dict:
    """
    Implementação verificável — tenta usar DuckDuckGo html, senão retorna estrutura para agente preencher.
    Não inventa resultados: se não conseguir pesquisar, declara limitação.
    """
    try:
        # Tenta DuckDuckGo lite — sem API key, local e free
        url = "https://lite.duckduckgo.com/lite/"
        # DuckDuckGo lite requer POST
        # Para MVP, fazemos GET simples e parsing básico, com timeout curto
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            # Primeiro, tenta html.duckduckgo.com
            resp = client.get("https://html.duckduckgo.com/html/", params={"q": query})
            if resp.status_code == 200:
                text = resp.text[:5000]
                # Extrai links de forma simples — não inventa, apenas extrai o que existe
                import re
                links = re.findall(r'href=\"(https?://[^\"]+)\"', text)
                # Filtra
                results = []
                seen = set()
                for link in links:
                    if "duckduckgo" in link:
                        continue
                    if link in seen:
                        continue
                    seen.add(link)
                    results.append({"url": link, "title": link[:80], "snippet": f"Resultado para {query}"})
                    if len(results) >= count:
                        break
                if results:
                    return {"query": query, "results": results, "source": "duckduckgo", "count": len(results)}
    except Exception as e:
        # Não falha, declara limitação
        pass

    # Fallback — não inventa resultados, declara que pesquisa externa não disponível no momento
    return {
        "query": query,
        "results": [],
        "source": "none",
        "count": 0,
        "limitation": "Pesquisa web externa não disponível neste ambiente sandbox ou bloqueada. Recomenda-se configurar SearXNG local ou usar web.fetch com URLs específicos.",
        "suggestion": "Use web.fetch com URLs conhecidos ou forneça documentos locais."
    }

@register_tool(
    id="web.fetch",
    name="Web Fetch",
    description="Faz fetch de uma página web e retorna markdown/text",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    output_schema={"type": "object", "properties": {"content": {"type": "string"}, "url": {"type": "string"}}}
)
def web_fetch(url: str) -> dict:
    try:
        with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": "AI-Brain/1.0"}) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}", "url": url, "content": None}
            content = resp.text[:20000]  # limita
            # Sanitiza
            from app.security.policies import sanitize_external_content
            content = sanitize_external_content(content)
            return {"url": url, "content": content, "status_code": resp.status_code, "length": len(content)}
    except Exception as e:
        return {"error": str(e), "url": url, "content": None}
