"""
API Negócios — Portfolio dos NOSSOS negócios
CRUD real com SQLite, sem invenção + KPIs dinâmicos por setor
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
import json

router = APIRouter()

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"

# KPIs por setor — reconhece automaticamente que KPIs mostrar
KPIS_BY_SECTOR = {
    "restauração": {
        "label": "Restauração / Café / Restaurante",
        "kpis": [
            {"id": "ticket_medio", "label": "Ticket Médio", "unit": "€", "formula": "revenue / clientes", "icon": "🎫"},
            {"id": "mesas_dia", "label": "Mesas/Dia", "unit": "", "icon": "🪑"},
            {"id": "ocupacao", "label": "Taxa Ocupação", "unit": "%", "icon": "📊"},
            {"id": "custo_alimentos", "label": "Food Cost %", "unit": "%", "icon": "🍽️"},
            {"id": "clientes_dia", "label": "Clientes/Dia", "unit": "", "icon": "👥"}
        ]
    },
    "saas": {
        "label": "SaaS / Software",
        "kpis": [
            {"id": "mrr", "label": "MRR", "unit": "€", "icon": "💰"},
            {"id": "churn", "label": "Churn Rate", "unit": "%", "icon": "📉"},
            {"id": "cac", "label": "CAC", "unit": "€", "icon": "🎯"},
            {"id": "ltv", "label": "LTV", "unit": "€", "icon": "♾️"},
            {"id": "nps", "label": "NPS", "unit": "", "icon": "⭐"}
        ]
    },
    "ecommerce": {
        "label": "E-commerce",
        "kpis": [
            {"id": "conversao", "label": "Taxa Conversão", "unit": "%", "icon": "🛒"},
            {"id": "aov", "label": "AOV", "unit": "€", "icon": "💳"},
            {"id": "carrinho_abandono", "label": "Abandono Carrinho", "unit": "%", "icon": "🛍️"},
            {"id": "cac", "label": "CAC", "unit": "€", "icon": "🎯"},
            {"id": "retencao", "label": "Retenção", "unit": "%", "icon": "🔁"}
        ]
    },
    "consultoria": {
        "label": "Consultoria / Serviços",
        "kpis": [
            {"id": "utilizacao", "label": "Taxa Utilização", "unit": "%", "icon": "⏱️"},
            {"id": "valor_hora", "label": "Valor Hora", "unit": "€", "icon": "💼"},
            {"id": "projetos_ativos", "label": "Projetos Ativos", "unit": "", "icon": "📁"},
            {"id": "satisfacao", "label": "Satisfação Cliente", "unit": "/10", "icon": "😊"},
            {"id": "pipeline", "label": "Pipeline", "unit": "€", "icon": "🔮"}
        ]
    },
    "infoproduto": {
        "label": "Infoproduto / Curso",
        "kpis": [
            {"id": "alunos", "label": "Alunos Ativos", "unit": "", "icon": "🎓"},
            {"id": "conclusao", "label": "Taxa Conclusão", "unit": "%", "icon": "✅"},
            {"id": "reembolso", "label": "Taxa Reembolso", "unit": "%", "icon": "↩️"},
            {"id": "ltv_aluno", "label": "LTV Aluno", "unit": "€", "icon": "💰"},
            {"id": "nps", "label": "NPS", "unit": "", "icon": "⭐"}
        ]
    },
    "default": {
        "label": "Geral",
        "kpis": [
            {"id": "receita", "label": "Receita Mensal", "unit": "€", "icon": "💰"},
            {"id": "custos", "label": "Custos Mensais", "unit": "€", "icon": "💸"},
            {"id": "lucro", "label": "Lucro", "unit": "€", "icon": "📈"},
            {"id": "margem", "label": "Margem", "unit": "%", "icon": "📊"},
            {"id": "crescimento", "label": "Crescimento M/M", "unit": "%", "icon": "🚀"}
        ]
    }
}

def get_kpis_for_sector(sector: str) -> Dict[str, Any]:
    """Retorna KPIs sugeridos para um setor"""
    if not sector:
        return KPIS_BY_SECTOR["default"]
    sector_lower = sector.lower()
    for key, config in KPIS_BY_SECTOR.items():
        if key in sector_lower or sector_lower in key:
            return config
        # Check aliases
        if "restaur" in sector_lower and key == "restauração":
            return config
        if "café" in sector_lower or "cafe" in sector_lower and key == "restauração":
            return KPIS_BY_SECTOR["restauração"]
        if "saas" in sector_lower or "software" in sector_lower:
            return KPIS_BY_SECTOR["saas"]
        if "ecommerce" in sector_lower or "loja" in sector_lower:
            return KPIS_BY_SECTOR["ecommerce"]
        if "consult" in sector_lower:
            return KPIS_BY_SECTOR["consultoria"]
        if "curso" in sector_lower or "infoproduto" in sector_lower or "formação" in sector_lower:
            return KPIS_BY_SECTOR["infoproduto"]
    return KPIS_BY_SECTOR["default"]

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
        kpis_config TEXT,
        custom_kpis TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Add columns if not exists (migration)
    try:
        cur.execute("SELECT kpis_config FROM businesses LIMIT 1")
    except:
        try:
            cur.execute("ALTER TABLE businesses ADD COLUMN kpis_config TEXT")
        except:
            pass
    try:
        cur.execute("SELECT custom_kpis FROM businesses LIMIT 1")
    except:
        try:
            cur.execute("ALTER TABLE businesses ADD COLUMN custom_kpis TEXT")
        except:
            pass
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
    status: Optional[str] = "ativo"
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
    kpis_config: Optional[str] = None
    custom_kpis: Optional[str] = None

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
    kpis_config: Optional[str] = None
    custom_kpis: Optional[str] = None

def row_to_dict(row):
    d = dict(row)
    # calcula margem e lucro
    rev = d.get('revenue_monthly') or 0
    costs = d.get('costs_monthly') or 0
    profit = rev - costs
    margin = (profit / rev * 100) if rev > 0 else 0
    d['profit_monthly'] = profit
    d['margin_percent'] = margin
    
    # Parse kpis_config
    try:
        if d.get('kpis_config'):
            d['kpis_config_parsed'] = json.loads(d['kpis_config'])
        else:
            # Auto-detect baseado no setor
            sector = d.get('sector') or ''
            kpis_suggested = get_kpis_for_sector(sector)
            d['kpis_config_parsed'] = kpis_suggested
            d['kpis_suggested'] = kpis_suggested
    except:
        d['kpis_config_parsed'] = get_kpis_for_sector(d.get('sector') or '')
    
    try:
        if d.get('custom_kpis'):
            d['custom_kpis_parsed'] = json.loads(d['custom_kpis'])
        else:
            d['custom_kpis_parsed'] = {}
    except:
        d['custom_kpis_parsed'] = {}
    
    # KPIs dinâmicos calculados
    custom = d.get('custom_kpis_parsed', {})
    d['dynamic_kpis'] = {
        "receita": rev,
        "custos": costs,
        "lucro": profit,
        "margem": round(margin, 1),
        **custom
    }
    
    return d

@router.get("/businesses/kpis/suggestions")
def kpis_suggestions(sector: str = None):
    """Retorna KPIs sugeridos para um setor — usado no frontend para reconhecer que KPIs mostrar"""
    config = get_kpis_for_sector(sector or "")
    return {
        "sector": sector or "default",
        "suggested": config,
        "all_sectors": {k: v["label"] for k, v in KPIS_BY_SECTOR.items()}
    }

@router.get("/businesses/kpis/all")
def kpis_all():
    """Retorna todos os KPIs por setor"""
    return KPIS_BY_SECTOR

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
    
    # Agrupa por setor para mostrar KPIs por setor
    by_sector = {}
    for b in businesses:
        sec = b.get('sector') or 'Outros'
        if sec not in by_sector:
            by_sector[sec] = {"count": 0, "revenue": 0, "kpis_config": get_kpis_for_sector(sec)}
        by_sector[sec]["count"] += 1
        by_sector[sec]["revenue"] += b.get('revenue_monthly',0) or 0
    
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
            "by_status": {s: len([b for b in businesses if b.get('status')==s]) for s in set(b.get('status') for b in businesses)},
            "by_sector": by_sector
        }
    }

@router.post("/businesses")
def create_business(data: BusinessCreate):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    bid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    # Auto-detect KPIs baseado no setor se não fornecido
    kpis_config = data.kpis_config
    if not kpis_config and data.sector:
        suggested = get_kpis_for_sector(data.sector)
        kpis_config = json.dumps(suggested)
    
    cur.execute("""
        INSERT INTO businesses (id, name, sector, description, status, business_model, value_proposition, customer_segment, channel, revenue_monthly, costs_monthly, currency, website_url, tags, notes, kpis_config, custom_kpis, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (bid, data.name, data.sector, data.description, data.status, data.business_model, data.value_proposition, data.customer_segment, data.channel, data.revenue_monthly, data.costs_monthly, data.currency, data.website_url, data.tags, data.notes, kpis_config, data.custom_kpis, now, now))
    conn.commit()
    cur.execute("SELECT * FROM businesses WHERE id=?", (bid,))
    row = cur.fetchone()
    conn.close()
    
    business = row_to_dict(row)
    return {
        "business": business, 
        "status": "created",
        "kpis_detected": business.get('kpis_config_parsed'),
        "message": f"Negócio criado com KPIs auto-detectados para setor {data.sector or 'geral'}: {', '.join([k['label'] for k in business.get('kpis_config_parsed', {}).get('kpis', [])[:3]])}"
    }

@router.get("/businesses/{business_id}")
def get_business(business_id: str):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    business = row_to_dict(row)
    
    # Missões ligadas a este negócio
    cur.execute("SELECT id, objective, status, created_at FROM missions WHERE business_id=? ORDER BY created_at DESC LIMIT 20", (business_id,))
    missions = [dict(r) for r in cur.fetchall()]
    
    # Também procura por nome no objective
    if not missions and business.get('name'):
        cur.execute("SELECT id, objective, status, created_at FROM missions WHERE objective LIKE ? ORDER BY created_at DESC LIMIT 10", (f"%{business['name']}%",))
        missions = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return {"business": business, "missions": missions, "missions_count": len(missions), "kpis_suggested": business.get('kpis_config_parsed')}

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
    
    # Se setor mudou, recalcula KPIs sugeridos
    if data.sector:
        suggested = get_kpis_for_sector(data.sector)
        fields.append("kpis_config=?")
        values.append(json.dumps(suggested))
    
    if fields:
        fields.append("updated_at=?")
        values.append(datetime.utcnow().isoformat())
        values.append(business_id)
        cur.execute(f"UPDATE businesses SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    
    cur.execute("SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    conn.close()
    business = row_to_dict(row)
    return {"business": business, "status": "updated", "kpis_detected": business.get('kpis_config_parsed')}

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
    """Dashboard completo de um negócio — KPIs + missões + sites + KPIs dinâmicos"""
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
            "tasks_count": len(tasks),
            "dynamic": business.get('dynamic_kpis', {}),
            "suggested": business.get('kpis_config_parsed', {})
        }
    }

@router.post("/businesses/{business_id}/kpis")
def update_business_kpis(business_id: str, kpis: Dict[str, Any]):
    """Atualiza KPIs custom de um negócio"""
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT custom_kpis FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    # Merge com existentes
    existing = {}
    try:
        if row["custom_kpis"]:
            existing = json.loads(row["custom_kpis"])
    except:
        pass
    
    existing.update(kpis)
    
    cur.execute("UPDATE businesses SET custom_kpis=?, updated_at=? WHERE id=?", (json.dumps(existing), datetime.utcnow().isoformat(), business_id))
    conn.commit()
    cur.execute("SELECT * FROM businesses WHERE id=?", (business_id,))
    updated = cur.fetchone()
    conn.close()
    
    return {"business": row_to_dict(updated), "kpis": existing, "status": "kpis_updated"}
