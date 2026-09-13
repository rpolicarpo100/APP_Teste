"""
API System — GET /health, GET /system/status, GET /logs, GET /system/network
"""
from fastapi import APIRouter
from datetime import datetime
import time
import httpx
from pathlib import Path

router = APIRouter()

@router.get("/health")
def health():
    from app.config.settings import settings
    from app.models.ollama import ollama_client
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "ollama_host": settings.ollama_host,
        "ollama_model": settings.ollama_model,
        "ollama_available": ollama_client.is_available(),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system/status")
def system_status():
    from app.config.settings import settings
    from app.brain.router import agent_registry
    from app.tools.registry import tool_registry
    from app.models.ollama import ollama_client

    agents = agent_registry.list_agents() if agent_registry else []
    tools = tool_registry.list_available() if tool_registry else []

    return {
        "app": settings.app_name,
        "autonomy_level": settings.autonomy_level,
        "max_agent_steps": settings.max_agent_steps,
        "agents": {"count": len(agents), "ids": [a.agent_id for a in agents]},
        "tools": {"count": len(tools), "ids": [t.id for t in tools]},
        "ollama": {"host": settings.ollama_host, "model": settings.ollama_model, "available": ollama_client.is_available(), "models": ollama_client.list_models()[:5]},
        "security": {"allow_file_write": settings.allow_file_write, "allow_python_exec": settings.allow_python_exec},
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system/network")
def system_network():
    """Network do site com KPIs — testa latência de APIs internas e externas + mapa completo com agentes e orquestrador"""
    from app.config.settings import settings, ROOT_DIR
    from app.brain.router import agent_registry
    from app.tools.registry import tool_registry
    import sqlite3

    start = time.time()
    
    # DB stats
    db_path = ROOT_DIR / "data" / "brain.db"
    db_size = db_path.stat().st_size if db_path.exists() else 0
    
    workspace_path = ROOT_DIR / settings.workspace_path
    workspace_files = len(list(workspace_path.glob("*"))) if workspace_path.exists() else 0
    
    # Counts from DB
    counts = {}
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        for tbl in ["missions", "tasks", "memories", "businesses", "conversations", "agents", "tools", "tool_calls"]:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                counts[tbl] = cur.fetchone()[0]
            except:
                counts[tbl] = 0
        conn.close()
    except Exception as e:
        counts = {"error": str(e)}

    # External APIs health — test latency REAL
    external = {}
    tests = [
        ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
        ("Yahoo Finance", "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d"),
        ("Google News RSS", "https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt"),
        ("CoinDesk RSS", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ]
    
    for name, url in tests:
        t0 = time.time()
        try:
            with httpx.Client(timeout=8, headers={"User-Agent": "AI-Brain/1.0"}, follow_redirects=True) as client:
                resp = client.get(url)
                latency = (time.time() - t0) * 1000
                external[name] = {
                    "url": url,
                    "status_code": resp.status_code,
                    "latency_ms": round(latency, 1),
                    "ok": resp.status_code == 200,
                    "size": len(resp.text)
                }
        except Exception as e:
            latency = (time.time() - t0) * 1000
            external[name] = {
                "url": url,
                "error": str(e)[:100],
                "latency_ms": round(latency, 1),
                "ok": False
            }

    # Agents detalhados
    agents_list = agent_registry.list_agents() if agent_registry else []
    agents_detailed = []
    for a in agents_list:
        agents_detailed.append({
            "id": getattr(a, 'agent_id', getattr(a, 'id', 'unknown')),
            "name": getattr(a, 'name', '—'),
            "specialty": getattr(a, 'specialty', '—'),
            "skills": getattr(a, 'skills', [])[:5] if hasattr(a, 'skills') else [],
            "tools": getattr(a, 'tools', [])[:5] if hasattr(a, 'tools') else [],
            "status": getattr(a, 'status', 'READY')
        })

    # Tools detalhados agrupados
    tools_list = tool_registry.list_available() if tool_registry else []
    tools_by_category = {}
    for t in tools_list:
        cat = t.id.split('.')[0] if '.' in t.id else 'other'
        if cat not in tools_by_category:
            tools_by_category[cat] = []
        tools_by_category[cat].append({"id": t.id, "name": t.name, "risk": getattr(t, 'risk_level', 'LOW')})

    # Orquestrador + fluxo
    orchestrator = {
        "type": "GOD Cerebro Core — Orquestrador Universal",
        "flow": [
            "1. User → FastAPI /chat ou /tasks",
            "2. FastAPI → Orchestrator (brain/orchestrator.py)",
            "3. Orchestrator → Mission Intake + Planner",
            "4. Planner → Task Graph Scheduler",
            "5. Scheduler → Agent Registry (8 agentes)",
            "6. Agent → Executor (brain/executor.py)",
            "7. Executor → Tool Registry (21 tools) + Permissions Check",
            "8. Tool → External API ou Filesystem ou Python",
            "9. Result → Validation Audit Core",
            "10. Audit → Project Memory (SQLite) + Response"
        ],
        "components": {
            "mission_intake": "app/brain/orchestrator.py — valida objective",
            "planner": "app/brain/planner.py — cria tasks",
            "agent_registry": "app/brain/router.py — 8 agentes",
            "tool_registry": "app/tools/registry.py — 21 tools",
            "task_graph": "app/brain/scheduler.py — dependências",
            "executor": "app/brain/executor.py — executa com retry",
            "validation": "app/brain/validation.py — verifica resultado",
            "memory": "app/memory/manager.py — SQLite memories"
        }
    }

    total_time = (time.time() - start) * 1000

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "app": settings.app_name,
        "db": {
            "path": str(db_path),
            "size_bytes": db_size,
            "size_mb": round(db_size / 1024 / 1024, 2),
            "counts": counts
        },
        "workspace": {
            "path": str(workspace_path),
            "files_count": workspace_files
        },
        "orchestrator": orchestrator,
        "agents": {
            "count": len(agents_list),
            "detailed": agents_detailed,
            "ids": [a.get('id') for a in agents_detailed]
        },
        "tools": {
            "count": len(tools_list),
            "by_category": tools_by_category,
            "ids": [t.id for t in tools_list]
        },
        "external_apis": external,
        "internal": {
            "total_check_ms": round(total_time, 1),
            "endpoints": {
                "/": "API Root",
                "/health": "Health + Ollama",
                "/system/status": "Sistema geral",
                "/system/network": "Network + KPIs (este)",
                "/chat": "Chat com orquestrador",
                "/tasks": "Missões + Task Graph",
                "/agents": "Lista 8 agentes",
                "/memory": "Project Memory",
                "/businesses": f"{counts.get('businesses',0)} negócios — portfolio",
                "/news/portugal": "Google News RSS PT",
                "/news/world": "Google News WORLD",
                "/news/markets": "Google News BUSINESS",
                "/news/crypto": "CoinDesk + CoinTelegraph RSS",
                "/crypto/gainers-losers": "CoinGecko top 100",
                "/stocks/gainers-losers": "Yahoo Finance 20 símbolos",
                "/dashboard/market-overview": "Agregador notícias + mercados",
                "/workspace/{file}": "Preview sites construídos"
            },
            "routers": ["system", "chat", "tasks", "agents", "memory", "approvals", "market", "businesses"]
        },
        "kpis": {
            "uptime_check_ms": round(total_time, 1),
            "db_size_mb": round(db_size / 1024 / 1024, 2),
            "total_missions": counts.get("missions", 0),
            "total_tasks": counts.get("tasks", 0),
            "total_businesses": counts.get("businesses", 0),
            "total_memories": counts.get("memories", 0),
            "total_agents": len(agents_list),
            "total_tools": len(tools_list),
            "workspace_files": workspace_files,
            "external_ok": sum(1 for v in external.values() if v.get("ok")),
            "external_total": len(external)
        }
    }


@router.get("/system/workspace-list")
def workspace_list():
    from app.config.settings import settings, ROOT_DIR
    import os
    from datetime import datetime
    workspace_path = ROOT_DIR / settings.workspace_path
    files = []
    try:
        if workspace_path.exists():
            for p in sorted(workspace_path.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:100]:
                try:
                    st = p.stat()
                    files.append({
                        "name": p.name,
                        "size": st.st_size,
                        "size_kb": round(st.st_size/1024,1),
                        "modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
                        "is_file": p.is_file(),
                        "url": f"/workspace/{p.name}" if p.is_file() else None
                    })
                except:
                    pass
    except Exception as e:
        return {"error": str(e), "files": []}
    return {"count": len(files), "files": files, "path": str(workspace_path)}

@router.get("/system/export-all")
def export_all():
    from app.config.settings import ROOT_DIR
    import sqlite3
    db_path = ROOT_DIR / "data" / "brain.db"
    data = {}
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        for tbl in ["missions","tasks","memories","businesses","conversations","agents","tools"]:
            try:
                cur.execute(f"SELECT * FROM {tbl} LIMIT 200")
                rows = [dict(r) for r in cur.fetchall()]
                data[tbl] = rows
            except Exception as e:
                data[tbl] = {"error": str(e)}
        conn.close()
    except Exception as e:
        return {"error": str(e)}
    return data


@router.get("/logs")
def get_logs(limit: int = 50):
    from app.security.audit import audit_manager
    logs = audit_manager.get_all()
    # Últimos N
    recent = logs[-limit:]
    return {"logs": [l.model_dump() for l in recent], "count": len(recent), "total": len(logs)}
