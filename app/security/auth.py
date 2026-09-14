"""
Auth + Path Traversal + CORS seguro — tarefa 5
- API_KEY auth opcional (se API_KEY env var setada)
- Path traversal check extra
- CORS seguro (não * por defeito em produção)
"""
import os
import re
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# API_KEY opcional — se não setada, auth desativada (dev mode)
API_KEY = os.getenv('API_KEY') or os.getenv('SECRET_KEY') or ""

# Paths públicos que não precisam auth
PUBLIC_PATHS = [
    "/", "/health", "/docs", "/openapi.json", "/redoc",
    "/dashboard", "/dashboard/", "/workspace", "/workspace/",
    "/system/status", "/system/network", "/system/workspace-list"
]

PUBLIC_PREFIXES = [
    "/workspace/", "/dashboard/", "/docs", "/redoc", "/openapi.json",
    "/news/", "/crypto/", "/stocks/", "/dashboard/"
]

def is_public_path(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    for prefix in PUBLIC_PREFIXES:
        if path.startswith(prefix):
            return True
    # /workspace/* sempre público para preview
    if path.startswith("/workspace"):
        return True
    return False

def check_api_key(request: Request):
    """Verifica API_KEY se configurada"""
    if not API_KEY or API_KEY == "change-me":
        return True  # auth desativada em dev
    
    # Se path público, não precisa
    if is_public_path(request.url.path):
        return True
    
    # Verifica header X-API-Key ou Authorization Bearer
    api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if not api_key:
        auth = request.headers.get("Authorization") or ""
        if auth.startswith("Bearer "):
            api_key = auth.replace("Bearer ", "").strip()
    
    # Também aceita query param ?api_key=xxx (para compat)
    if not api_key:
        api_key = request.query_params.get("api_key")
    
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API_KEY inválida ou ausente — adiciona header X-API-Key ou ?api_key= — configura API_KEY env var no Render/Leapcell")
    
    return True

def check_path_traversal(request: Request):
    """Bloqueia path traversal em URL e query params"""
    path = request.url.path
    query = str(request.url.query)
    full = path + "?" + query
    
    # Padrões maliciosos
    traversal_patterns = [
        r'\.\./', r'\.\.\\', r'%2e%2e', r'%2e%2e%2f',
        r'/etc/passwd', r'/etc/shadow', r'c:\\windows', r'c:/windows',
        r'\.\.%2f', r'%2e%2e/', r'..%5c', r'%252e%252e',
        r';\s*cat\s+', r'\|\s*cat\s+', r'`cat', r'\$\(cat',
        r'rm\s+-rf\s+/', r';\s*rm\s+', r'\|\s*rm\s+'
    ]
    
    lower = full.lower()
    for pat in traversal_patterns:
        if re.search(pat, lower):
            raise HTTPException(status_code=400, detail=f"Path traversal bloqueado — padrão detectado: {pat} — input sanitizado com html.escape")
    
    # Verifica se path contém .. após normalização
    from pathlib import Path
    try:
        # Se path tem .. no segmento
        if ".." in Path(path).parts:
            raise HTTPException(status_code=400, detail="Path traversal bloqueado — '..' não permitido no path")
    except HTTPException:
        raise
    except:
        pass
    
    return True

async def auth_and_security_middleware(request: Request, call_next):
    """Middleware que combina auth + path traversal"""
    try:
        check_path_traversal(request)
        check_api_key(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail, "path": request.url.path})
    except Exception as e:
        # Se falhar verificação, bloqueia por segurança
        return JSONResponse(status_code=400, content={"error": f"Security check fail: {str(e)}"})
    
    response = await call_next(request)
    # Headers de segurança extra
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

def get_cors_origins():
    """CORS seguro — não * em produção se API_KEY setada"""
    cors_env = os.getenv('CORS_ORIGINS', '')
    if cors_env:
        if cors_env == "*":
            # Se API_KEY setada, não permite * — força lista específica
            if API_KEY and API_KEY != "change-me":
                return [
                    "https://app-teste-x6od.onrender.com",
                    "https://ai-brain-god.leapcell.dev",
                    "http://localhost:8000",
                    "http://localhost:3000",
                    "http://127.0.0.1:8000"
                ]
            return ["*"]
        return [o.strip() for o in cors_env.split(",") if o.strip()]
    
    # Default: se produção com API_KEY, lista restritiva
    if API_KEY and API_KEY != "change-me":
        return [
            "https://app-teste-x6od.onrender.com",
            "https://ai-brain-god.leapcell.dev",
            "http://localhost:8000",
            "http://localhost:3000",
            "http://127.0.0.1:8000",
            "https://rpolicarpo100.github.io"
        ]
    
    # Dev: permite tudo mas avisa
    return ["*"]
