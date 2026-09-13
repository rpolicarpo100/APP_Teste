"""
API Market — Notícias e Mercados para Dashboard
Endpoints REAIS usando ferramentas testadas e validadas
"""
from fastapi import APIRouter
from typing import Optional

router = APIRouter()

@router.get("/news/portugal")
def get_news_portugal(count: int = 8):
    from app.tools.news import news_portugal
    return news_portugal(count=count)

@router.get("/news/world")
def get_news_world(count: int = 8):
    from app.tools.news import news_world
    return news_world(count=count)

@router.get("/news/markets")
def get_news_markets(count: int = 8):
    from app.tools.news import news_markets
    return news_markets(count=count)

@router.get("/news/crypto")
def get_news_crypto(count: int = 8):
    from app.tools.news import news_crypto
    return news_crypto(count=count)

@router.get("/news/all")
def get_news_all(count_per_category: int = 5):
    from app.tools.news import news_all
    return news_all(count_per_category=count_per_category)

@router.get("/crypto/markets")
def get_crypto_markets(vs_currency: str = "eur", count: int = 50):
    from app.tools.market_data import crypto_markets
    return crypto_markets(vs_currency=vs_currency, count=count)

@router.get("/crypto/gainers-losers")
def get_crypto_gainers_losers(vs_currency: str = "eur", count: int = 5):
    from app.tools.market_data import crypto_gainers_losers
    return crypto_gainers_losers(vs_currency=vs_currency, count=count)

@router.get("/stocks/markets")
def get_stocks_markets(vs_currency: str = "eur"):
    from app.tools.market_data import stocks_markets
    return stocks_markets(vs_currency=vs_currency)

@router.get("/stocks/gainers-losers")
def get_stocks_gainers_losers(count: int = 5):
    from app.tools.market_data import stocks_gainers_losers
    return stocks_gainers_losers(count=count)

@router.get("/dashboard/market-overview")
def get_dashboard_market_overview(news_count: int = 4, crypto_count: int = 5, stocks_count: int = 5):
    from app.tools.market_data import dashboard_market_overview
    return dashboard_market_overview(news_count=news_count, crypto_count=crypto_count, stocks_count=stocks_count)
