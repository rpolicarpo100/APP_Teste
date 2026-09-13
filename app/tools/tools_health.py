"""
Tools para Tools Health — audit, check, ranking, failover
"""
from app.tools.registry import register_tool
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"

def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@register_tool(
    id="tool.health_check",
    name="Verificar saúde tools",
    description="Audita todas as tools, verifica se implementação existe, lista e analisa uso",
    risk_level="LOW"
)
def tools_health_check_tool(tool_id: str = None) -> dict:
    """Verifica saúde de uma ou todas as tools"""
    try:
        from app.agents.tools_health import ToolsHealthAgent
        from app.agents.base import TaskInput
        import uuid
        
        agent = ToolsHealthAgent()
        
        if tool_id:
            from app.tools.registry import tool_registry
            tool_def = tool_registry.get(tool_id)
            if not tool_def:
                return {"error": f"Tool {tool_id} não encontrada", "available": [t.id for t in tool_registry.list_all()]}
            result = agent._check_tool(tool_def)
            agent._update_ranking(result)
            return {"tool": result, "status": "checked"}
        else:
            task = TaskInput(
                task_id=str(uuid.uuid4()),
                mission_id=str(uuid.uuid4()),
                agent_id="tools_health",
                objective="verificar saúde de todas as tools"
            )
            output = agent.execute(task)
            return {
                "summary": output.summary,
                "health": [a["data"] for a in output.artifacts if a["type"] == "tool_health"][0] if output.artifacts else [],
                "ranking": [a["data"] for a in output.artifacts if a["type"] == "tool_ranking"][0] if len(output.artifacts) > 1 else [],
                "suggestions": output.next_recommendations
            }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@register_tool(
    id="tool.audit",
    name="Auditar tools",
    description="Lista todas as tools por categoria, com status e implementação",
    risk_level="LOW"
)
def tools_audit_tool() -> dict:
    """Audita tools"""
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
            "all_tools": [a["data"] for a in output.artifacts if a["type"] == "all_tools"][0] if len(output.artifacts) > 1 else []
        }
    except Exception as e:
        return {"error": str(e)}

@register_tool(
    id="tool.ranking",
    name="Ranking tools por experiência",
    description="Retorna ranking de tools baseado em experiência, uso e sucesso",
    risk_level="LOW"
)
def tools_ranking_tool(category: str = None) -> dict:
    """Ranking tools"""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        if category:
            cur.execute("SELECT * FROM tool_rankings WHERE category=? ORDER BY score DESC, rank ASC", (category,))
        else:
            cur.execute("SELECT * FROM tool_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        
        by_cat = {}
        for r in rankings:
            cat = r["category"]
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(r)
        
        best_by_category = {}
        for cat, tools in by_cat.items():
            if tools:
                best = max(tools, key=lambda x: x["score"] or 0)
                best_by_category[cat] = {
                    "tool_id": best["tool_id"],
                    "name": best["name"],
                    "score": best["score"],
                    "experience": best["experience_points"],
                    "usage": best["usage_count"],
                    "status": best["status"]
                }
        
        conn.close()
        
        return {
            "rankings": rankings,
            "by_category": by_cat,
            "best_by_category": best_by_category,
            "total": len(rankings)
        }
    except Exception as e:
        return {"error": str(e)}

@register_tool(
    id="tool.failover",
    name="Failover tool para melhor alternativa",
    description="Troca tool com falhas por alternativa melhor rankeada",
    risk_level="MEDIUM"
)
def tools_failover_tool(tool_id: str, force_alternative: str = None) -> dict:
    """Failover tool"""
    try:
        from app.agents.tools_health import TOOL_ALTERNATIVES
        conn = _get_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM tool_rankings WHERE tool_id=?", (tool_id,))
        row = cur.fetchone()
        if not row:
            return {"error": f"Tool {tool_id} não encontrada no ranking — faz health check primeiro"}
        
        alternatives = TOOL_ALTERNATIVES.get(tool_id, [])
        
        if force_alternative:
            if force_alternative not in alternatives:
                return {"error": f"Alternativa {force_alternative} não válida", "available": alternatives}
            alternative = force_alternative
        else:
            if not alternatives:
                return {"error": "Sem alternativas configuradas"}
            placeholders = ",".join(["?"] * len(alternatives))
            cur.execute(f"SELECT tool_id, score FROM tool_rankings WHERE tool_id IN ({placeholders}) ORDER BY score DESC", alternatives)
            alt_ranked = cur.fetchall()
            if alt_ranked:
                alternative = alt_ranked[0]["tool_id"]
            else:
                alternative = alternatives[0]
        
        cur.execute("""
        UPDATE tool_rankings SET alternative_in_use=?, status='failover', updated_at=?
        WHERE tool_id=?
        """, (alternative, datetime.utcnow().isoformat(), tool_id))
        conn.commit()
        conn.close()
        
        return {
            "tool_id": tool_id,
            "failed_over_to": alternative,
            "status": "failover",
            "message": f"Tool {tool_id} agora usa alternativa {alternative}"
        }
    except Exception as e:
        return {"error": str(e)}

@register_tool(
    id="tool.usage_log",
    name="Registar uso de tool",
    description="Regista uso de tool para ranking por experiência",
    risk_level="LOW"
)
def tool_usage_log_tool(tool_id: str, agent_id: str = None, status: str = "ok", latency_ms: float = 0, error: str = None) -> dict:
    """Loga uso de tool para ranking"""
    try:
        import uuid
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO tool_calls_log (id, tool_id, agent_id, status, latency_ms, error, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            tool_id,
            agent_id,
            status,
            latency_ms,
            error,
            datetime.utcnow().isoformat()
        ))
        # Atualiza contadores em tool_rankings
        cur.execute("SELECT success_count, fail_count, usage_count, experience_points FROM tool_rankings WHERE tool_id=?", (tool_id,))
        row = cur.fetchone()
        if row:
            success_count, fail_count, usage_count, exp = row
            if status == "ok":
                success_count += 1
                exp += 1
            else:
                fail_count += 1
                exp = max(0, exp - 1)
            usage_count += 1
            cur.execute("""
            UPDATE tool_rankings SET success_count=?, fail_count=?, usage_count=?, experience_points=?, updated_at=?
            WHERE tool_id=?
            """, (success_count, fail_count, usage_count, exp, datetime.utcnow().isoformat(), tool_id))
        
        conn.commit()
        conn.close()
        return {"status": "logged", "tool_id": tool_id}
    except Exception as e:
        return {"error": str(e)}
