"""
Episodic memory — TASK, ACTION, RESULT, ERROR, LESSON — Local AI Brain §15
Supports SQLite and Postgres (Neon)
"""
from app.memory.manager import memory_manager, MemoryType
import uuid
import sqlite3
from pathlib import Path
from app.config.settings import ROOT_DIR
from datetime import datetime
import os

def _get_conn():
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith(('postgres://', 'postgresql://')):
        import psycopg2
        import psycopg2.extras
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
    db_path = ROOT_DIR / "data" / "brain.db"
    conn = sqlite3.connect(str(db_path))
    return conn

def _execute(cur, query, params=None):
    db_url = os.getenv('DATABASE_URL')
    is_pg = db_url and db_url.startswith(('postgres://', 'postgresql://'))
    if is_pg:
        query = query.replace('?', '%s')
    if params is None:
        return cur.execute(query)
    return cur.execute(query, params)

def add_experience(task: str, agent: str, action: str, result: str, error: str = None, lesson: str = None):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        exp_id = str(uuid.uuid4())
        _execute(cur, """
            INSERT INTO experiences (id, task, agent, action, result, error, lesson, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (exp_id, task, agent, action, result, error, lesson, datetime.utcnow().isoformat()))
        conn.commit()
        content = f"TASK: {task} | AGENT: {agent} | ACTION: {action} | RESULT: {result} | ERROR: {error} | LESSON: {lesson}"
        memory_manager.add(content, type=MemoryType.EPISODIC, source=agent, confidence="medium")
        return exp_id
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()

def search_experiences(query: str, limit: int = 5):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        _execute(cur, "SELECT * FROM experiences WHERE task LIKE ? OR lesson LIKE ? ORDER BY created_at DESC LIMIT ?", (f"%{query}%", f"%{query}%", limit))
        return [dict(r) for r in cur.fetchall()]
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()
