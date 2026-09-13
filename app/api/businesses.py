"""
API Negócios — Portfolio dos NOSSOS negócios
CRUD real com SQLite, sem invenção
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

router = APIRouter()

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def ensure_businesses_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        sector TEXT,
        description TEXT,
        status TEXT DEFAULT 'ativo',
        business_model TEXT,
        value_proposition TEXT,
        customer_segment TEXT,
        channel TEXT,
        revenue_monthly REAL DEFAULT 0,
        costs_monthly REAL DEFAULT 0,
        currency TEXT DEFAULT 'EUR',
        website_url TEXT,
        logo_url TEXT,
        tags TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Add column business_id to missions if not exists (for linking)
    try:
        cur.execute("SELECT business_id FROM missions LIMIT 1")
    except:
        try:
            cur.execute("ALTER TABLE missions ADD COLUMN business_id TEXT REFERENCES businesses(id)")
        except:
            pass
    conn.commit()
    conn.close()

# Garante tabela ao importar
ensure_businesses_table()

class BusinessCreate(BaseModel):
    name: str
    sector: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "ativo"  # ideia, validacao, ativo, pausado, vendido, arquivado
    business_model: Optional[str] = None
    value_proposition: Optional[str] = None
    customer_segment: Optional[str] = None
    channel: Optional[str] = None
    revenue_monthly: Optional[float] = 0
    costs_monthly: Optional[float] = 0
    currency: Optional[str] = "EUR"
    website_url: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    business_model: Optional[str] = None
    value_proposition: Optional[str] = None
    customer_segment: Optional[str] = None
    channel: Optional[str] = None
    revenue_monthly: Optional[float] = None
    costs_monthly: Optional[float] = None
    currency: Optional[str] = None
    website_url: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

def row_to_dict(row):
    d = dict(row)
    # calcula margem e lucro
    rev = d.get('revenue_monthly') or 0
    costs = d.get('costs_monthly') or 0
    profit = rev - costs
    margin = (profit / rev * 100) if rev > 0 else 0
    d['profit_monthly'] = profit
    d['margin_percent'] = margin
    return d

@router.get("/businesses")
def list_businesses():
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM businesses ORDER BY updated_at DESC")
    rows = cur.fetchall()
    businesses = [row_to_dict(r) for r in rows]
    
    # KPIs globais
    total_rev = sum(b.get('revenue_monthly',0) or 0 for b in businesses)
    total_costs = sum(b.get('costs_monthly',0) or 0 for b in businesses)
    total_profit = total_rev - total_costs
    total_margin = (total_profit / total_rev * 100) if total_rev>0 else 0
    
    conn.close()
    return {
        "businesses": businesses,
        "count": len(businesses),
        "kpis": {
            "total_businesses": len(businesses),
            "total_revenue": total_rev,
            "total_costs": total_costs,
            "total_profit": total_profit,
            "avg_margin": total_margin,
            "by_status": {s: len([b for b in businesses if b.get('status')==s]) for s in set(b.get('status') for b in businesses)}
        }
    }

@router.post("/businesses")
def create_business(data: BusinessCreate):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    bid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    cur.execute("""
        INSERT INTO businesses (id, name, sector, description, status, business_model, value_proposition, customer_segment, channel, revenue_monthly, costs_monthly, currency, website_url, tags, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (bid, data.name, data.sector, data.description, data.status, data.business_model, data.value_proposition, data.customer_segment, data.channel, data.revenue_monthly, data.costs_monthly, data.currency, data.website_url, data.tags, data.notes, now, now))
    conn.commit()
    cur.execute("SELECT * FROM businesses WHERE id=?", (bid,))
    row = cur.fetchone()
    conn.close()
    return {"business": row_to_dict(row), "status": "created"}

@router.get("/businesses/{business_id}")
def get_business(business_id: str):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "Negócio não encontrado", "id": business_id}
    
    business = row_to_dict(row)
    
    # Missões ligadas a este negócio (via business_id ou context)
    cur.execute("SELECT id, objective, status, created_at FROM missions WHERE business_id=? OR context LIKE ? ORDER BY created_at DESC LIMIT 10", (business_id, f"%{business_id}%"))
    missions = [dict(r) for r in cur.fetchall()]
    
    # Também procura por nome no objective
    if not missions and business.get('name'):
        cur.execute("SELECT id, objective, status, created_at FROM missions WHERE objective LIKE ? ORDER BY created_at DESC LIMIT 10", (f"%{business['name']}%",))
        missions = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return {"business": business, "missions": missions, "missions_count": len(missions)}

@router.put("/businesses/{business_id}")
def update_business(business_id: str, data: BusinessUpdate):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM businesses WHERE id=?", (business_id,))
    if not cur.fetchone():
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    fields = []
    values = []
    for k, v in data.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k}=?")
            values.append(v)
    
    if fields:
        fields.append("updated_at=?")
        values.append(datetime.utcnow().isoformat())
        values.append(business_id)
        cur.execute(f"UPDATE businesses SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    
    cur.execute("SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    conn.close()
    return {"business": row_to_dict(row), "status": "updated"}

@router.delete("/businesses/{business_id}")
def delete_business(business_id: str):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM businesses WHERE id=?", (business_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": business_id}

@router.get("/businesses/{business_id}/dashboard")
def business_dashboard(business_id: str):
    """Dashboard completo de um negócio — KPIs + missões + sites"""
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    business = row_to_dict(row)
    
    # Missões
    cur.execute("SELECT * FROM missions WHERE business_id=? ORDER BY created_at DESC LIMIT 20", (business_id,))
    missions_rows = cur.fetchall()
    missions = [dict(r) for r in missions_rows]
    
    # Tasks recentes desse negócio (via missions)
    mission_ids = [m['id'] for m in missions]
    tasks = []
    if mission_ids:
        placeholders = ",".join("?" for _ in mission_ids)
        cur.execute(f"SELECT * FROM tasks WHERE mission_id IN ({placeholders}) ORDER BY created_at DESC LIMIT 20", mission_ids)
        tasks = [dict(r) for r in cur.fetchall()]
    
    # Workspace files que mencionam o negócio?
    # Para MVP, lista ficheiros recentes
    import os
    workspace_path = Path(__file__).resolve().parent.parent.parent / "data" / "workspace"
    files = []
    if workspace_path.exists():
        for f in sorted(workspace_path.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            if f.is_file():
                files.append({"name": f.name, "size": f.stat().st_size, "url": f"/workspace/{f.name}"})
    
    conn.close()
    
    return {
        "business": business,
        "missions": missions,
        "tasks": tasks,
        "files": files,
        "kpis": {
            "revenue": business.get('revenue_monthly',0),
            "costs": business.get('costs_monthly',0),
            "profit": business.get('profit_monthly',0),
            "margin": business.get('margin_percent',0),
            "missions_count": len(missions),
            "tasks_count": len(tasks)
        }
    }
