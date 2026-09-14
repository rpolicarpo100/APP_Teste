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
    """Retorna KPIs sugeridos para um setor — normaliza para detectar E-commerce com hífen, etc"""
    if not sector:
        return KPIS_BY_SECTOR["default"]
    # Normaliza: remove hífen, espaços, acentos básicos
    sector_lower = sector.lower().replace("-", "").replace(" ", "").replace("_", "")
    sector_original_lower = sector.lower()
    
    # Mapeamento direto normalizado
    if "restaur" in sector_lower or "cafe" in sector_lower or "café" in sector_original_lower:
        return KPIS_BY_SECTOR["restauração"]
    if "saas" in sector_lower or "software" in sector_lower:
        return KPIS_BY_SECTOR["saas"]
    if "ecommerce" in sector_lower or "e-commerce" in sector_original_lower or "loja" in sector_lower or "shopify" in sector_lower or "expensy" in sector_lower:
        return KPIS_BY_SECTOR["ecommerce"]
    if "consult" in sector_lower:
        return KPIS_BY_SECTOR["consultoria"]
    if "curso" in sector_lower or "infoproduto" in sector_lower or "formac" in sector_lower or "educa" in sector_lower:
        return KPIS_BY_SECTOR["infoproduto"]
    
    for key, config in KPIS_BY_SECTOR.items():
        key_norm = key.lower().replace("-", "").replace(" ", "")
        if key_norm in sector_lower or sector_lower in key_norm:
            return config
    
    return KPIS_BY_SECTOR["default"]

def get_conn():
    import os
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith(('postgres://', 'postgresql://')):
        # Use Postgres via psycopg2 for zero-cost Neon/Supabase persistence
        import psycopg2
        import psycopg2.extras
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    # Fallback SQLite (ephemeral on Render free without disk)
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"[Businesses] get_conn erro: {e} — tenta apagar DB")
        try:
            if DB_PATH.exists():
                DB_PATH.unlink()
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e2:
            print(f"[Businesses] Falha ao recriar DB: {e2}")
            raise

def _is_postgres():
    import os
    db_url = os.getenv('DATABASE_URL')
    return db_url and db_url.startswith(('postgres://', 'postgresql://'))


def _execute(cur, query, params=None):
    import os
    db_url = os.getenv('DATABASE_URL')
    is_pg = db_url and db_url.startswith(('postgres://', 'postgresql://'))
    if is_pg:
        # Convert ? to %s for Postgres
        query = query.replace('?', '%s')
    if params is None:
        return cur.execute(query)
    return cur.execute(query, params)


def _row_to_dict(row, cur=None):
    # For SQLite Row or Postgres tuple
    if isinstance(row, dict):
        return row
    if hasattr(row, 'keys'):
        try:
            return dict(row)
        except:
            pass
    # For psycopg2, use cursor description
    if cur and hasattr(cur, 'description'):
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, row))
    return dict(row) if row else None


# Plataformas suportadas para múltiplos links — EXPENSYVX exemplo
PLATFORMS = {
    "youtube": {"label": "YouTube", "icon": "▶️", "color": "#FF0000", "placeholder": "https://youtube.com/@..."},
    "tiktok": {"label": "TikTok", "icon": "🎵", "color": "#000000", "placeholder": "https://tiktok.com/@..."},
    "instagram": {"label": "Instagram", "icon": "📸", "color": "#E4405F", "placeholder": "https://instagram.com/..."},
    "shopify": {"label": "Shopify", "icon": "🛍️", "color": "#95BF47", "placeholder": "https://...myshopify.com"},
    "printify": {"label": "Printify", "icon": "🖨️", "color": "#4A90E2", "placeholder": "https://printify.com/..."},
    "gumroad": {"label": "Gumroad", "icon": "💰", "color": "#FF90E8", "placeholder": "https://gumroad.com/..."},
    "website": {"label": "Website", "icon": "🌐", "color": "#111", "placeholder": "https://..."},
    "facebook": {"label": "Facebook", "icon": "👍", "color": "#1877F2", "placeholder": "https://facebook.com/..."},
    "twitter": {"label": "X/Twitter", "icon": "🐦", "color": "#000", "placeholder": "https://x.com/..."},
    "linkedin": {"label": "LinkedIn", "icon": "💼", "color": "#0A66C2", "placeholder": "https://linkedin.com/..."},
    "etsy": {"label": "Etsy", "icon": "🛒", "color": "#F56400", "placeholder": "https://etsy.com/..."},
    "amazon": {"label": "Amazon", "icon": "📦", "color": "#FF9900", "placeholder": "https://amazon.com/..."},
    "other": {"label": "Outro", "icon": "🔗", "color": "#888", "placeholder": "https://..."}
}

def ensure_businesses_table():
    import os
    db_url = os.getenv('DATABASE_URL')
    is_postgres = db_url and db_url.startswith(('postgres://', 'postgresql://'))
    try:
        conn = get_conn()
        cur = conn.cursor()
    except Exception as e:
        print(f"[Businesses] get_conn falhou: {e}")
        return
    # Tabela business_links — múltiplos links por negócio (EXPENSYVX: youtube, tiktok, insta, shopify, printify, gumroad)
    _execute(cur, """
    CREATE TABLE IF NOT EXISTS business_links (
        id TEXT PRIMARY KEY,
        business_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        url TEXT NOT NULL,
        label TEXT,
        is_primary INTEGER DEFAULT 0,
        clicks INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(business_id) REFERENCES businesses(id) ON DELETE CASCADE
    )
    """)
    _execute(cur, """
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
        _execute(cur, "SELECT kpis_config FROM businesses LIMIT 1")
    except:
        try:
            _execute(cur, "ALTER TABLE businesses ADD COLUMN kpis_config TEXT")
        except:
            pass
    try:
        _execute(cur, "SELECT custom_kpis FROM businesses LIMIT 1")
    except:
        try:
            _execute(cur, "ALTER TABLE businesses ADD COLUMN custom_kpis TEXT")
        except:
            pass
    # Add column business_id to missions if not exists (for linking)
    try:
        _execute(cur, "SELECT business_id FROM missions LIMIT 1")
    except:
        try:
            _execute(cur, "ALTER TABLE missions ADD COLUMN business_id TEXT REFERENCES businesses(id)")
        except:
            pass
    conn.commit()
    conn.close()

# Garante tabela ao importar — safe para Render
try:
    ensure_businesses_table()
except Exception as e:
    print(f"[Businesses] Erro ao criar tabela no import (ignorado): {e}")

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

def get_business_links(business_id: str) -> List[Dict[str, Any]]:
    """Retorna todos os links de um negócio"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        _execute(cur, "SELECT * FROM business_links WHERE business_id=? ORDER BY is_primary DESC, platform ASC", (business_id,))
        links = [dict(r) for r in cur.fetchall()]
        conn.close()
        # Enriquece com config da plataforma
        for link in links:
            plat = link.get('platform', 'other')
            cfg = PLATFORMS.get(plat, PLATFORMS['other'])
            link['platform_label'] = cfg['label']
            link['platform_icon'] = cfg['icon']
            link['platform_color'] = cfg['color']
        return links
    except Exception as e:
        print(f"[BusinessLinks] Erro ao buscar links: {e}")
        return []

def row_to_dict(row, include_links: bool = True):
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
    
    # Links múltiplos — EXPENSYVX exemplo
    if include_links and d.get('id'):
        try:
            d['links'] = get_business_links(d['id'])
            d['links_count'] = len(d['links'])
            # Agrupa por plataforma
            by_platform = {}
            for link in d['links']:
                plat = link.get('platform')
                if plat not in by_platform:
                    by_platform[plat] = []
                by_platform[plat].append(link)
            d['links_by_platform'] = by_platform
        except:
            d['links'] = []
            d['links_count'] = 0
            d['links_by_platform'] = {}
    
    return d

@router.get("/businesses/platforms")
def platforms_list():
    """Lista plataformas suportadas para múltiplos links — EXPENSYVX: youtube, tiktok, insta, shopify, printify, gumroad"""
    return {"platforms": PLATFORMS, "count": len(PLATFORMS)}

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
    _execute(cur, "SELECT * FROM businesses ORDER BY updated_at DESC")
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
    
    _execute(cur, """
        INSERT INTO businesses (id, name, sector, description, status, business_model, value_proposition, customer_segment, channel, revenue_monthly, costs_monthly, currency, website_url, tags, notes, kpis_config, custom_kpis, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (bid, data.name, data.sector, data.description, data.status, data.business_model, data.value_proposition, data.customer_segment, data.channel, data.revenue_monthly, data.costs_monthly, data.currency, data.website_url, data.tags, data.notes, kpis_config, data.custom_kpis, now, now))
    conn.commit()
    _execute(cur, "SELECT * FROM businesses WHERE id=?", (bid,))
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
    _execute(cur, "SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    business = row_to_dict(row)
    
    # Missões ligadas a este negócio
    _execute(cur, "SELECT id, objective, status, created_at FROM missions WHERE business_id=? ORDER BY created_at DESC LIMIT 20", (business_id,))
    missions = [dict(r) for r in cur.fetchall()]
    
    # Também procura por nome no objective
    if not missions and business.get('name'):
        _execute(cur, "SELECT id, objective, status, created_at FROM missions WHERE objective LIKE ? ORDER BY created_at DESC LIMIT 10", (f"%{business['name']}%",))
        missions = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return {"business": business, "missions": missions, "missions_count": len(missions), "kpis_suggested": business.get('kpis_config_parsed')}

@router.put("/businesses/{business_id}")
def update_business(business_id: str, data: BusinessUpdate):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT * FROM businesses WHERE id=?", (business_id,))
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
        _execute(cur, f"UPDATE businesses SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    
    _execute(cur, "SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    conn.close()
    business = row_to_dict(row)
    return {"business": business, "status": "updated", "kpis_detected": business.get('kpis_config_parsed')}

@router.delete("/businesses/{business_id}")
def delete_business(business_id: str):
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "DELETE FROM businesses WHERE id=?", (business_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": business_id}

@router.get("/businesses/{business_id}/dashboard")
def business_dashboard(business_id: str):
    """Dashboard completo de um negócio — KPIs + missões + sites + KPIs dinâmicos"""
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT * FROM businesses WHERE id=?", (business_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    business = row_to_dict(row)
    
    # Missões
    _execute(cur, "SELECT * FROM missions WHERE business_id=? ORDER BY created_at DESC LIMIT 20", (business_id,))
    missions_rows = cur.fetchall()
    missions = [dict(r) for r in missions_rows]
    
    # Tasks recentes desse negócio (via missions)
    mission_ids = [m['id'] for m in missions]
    tasks = []
    if mission_ids:
        placeholders = ",".join("?" for _ in mission_ids)
        _execute(cur, f"SELECT * FROM tasks WHERE mission_id IN ({placeholders}) ORDER BY created_at DESC LIMIT 20", mission_ids)
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

# === BUSINESS LINKS — múltiplos links por negócio (EXPENSYVX: youtube, tiktok, insta, shopify, printify, gumroad) ===

class BusinessLinkCreate(BaseModel):
    platform: str  # youtube, tiktok, instagram, shopify, printify, gumroad, website, etc
    url: str
    label: Optional[str] = None
    is_primary: Optional[bool] = False

class BusinessLinkUpdate(BaseModel):
    platform: Optional[str] = None
    url: Optional[str] = None
    label: Optional[str] = None
    is_primary: Optional[bool] = None

@router.get("/businesses/{business_id}/links")
def list_business_links(business_id: str):
    """Lista todos os links de um negócio — EXPENSYVX tem 6+ links"""
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT id FROM businesses WHERE id=?", (business_id,))
    if not cur.fetchone():
        conn.close()
        return {"error": "Negócio não encontrado"}
    conn.close()
    links = get_business_links(business_id)
    return {"business_id": business_id, "links": links, "count": len(links), "platforms": PLATFORMS}

@router.post("/businesses/{business_id}/links")
def create_business_link(business_id: str, data: BusinessLinkCreate):
    """Adiciona link a um negócio — ex: EXPENSYVX + youtube"""
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT id FROM businesses WHERE id=?", (business_id,))
    if not cur.fetchone():
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    if data.platform not in PLATFORMS:
        # Permite custom mas avisa
        if data.platform not in ["custom", "other"]:
            # Auto-mapeia para other se não conhecido
            pass
    
    link_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    _execute(cur, """
        INSERT INTO business_links (id, business_id, platform, url, label, is_primary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (link_id, business_id, data.platform, data.url, data.label, 1 if data.is_primary else 0, now))
    
    # Se é primary, remove primary dos outros
    if data.is_primary:
        _execute(cur, "UPDATE business_links SET is_primary=0 WHERE business_id=? AND id!=?", (business_id, link_id))
    
    conn.commit()
    _execute(cur, "SELECT * FROM business_links WHERE id=?", (link_id,))
    row = cur.fetchone()
    conn.close()
    
    link = dict(row) if row else {}
    plat_cfg = PLATFORMS.get(link.get('platform', 'other'), PLATFORMS['other'])
    link['platform_label'] = plat_cfg['label']
    link['platform_icon'] = plat_cfg['icon']
    
    return {"link": link, "status": "created", "business_id": business_id}

@router.put("/businesses/{business_id}/links/{link_id}")
def update_business_link(business_id: str, link_id: str, data: BusinessLinkUpdate):
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT * FROM business_links WHERE id=? AND business_id=?", (link_id, business_id))
    if not cur.fetchone():
        conn.close()
        return {"error": "Link não encontrado"}
    
    fields = []
    values = []
    for k, v in data.dict(exclude_unset=True).items():
        if v is not None:
            if k == 'is_primary':
                fields.append("is_primary=?")
                values.append(1 if v else 0)
            else:
                fields.append(f"{k}=?")
                values.append(v)
    
    if fields:
        values.append(link_id)
        _execute(cur, f"UPDATE business_links SET {', '.join(fields)} WHERE id=?", values)
        if data.is_primary:
            _execute(cur, "UPDATE business_links SET is_primary=0 WHERE business_id=? AND id!=?", (business_id, link_id))
        conn.commit()
    
    _execute(cur, "SELECT * FROM business_links WHERE id=?", (link_id,))
    row = cur.fetchone()
    conn.close()
    return {"link": dict(row) if row else {}, "status": "updated"}

@router.delete("/businesses/{business_id}/links/{link_id}")
def delete_business_link(business_id: str, link_id: str):
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "DELETE FROM business_links WHERE id=? AND business_id=?", (link_id, business_id))
    conn.commit()
    conn.close()
    return {"status": "deleted", "link_id": link_id, "business_id": business_id}

@router.post("/businesses/{business_id}/links/bulk")
def bulk_create_links(business_id: str, links: List[BusinessLinkCreate]):
    """Cria múltiplos links de uma vez — ideal para EXPENSYVX com 6 links"""
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT id FROM businesses WHERE id=?", (business_id,))
    if not cur.fetchone():
        conn.close()
        return {"error": "Negócio não encontrado"}
    
    created = []
    for data in links:
        link_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        _execute(cur, """
            INSERT INTO business_links (id, business_id, platform, url, label, is_primary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (link_id, business_id, data.platform, data.url, data.label, 1 if data.is_primary else 0, now))
        created.append({"id": link_id, "platform": data.platform, "url": data.url})
    
    conn.commit()
    conn.close()
    return {"created": created, "count": len(created), "business_id": business_id}

@router.post("/businesses/{business_id}/kpis")
def update_business_kpis(business_id: str, kpis: Dict[str, Any]):
    """Atualiza KPIs custom de um negócio"""
    ensure_businesses_table()
    conn = get_conn()
    cur = conn.cursor()
    _execute(cur, "SELECT custom_kpis FROM businesses WHERE id=?", (business_id,))
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
    
    _execute(cur, "UPDATE businesses SET custom_kpis=?, updated_at=? WHERE id=?", (json.dumps(existing), datetime.utcnow().isoformat(), business_id))
    conn.commit()
    _execute(cur, "SELECT * FROM businesses WHERE id=?", (business_id,))
    updated = cur.fetchone()
    conn.close()
    
    return {"business": row_to_dict(updated), "kpis": existing, "status": "kpis_updated"}
