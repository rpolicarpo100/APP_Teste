"""
GOD Cerebro Core — FastAPI Main
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn, os
from pathlib import Path

from app.config.settings import settings, ROOT_DIR
from app.database.connection import init_db
from app.brain.router import init_default_agents, agent_registry
from app.tools.registry import tool_registry
from app.brain.executor import Executor
from app.brain.orchestrator import Orchestrator

import app.tools.filesystem
import app.tools.web
import app.tools.python
import app.tools.scheduler
import app.tools.browser
import app.tools.site_builder
import app.tools.news
import app.tools.market_data

if os.getenv('DISABLE_PROVIDER_HEALTH') != 'true':
    try:
        import app.tools.provider_health
        print("[Main] Provider Health tools OK")
    except Exception as e:
        print(f"[Main] Provider Health tools fail: {e}")
else:
    print("[Main] Provider Health tools desativados")

if os.getenv('DISABLE_TOOLS_HEALTH') != 'true':
    try:
        import app.tools.tools_health
        print("[Main] Tools Health tools OK")
    except Exception as e:
        print(f"[Main] Tools Health tools fail: {e}")
else:
    print("[Main] Tools Health tools desativados")

from app.api import chat, tasks, agents, memory, approvals, system, market, businesses

providers_available = False
if os.getenv('DISABLE_PROVIDER_HEALTH') != 'true':
    try:
        from app.api import providers
        providers_available = True
        print("[Main] Providers API OK")
    except Exception as e:
        print(f"[Main] Providers API fail: {e}")

tools_health_available = False
if os.getenv('DISABLE_TOOLS_HEALTH') != 'true':
    try:
        from app.api import tools_health as tools_health_api
        tools_health_available = True
        print("[Main] Tools Health API OK")
    except Exception as e:
        print(f"[Main] Tools Health API fail: {e}")

init_db()
init_default_agents()

executor = Executor(agent_registry=agent_registry, tool_registry_ref=tool_registry)
orchestrator = Orchestrator(agent_registry=agent_registry, executor=executor)

tasks.set_orchestrator(orchestrator)
agents.set_agent_registry(agent_registry)
chat.set_orchestrator(orchestrator)

app = FastAPI(
    title=settings.app_name,
    description="GOD Cerebro Core — 10 agentes + auto-refresh + KPIs dinâmicos + Provider Health + Tools Health Ranking",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, tags=["system"])
app.include_router(chat.router, prefix="", tags=["chat"])
app.include_router(tasks.router, prefix="", tags=["tasks"])
app.include_router(agents.router, prefix="", tags=["agents"])
app.include_router(memory.router, prefix="", tags=["memory"])
app.include_router(approvals.router, prefix="", tags=["approvals"])
app.include_router(market.router, prefix="", tags=["market"])
app.include_router(businesses.router, prefix="", tags=["negocios"])
if providers_available:
    app.include_router(providers.router, prefix="", tags=["providers"])
if tools_health_available:
    app.include_router(tools_health_api.router, prefix="", tags=["tools-health"])

frontend_path = ROOT_DIR / "frontend"
workspace_path = ROOT_DIR / settings.workspace_path
workspace_path.mkdir(parents=True, exist_ok=True)

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
    frontend_exists = (ROOT_DIR / "frontend" / "index.html").exists()
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "health": "/health",
        "agents": [a.agent_id for a in agent_registry.list_agents()],
        "tools": [t.id for t in tool_registry.list_available()],
        "frontend_exists": frontend_exists,
        "auto_refresh": True,
        "kpis_dynamic": True,
        "provider_health": providers_available,
        "tools_health": tools_health_available,
        "multi_links": True
    }

def main():
    settings.resolve_paths()
    port = getattr(settings, 'effective_port', settings.app_port)
    print(f"Starting {settings.app_name} on {settings.app_host}:{port}")
    print(f"Agents: {[a.agent_id for a in agent_registry.list_agents()]}")
    print(f"Tools: {[t.id for t in tool_registry.list_available()]}")
    if os.getenv('DISABLE_SCHEDULER') != 'true':
        try:
            from app.tools.scheduler import start_all_health_schedulers
            start_all_health_schedulers()
            print("All Health Schedulers iniciados — provider 5min + tools 10min")
        except Exception as e:
            print(f"Scheduler fail: {e}")
            # Fallback tenta só provider
            try:
                from app.tools.scheduler import start_provider_health_scheduler
                start_provider_health_scheduler()
            except:
                pass
    else:
        print("Scheduler desativado")
    uvicorn.run("app.main:app", host=settings.app_host, port=port, reload=False)

if __name__ == "__main__":
    main()
