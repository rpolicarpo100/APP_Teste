"""
API Tools Health — audit, health, ranking, failover para tools
Similar ao Provider Health mas para tools internas
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import sqlite3
from pathlib import Path
from datetime import datetime

router = APIRouter()

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/tools/health")
def tools_health():
    """Audita todas as tools, verifica saúde e retorna ranking"""
    try:
        from app.agents.tools_health import ToolsHealthAgent
        from app.agents.base import TaskInput
        import uuid
        
        agent = ToolsHealthAgent()
        task = TaskInput(
            task_id=str(uuid.uuid4()),
            mission_id=str(uuid.uuid4()),
            agent_id="tools_health",
            objective="verificar saúde de todas as tools"
        )
        output = agent.execute(task)
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tool_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='ok' THEN 1 ELSE 0 END) as ok, SUM(CASE WHEN status='fail' THEN 1 ELSE 0 END) as fail FROM tool_rankings")
        row = cur.fetchone()
        stats = dict(row) if row else {"total": 0, "ok": 0, "fail": 0}
        conn.close()
        
        return {
            "status": "ok",
            "summary": output.summary,
            "stats": stats,
            "health": [a["data"] for a in output.artifacts if a["type"] == "tool_health"][0] if output.artifacts else [],
            "rankings": rankings,
            "suggestions": output.next_recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@router.get("/tools/ranking")
def tools_ranking(category: Optional[str] = None):
    """Ranking tools por experiência e uso"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        if category:
            cur.execute("SELECT * FROM tool_rankings WHERE category=? ORDER BY score DESC", (category,))
        else:
            cur.execute("SELECT * FROM tool_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT category FROM tool_rankings GROUP BY category")
        categories = [r["category"] for r in cur.fetchall()]
        
        best_by_cat = {}
        for cat in categories:
            cur.execute("SELECT * FROM tool_rankings WHERE category=? ORDER BY score DESC LIMIT 1", (cat,))
            best = cur.fetchone()
            if best:
                best_by_cat[cat] = dict(best)
        
        cur.execute("SELECT * FROM tool_health_history ORDER BY check_time DESC LIMIT 20")
        history = [dict(r) for r in cur.fetchall()]
        
        cur.execute("SELECT * FROM tool_calls_log ORDER BY created_at DESC LIMIT 20")
        calls = [dict(r) for r in cur.fetchall()]
        
        conn.close()
        
        return {
            "rankings": rankings,
            "best_by_category": best_by_cat,
            "history": history,
            "recent_calls": calls,
            "categories": categories,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/tools/audit")
def tools_audit():
    """Audita tools por categoria"""
    try:
        from app.agents.tools_health import ToolsHealthAgent
        from app.agents.base import TaskInput
        import uuid
        
        agent = ToolsHealthAgent()
        task = TaskInput(
            task_id=str(uuid.uuid4()),
            mission_id=str(uuid.uuid4()),
            agent_id="tools_health",
            objective="auditar lista de tools por categoria"
        )
        output = agent.execute(task)
        
        return {
            "summary": output.summary,
            "by_category": [a["data"] for a in output.artifacts if a["type"] == "tools_by_category"][0] if output.artifacts else {},
            "all_tools": [a["data"] for a in output.artifacts if a["type"] == "all_tools"][0] if len(output.artifacts) > 1 else [],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/tools/health/{tool_id}")
def tool_health_detail(tool_id: str):
    """Detalhe de uma tool específica"""
    try:
        from app.tools.registry import tool_registry
        from app.agents.tools_health import TOOL_ALTERNATIVES
        
        tool_def = tool_registry.get(tool_id)
        if not tool_def:
            return {"error": f"Tool {tool_id} não encontrada", "available": [t.id for t in tool_registry.list_all()]}
        
        from app.agents.tools_health import ToolsHealthAgent
        agent = ToolsHealthAgent()
        check = agent._check_tool(tool_def)
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tool_rankings WHERE tool_id=?", (tool_id,))
        ranking = cur.fetchone()
        cur.execute("SELECT * FROM tool_health_history WHERE tool_id=? ORDER BY check_time DESC LIMIT 10", (tool_id,))
        history = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT * FROM tool_calls_log WHERE tool_id=? ORDER BY created_at DESC LIMIT 10", (tool_id,))
        calls = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        return {
            "tool_id": tool_id,
            "definition": {
                "id": tool_def.id,
                "name": tool_def.name,
                "description": tool_def.description,
                "risk": getattr(tool_def, 'risk_level', 'LOW'),
                "implementation": getattr(tool_def, 'implementation', None)
            },
            "current_check": check,
            "ranking": dict(ranking) if ranking else None,
            "history": history,
            "recent_calls": calls,
            "alternatives": TOOL_ALTERNATIVES.get(tool_id, [])
        }
    except Exception as e:
        return {"error": str(e)}

class FailoverRequest(BaseModel):
    alternative: Optional[str] = None

@router.post("/tools/failover/{tool_id}")
def tool_failover(tool_id: str, data: FailoverRequest = None):
    """Força failover de tool para alternativa melhor rankeada"""
    try:
        from app.tools.tools_health import tools_failover_tool
        alt = data.alternative if data else None
        result = tools_failover_tool(tool_id, alt)
        return result
    except Exception as e:
        return {"error": str(e)}

@router.get("/tools/alternatives/{tool_id}")
def tool_alternatives(tool_id: str):
    """Lista alternativas para uma tool"""
    try:
        from app.agents.tools_health import TOOL_ALTERNATIVES
        from app.tools.registry import tool_registry
        
        if tool_id not in TOOL_ALTERNATIVES:
            return {"tool_id": tool_id, "alternatives": [], "message": "Sem alternativas configuradas"}
        
        alts = TOOL_ALTERNATIVES[tool_id]
        
        conn = get_conn()
        cur = conn.cursor()
        if alts:
            placeholders = ",".join(["?"] * len(alts))
            cur.execute(f"SELECT tool_id, name, status, score, rank, usage_count FROM tool_rankings WHERE tool_id IN ({placeholders}) ORDER BY score DESC", alts)
            alt_details = [dict(r) for r in cur.fetchall()]
        else:
            alt_details = []
        
        # Se não tem ranking ainda, lista do registry
        if not alt_details:
            alt_details = []
            for alt_id in alts:
                t = tool_registry.get(alt_id)
                if t:
                    alt_details.append({"tool_id": t.id, "name": t.name, "status": t.status.value, "score": 0.5, "rank": 999})
        
        conn.close()
        
        return {
            "tool_id": tool_id,
            "alternatives": alts,
            "alternative_details": alt_details
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/tools/usage")
def tools_usage():
    """Retorna uso recente de tools"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT tool_id, COUNT(*) as count, AVG(latency_ms) as avg_lat, SUM(CASE WHEN status='ok' THEN 1 ELSE 0 END) as ok_count FROM tool_calls_log GROUP BY tool_id ORDER BY count DESC")
        usage = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT * FROM tool_calls_log ORDER BY created_at DESC LIMIT 30")
        recent = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"usage_by_tool": usage, "recent_calls": recent}
    except Exception as e:
        return {"error": str(e)}
