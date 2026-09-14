"""
Rate limit — 10 req/min por IP para /chat, custo 0 sem Redis (in-memory)
Usa slowapi free, sem cartão
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# In-memory limiter — sem Redis, funciona para MVP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit excedido — 10 req/min por IP para /chat",
            "detail": f"Limite: {exc.detail}",
            "retry_after": "60s",
            "message": "Aguarda 1 minuto — quota Groq 14.4k/dia e Gemini 60/min protegida"
        }
    )
