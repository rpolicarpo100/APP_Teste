"""
GOD Cerebro Core / Local AI Brain — FastAPI Main
Ponto de entrada: python -m app.main
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

from app.config.settings import settings, ROOT_DIR
from app.database.connection import init_db
from app.brain.router import init_default_agents, agent_registry
from app.tools.registry import tool_registry
from app.brain.executor import Executor
from app.brain.orchestrator import Orchestrator

# Import tools para registar — importante: importar antes de iniciar
import app.tools.filesystem  # noqa
import app.tools.web  # noqa
import app.tools.python  # noqa
import app.tools.scheduler  # noqa
import app.tools.browser  # noqa
import app.tools.site_builder  # noqa — construtor de apps/sites via chat
import app.tools.news  # noqa — notícias Portugal | Mundo | Mercados | Crypto — REAL
import app.tools.market_data  # noqa — ganhadores/perdedores Crypto e Ações — REAL
import app.tools.provider_health  # noqa — verifica providers, failover e ranking por experiência

# Import APIs
from app.api import chat, tasks, agents, memory, approvals, system, market, businesses, providers

# Inicializa DB
init_db()

# Inicializa agentes
init_default_agents()

# Inicializa executor e orchestrator
executor = Executor(agent_registry=agent_registry, tool_registry_ref=tool_registry)
orchestrator = Orchestrator(agent_registry=agent_registry, executor=executor)

# Inject dependencies nas rotas
tasks.set_orchestrator(orchestrator)
agents.set_agent_registry(agent_registry)
chat.set_orchestrator(orchestrator)

app = FastAPI(
    title=settings.app_name,
    description="GOD Cerebro Core — Orquestrador Universal de Agentes + Local AI Brain v1.0 + Provider Health Ranking",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(system.router, tags=["system"])
app.include_router(chat.router, prefix="", tags=["chat"])
app.include_router(tasks.router, prefix="", tags=["tasks"])
app.include_router(agents.router, prefix="", tags=["agents"])
app.include_router(memory.router, prefix="", tags=["memory"])
app.include_router(approvals.router, prefix="", tags=["approvals"])
app.include_router(market.router, prefix="", tags=["market — notícias e ganhadores/perdedores REAL"]) 
app.include_router(businesses.router, prefix="", tags=["negócios — portfolio dos nossos negócios"])
app.include_router(providers.router, prefix="", tags=["providers — health check, ranking e failover automático"])

# Frontend static + workspace static — para preview de sites construídos via chat
frontend_path = ROOT_DIR / "frontend"
workspace_path = ROOT_DIR / settings.workspace_path
workspace_path.mkdir(parents=True, exist_ok=True)

# Monta workspace para preview de apps/sites construídos — /workspace/{ficheiro}.html
try:
    app.mount("/workspace", StaticFiles(directory=str(workspace_path), html=True), name="workspace")
except Exception:
    pass

if frontend_path.exists():
    index_file = frontend_path / "index.html"
    if index_file.exists():
        try:
            app.mount("/dashboard", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
        except Exception:
            pass
        @app.get("/dashboard", include_in_schema=False)
        @app.get("/dashboard/", include_in_schema=False)
        def serve_dashboard():
            return FileResponse(str(index_file))

@app.get("/")
def root():
    # Se frontend existe, serve dashboard por defeito? Não, mantém JSON para API, mas adiciona link
    frontend_exists = (ROOT_DIR / "frontend" / "index.html").exists()
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "dashboard_direct": "/dashboard/",
        "health": "/health",
        "architecture": "GOD Cerebro Core + Local AI Brain v1.0 + Provider Health Ranking",
        "agents": [a.agent_id for a in agent_registry.list_agents()],
        "tools": [t.id for t in tool_registry.list_available()],
        "frontend_exists": frontend_exists,
        "message": "Abre /dashboard para app leve e bonita com DASHBOARD | CHAT | NEGOCIOS | DEFINIÇÕES + auto-refresh + provider health ranking"
    }

def main():
    settings.resolve_paths()
    port = getattr(settings, 'effective_port', settings.app_port)
    print(f"Starting {settings.app_name} on {settings.app_host}:{port}")
    print(f"Ollama: {settings.ollama_host} model={settings.ollama_model}")
    print(f"Agents: {[a.agent_id for a in agent_registry.list_agents()]}")
    print(f"Tools: {[t.id for t in tool_registry.list_available()]}")
    # Inicia scheduler para provider health checks periódicos — opcional, desativa no Render free se falhar
    import os
    if os.getenv('DISABLE_SCHEDULER') != 'true':
        try:
            from app.tools.scheduler import start_provider_health_scheduler
            start_provider_health_scheduler()
            print("Provider Health Scheduler iniciado — verifica providers a cada 5 min")
        except Exception as e:
            print(f"Scheduler não iniciado: {e}")
    else:
        print("Scheduler desativado via DISABLE_SCHEDULER=true")
    uvicorn.run("app.main:app", host=settings.app_host, port=port, reload=False)

if __name__ == "__main__":
    main()
