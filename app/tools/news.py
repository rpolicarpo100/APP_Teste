"""
News tools — Notícias do dia Portugal | Mundo | Mercados | Crypto
Ferramentas REAIS e FIÁVEIS, testadas e validadas

Fontes identificadas:
- Portugal: Google News RSS PT (https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt) — gratuito, sem API key, fiável
- Mundo: Google News RSS World + BBC RSS
- Mercados: Yahoo Finance + Google News Business
- Crypto: CoinDesk RSS + CoinTelegraph RSS + CoinGecko status

Todas usam httpx + xml.etree (built-in) — sem dependências pesadas
"""
from app.tools.registry import register_tool
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
import re

def _parse_rss(xml_text: str, max_items: int = 8) -> list:
    """Parser RSS simples e robusto — sem feedparser externo"""
    articles = []
    try:
        root = ET.fromstring(xml_text)
        # Tenta encontrar items — RSS 2.0: channel/item, Atom: entry
        # RSS 2.0
        for item in root.findall('.//item')[:max_items]:
            title_el = item.find('title')
            link_el = item.find('link')
            pub_el = item.find('pubDate')
            desc_el = item.find('description')
            source_el = item.find('source')
            
            title = title_el.text if title_el is not None else "Sem título"
            link = link_el.text if link_el is not None else ""
            pub = pub_el.text if pub_el is not None else ""
            desc = desc_el.text if desc_el is not None else ""
            source = source_el.text if source_el is not None else ""
            
            # Limpa HTML de description
            desc = re.sub(r'<[^>]+>', '', desc)[:200]
            
            articles.append({
                "title": title.strip()[:200],
                "link": link.strip(),
                "pubDate": pub.strip(),
                "description": desc.strip(),
                "source": source.strip() if source else "RSS"
            })
        
        # Se não encontrou via item, tenta Atom entry
        if not articles:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('.//atom:entry', ns)[:max_items]:
                title_el = entry.find('atom:title', ns)
                link_el = entry.find('atom:link', ns)
                pub_el = entry.find('atom:updated', ns) or entry.find('atom:published', ns)
                summary_el = entry.find('atom:summary', ns)
                
                title = title_el.text if title_el is not None else "Sem título"
                link = link_el.get('href') if link_el is not None else ""
                pub = pub_el.text if pub_el is not None else ""
                desc = summary_el.text if summary_el is not None else ""
                
                articles.append({
                    "title": title.strip()[:200],
                    "link": link.strip(),
                    "pubDate": pub.strip(),
                    "description": re.sub(r'<[^>]+>', '', desc)[:200].strip(),
                    "source": "Atom"
                })
    except ET.ParseError as e:
        return [{"error": f"RSS parse error: {str(e)}", "title": "Erro parsing", "link": "", "pubDate": "", "description": ""}]
    except Exception as e:
        return [{"error": str(e), "title": "Erro", "link": "", "pubDate": "", "description": ""}]
    
    return articles

def _fetch_rss(url: str, max_items: int = 8) -> dict:
    """Fetch RSS com httpx — timeout curto, User-Agent real"""
    try:
        with httpx.Client(timeout=10, follow_redirects=True, headers={"User-Agent": "AI-Brain/1.0 (+https://local)"}) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}", "url": url, "articles": [], "count": 0}
            
            articles = _parse_rss(resp.text, max_items=max_items)
            return {
                "url": url,
                "articles": articles,
                "count": len(articles),
                "fetched_at": datetime.utcnow().isoformat(),
                "status": "success" if articles else "empty"
            }
    except Exception as e:
        return {"error": str(e), "url": url, "articles": [], "count": 0, "status": "failed"}

@register_tool(
    id="news.portugal",
    name="Notícias Portugal",
    description="Notícias do dia Portugal — Google News RSS PT + Observador RSS — gratuito e fiável",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"count": {"type": "integer"}}},
    output_schema={"type": "object", "properties": {"articles": {"type": "array"}}}
)
def news_portugal(count: int = 8) -> dict:
    """
    Ferramenta REAL e FIÁVEL — Google News RSS Portugal
    Testado: https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt
    Sem API key, sem custo, actualizado em tempo real
    """
    # Tenta múltiplas fontes para fiabilidade
    sources = [
        "https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt",
        "https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt&topic=business",
        "https://observador.pt/feed/"
    ]
    
    for url in sources:
        result = _fetch_rss(url, max_items=count)
        if result.get("count", 0) > 0:
            result["source_name"] = "Google News Portugal" if "google" in url else "Observador"
            result["category"] = "Portugal"
            return result
    
    return {"error": "Todas as fontes Portugal falharam", "articles": [], "count": 0, "category": "Portugal", "status": "failed"}

@register_tool(
    id="news.world",
    name="Notícias Mundo",
    description="Notícias do dia Mundo — Google News World + BBC — gratuito e fiável",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"count": {"type": "integer"}}},
    output_schema={"type": "object", "properties": {"articles": {"type": "array"}}}
)
def news_world(count: int = 8) -> dict:
    """
    REAL e FIÁVEL — Google News World + BBC RSS
    Testado: /rss/headlines/section/topic/WORLD?hl=pt-PT&gl=PT&ceid=PT:pt retorna Mundo real
    """
    sources = [
        "https://news.google.com/rss/headlines/section/topic/WORLD?hl=pt-PT&gl=PT&ceid=PT:pt",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    ]
    
    for url in sources:
        result = _fetch_rss(url, max_items=count)
        if result.get("count", 0) > 0:
            if "bbc" in url:
                result["source_name"] = "BBC World"
            elif "WORLD" in url:
                result["source_name"] = "Google News Mundo"
            else:
                result["source_name"] = "Google News World EN"
            result["category"] = "Mundo"
            return result
    
    return {"error": "Todas as fontes Mundo falharam", "articles": [], "count": 0, "category": "Mundo", "status": "failed"}

@register_tool(
    id="news.markets",
    name="Notícias Mercados",
    description="Notícias Mercados — Yahoo Finance + Google News Business — gratuito e fiável",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"count": {"type": "integer"}}},
    output_schema={"type": "object", "properties": {"articles": {"type": "array"}}}
)
def news_markets(count: int = 8) -> dict:
    """
    REAL e FIÁVEL — Mercados financeiros
    Testado: BUSINESS topic PT + Yahoo Finance RSS funcionam
    """
    sources = [
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=pt-PT&gl=PT&ceid=PT:pt",
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC,%5EIXIC&region=US&lang=en-US",
        "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en&topic=b"
    ]
    
    for url in sources:
        result = _fetch_rss(url, max_items=count)
        if result.get("count", 0) > 0:
            if "yahoo" in url:
                result["source_name"] = "Yahoo Finance"
            elif "BUSINESS" in url:
                result["source_name"] = "Google News Negócios"
            else:
                result["source_name"] = "Google News Mercados EN"
            result["category"] = "Mercados"
            return result
    
    return {"error": "Todas as fontes Mercados falharam", "articles": [], "count": 0, "category": "Mercados", "status": "failed"}

@register_tool(
    id="news.crypto",
    name="Notícias Crypto",
    description="Notícias Crypto — CoinDesk + CoinTelegraph RSS — gratuito e fiável",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"count": {"type": "integer"}}},
    output_schema={"type": "object", "properties": {"articles": {"type": "array"}}}
)
def news_crypto(count: int = 8) -> dict:
    """
    REAL e FIÁVEL — Crypto news
    """
    sources = [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt&q=crypto+OR+bitcoin+OR+ethereum&ceid=PT:pt"
    ]
    
    for url in sources:
        result = _fetch_rss(url, max_items=count)
        if result.get("count", 0) > 0:
            result["source_name"] = "CoinDesk" if "coindesk" in url else "CoinTelegraph" if "cointelegraph" in url else "Google News Crypto"
            result["category"] = "Crypto"
            return result
    
    return {"error": "Todas as fontes Crypto falharam", "articles": [], "count": 0, "category": "Crypto", "status": "failed"}

@register_tool(
    id="news.all",
    name="Todas Notícias",
    description="Agrega notícias Portugal + Mundo + Mercados + Crypto",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"count_per_category": {"type": "integer"}}},
    output_schema={"type": "object", "properties": {"portugal": {"type": "object"}, "world": {"type": "object"}}}
)
def news_all(count_per_category: int = 5) -> dict:
    """
    Agregador REAL — chama 4 ferramentas reais
    """
    return {
        "portugal": news_portugal(count=count_per_category),
        "world": news_world(count=count_per_category),
        "markets": news_markets(count=count_per_category),
        "crypto": news_crypto(count=count_per_category),
        "fetched_at": datetime.utcnow().isoformat(),
        "total_count": 0  # calculado no frontend
    }
