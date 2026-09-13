"""
API Providers — health, ranking, failover
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
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/providers/health")
def providers_health():
    """Verifica saúde de todos os providers e retorna status + ranking"""
    try:
        from app.agents.provider_health import ProviderHealthAgent, PROVIDERS_CONFIG
        from app.agents.base import TaskInput
        import uuid
        
        agent = ProviderHealthAgent()
        task = TaskInput(
            task_id=str(uuid.uuid4()),
            mission_id=str(uuid.uuid4()),
            agent_id="provider_health",
            objective="verificar saúde de todos os providers"
        )
        output = agent.execute(task)
        
        # Get current rankings
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM provider_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='ok' THEN 1 ELSE 0 END) as ok, SUM(CASE WHEN status='fail' THEN 1 ELSE 0 END) as fail FROM provider_rankings")
        stats = dict(cur.fetchone())
        conn.close()
        
        return {
            "status": "ok",
            "summary": output.summary,
            "stats": stats,
            "health": [a["data"] for a in output.artifacts if a["type"] == "provider_health"][0] if output.artifacts else [],
            "rankings": rankings,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@router.get("/providers/ranking")
def providers_ranking(category: Optional[str] = None):
    """Retorna ranking por experiência"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        if category:
            cur.execute("SELECT * FROM provider_rankings WHERE category=? ORDER BY score DESC", (category,))
        else:
            cur.execute("SELECT * FROM provider_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        
        # Best by category
        cur.execute("SELECT category FROM provider_rankings GROUP BY category")
        categories = [r["category"] for r in cur.fetchall()]
        
        best_by_cat = {}
        for cat in categories:
            cur.execute("SELECT * FROM provider_rankings WHERE category=? ORDER BY score DESC LIMIT 1", (cat,))
            best = cur.fetchone()
            if best:
                best_by_cat[cat] = dict(best)
        
        # History
        cur.execute("SELECT * FROM provider_health_history ORDER BY check_time DESC LIMIT 20")
        history = [dict(r) for r in cur.fetchall()]
        
        conn.close()
        
        return {
            "rankings": rankings,
            "best_by_category": best_by_cat,
            "history": history,
            "categories": categories,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/providers/health/{provider_id}")
def provider_health_detail(provider_id: str):
    """Detalhe de um provider específico"""
    try:
        from app.agents.provider_health import ProviderHealthAgent, PROVIDERS_CONFIG
        if provider_id not in PROVIDERS_CONFIG:
            return {"error": f"Provider {provider_id} não encontrado", "available": list(PROVIDERS_CONFIG.keys())}
        
        config = PROVIDERS_CONFIG[provider_id]
        agent = ProviderHealthAgent()
        check = agent._check_provider(provider_id, config)
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM provider_rankings WHERE provider_id=?", (provider_id,))
        ranking = cur.fetchone()
        cur.execute("SELECT * FROM provider_health_history WHERE provider_id=? ORDER BY check_time DESC LIMIT 10", (provider_id,))
        history = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        return {
            "provider_id": provider_id,
            "config": config,
            "current_check": check,
            "ranking": dict(ranking) if ranking else None,
            "history": history
        }
    except Exception as e:
        return {"error": str(e)}

class FailoverRequest(BaseModel):
    alternative: Optional[str] = None

@router.post("/providers/failover/{provider_id}")
def provider_failover(provider_id: str, data: FailoverRequest = None):
    """Força failover para alternativa"""
    try:
        from app.tools.provider_health import failover_tool
        alt = data.alternative if data else None
        result = failover_tool(provider_id, alt)
        return result
    except Exception as e:
        return {"error": str(e)}

@router.get("/providers/alternatives/{provider_id}")
def provider_alternatives(provider_id: str):
    """Lista alternativas para um provider"""
    try:
        from app.agents.provider_health import PROVIDERS_CONFIG
        if provider_id not in PROVIDERS_CONFIG:
            return {"error": "Provider não encontrado"}
        config = PROVIDERS_CONFIG[provider_id]
        
        conn = get_conn()
        cur = conn.cursor()
        alts = config.get("alternatives", [])
        if alts:
            placeholders = ",".join(["?"] * len(alts))
            cur.execute(f"SELECT provider_id, name, status, score, rank FROM provider_rankings WHERE provider_id IN ({placeholders}) ORDER BY score DESC", alts)
            alt_details = [dict(r) for r in cur.fetchall()]
        else:
            alt_details = []
        conn.close()
        
        return {
            "provider_id": provider_id,
            "alternatives": alts,
            "alternative_details": alt_details,
            "current_config": config
        }
    except Exception as e:
        return {"error": str(e)}
