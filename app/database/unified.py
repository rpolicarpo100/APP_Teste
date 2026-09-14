"""
Unified DB — SQLite + Neon Postgres (free forever) — zero-cost
Abstrai sqlite3 vs postgres para missions/tasks persistência total

- Se DATABASE_URL=postgres://... (Neon 0.5GB free) -> usa psycopg2
- Se não -> SQLite data/brain.db (efêmero no Render free sem disk)

Resolve tarefa 3: missions/tasks migrar SQLite efêmero → Neon Postgres
"""
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config.settings import ROOT_DIR

DB_PATH = ROOT_DIR / "data" / "brain.db"

def is_postgres() -> bool:
    url = os.getenv('DATABASE_URL') or ""
    return url.startswith(('postgres://', 'postgresql://'))

def get_db_url() -> str:
    return os.getenv('DATABASE_URL') or f"sqlite:///{DB_PATH}"

def _get_pg_conn():
    import psycopg2
    import psycopg2.extras
    url = os.getenv('DATABASE_URL')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    conn = psycopg2.connect(url)
    conn.autocommit = False
    return conn

def get_conn():
    """Retorna conn compatível — sqlite3 ou psycopg2"""
    if is_postgres():
        try:
            return _get_pg_conn()
        except Exception as e:
            print(f"[UnifiedDB] Postgres fail {e} — fallback SQLite")
    # SQLite fallback
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"[UnifiedDB] SQLite fail {e} — tenta recriar")
        if DB_PATH.exists():
            try:
                DB_PATH.unlink()
            except:
                pass
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

def _convert_query(query: str) -> str:
    """Converte ? placeholders para %s se Postgres"""
    if is_postgres():
        # Conta ? e troca por %s, mas ignora ?? etc
        # Simples: troca todos ? por %s
        return query.replace('?', '%s')
    return query

def execute(conn, query: str, params=None):
    """Execute com conversão automática ? -> %s"""
    q = _convert_query(query)
    cur = conn.cursor()
    if params is None:
        cur.execute(q)
    else:
        cur.execute(q, params)
    return cur

def executemany(conn, query: str, params_list):
    q = _convert_query(query)
    cur = conn.cursor()
    cur.executemany(q, params_list)
    return cur

def fetchone(cur):
    row = cur.fetchone()
    if row is None:
        return None
    if is_postgres():
        # psycopg2 RealDictRow ou tuple?
        if isinstance(row, dict):
            return row
        # Se for tuple, precisamos converter — mas usamos RealDictCursor em get_conn? No unified usamos default cursor
        # Para compat, vamos usar dict se possível
        try:
            # tenta dict(row)
            return dict(row)
        except:
            return row
    else:
        # sqlite Row -> dict
        try:
            return dict(row)
        except:
            return row

def fetchall(cur):
    rows = cur.fetchall()
    result = []
    for r in rows:
        if is_postgres():
            if isinstance(r, dict):
                result.append(r)
            else:
                try:
                    result.append(dict(r))
                except:
                    # Se tuple, retorna como dict via description
                    try:
                        cols = [d[0] for d in cur.description]
                        result.append(dict(zip(cols, r)))
                    except:
                        result.append(r)
        else:
            try:
                result.append(dict(r))
            except:
                result.append(r)
    return result

def init_tables(conn):
    """Cria tabelas se não existirem — funciona SQLite e Postgres"""
    is_pg = is_postgres()
    try:
        # missions
        if is_pg:
            execute(conn, """
                CREATE TABLE IF NOT EXISTS missions (
                    id TEXT PRIMARY KEY,
                    objective TEXT NOT NULL,
                    expected_result TEXT,
                    context TEXT,
                    constraints_text TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'PENDING',
                    autonomy_level INTEGER DEFAULT 2,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            execute(conn, """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    mission_id TEXT REFERENCES missions(id),
                    objective TEXT NOT NULL,
                    description TEXT,
                    agent_id TEXT,
                    required_skills TEXT,
                    dependencies TEXT,
                    priority TEXT DEFAULT 'medium',
                    acceptance_criteria TEXT,
                    risk TEXT DEFAULT 'low',
                    required_tools TEXT,
                    status TEXT DEFAULT 'PENDING',
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    result_summary TEXT,
                    artifacts TEXT,
                    evidence TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
        else:
            execute(conn, """CREATE TABLE IF NOT EXISTS missions (
                id TEXT PRIMARY KEY,
                objective TEXT NOT NULL,
                expected_result TEXT,
                context TEXT,
                constraints_text TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'PENDING',
                autonomy_level INTEGER DEFAULT 2,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )""")
            execute(conn, """CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                mission_id TEXT REFERENCES missions(id),
                objective TEXT NOT NULL,
                description TEXT,
                agent_id TEXT,
                required_skills TEXT,
                dependencies TEXT,
                priority TEXT DEFAULT 'medium',
                acceptance_criteria TEXT,
                risk TEXT DEFAULT 'low',
                required_tools TEXT,
                status TEXT DEFAULT 'PENDING',
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                result_summary TEXT,
                artifacts TEXT,
                evidence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )""")
        # conversations, messages, memories, etc
        execute(conn, """CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created_at TEXT,
            updated_at TEXT
        )""")
        execute(conn, """CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT
        )""")
        execute(conn, """CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        execute(conn, """CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            confidence TEXT DEFAULT 'medium',
            mission_id TEXT,
            task_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )""")
        execute(conn, """CREATE TABLE IF NOT EXISTS businesses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            sector TEXT,
            description TEXT,
            status TEXT DEFAULT 'ativo',
            revenue_monthly REAL DEFAULT 0,
            costs_monthly REAL DEFAULT 0,
            profit_monthly REAL DEFAULT 0,
            margin_percent REAL DEFAULT 0,
            value_proposition TEXT,
            customer_segment TEXT,
            channel TEXT,
            website_url TEXT,
            links TEXT,
            tags TEXT,
            notes TEXT,
            kpis_config TEXT,
            dynamic_kpis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
    except Exception as e:
        print(f"[UnifiedDB] init_tables fail: {e}")
        try:
            conn.rollback()
        except:
            pass
