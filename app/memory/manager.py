"""
Memory Manager — GOD §5.8 + Local AI Brain §14-15
Supports SQLite (local) and Postgres (Neon/Supabase zero-cost)
"""
from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import os

from app.config.settings import settings, ROOT_DIR

class MemoryType:
    SHORT = "short"
    LONG = "long"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

class MemoryManager:
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = ROOT_DIR / "data" / "brain.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _is_postgres(self):
        db_url = os.getenv('DATABASE_URL')
        return db_url and db_url.startswith(('postgres://', 'postgresql://'))

    def _get_conn(self):
        db_url = os.getenv('DATABASE_URL')
        if db_url and db_url.startswith(('postgres://', 'postgresql://')):
            import psycopg2
            import psycopg2.extras
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _execute(self, cur, query, params=None):
        db_url = os.getenv('DATABASE_URL')
        is_pg = db_url and db_url.startswith(('postgres://', 'postgresql://'))
        if is_pg:
            query = query.replace('?', '%s')
        if params is None:
            return cur.execute(query)
        return cur.execute(query, params)

    def add(self, content: str, type: str = MemoryType.SHORT, source: str = None, confidence: str = "medium", mission_id: str = None, task_id: str = None, expires_in_days: int = None) -> str:
        mem_id = str(uuid.uuid4())
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()

        conn = self._get_conn()
        try:
            cur = conn.cursor()
            self._execute(cur, """
                INSERT INTO memories (id, type, content, source, confidence, mission_id, task_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (mem_id, type, content, source, confidence, mission_id, task_id, expires_at))
            conn.commit()
        finally:
            try:
                cur.close()
            except:
                pass
            conn.close()
        return mem_id

    def search(self, query: str, type: str = None, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if type:
                self._execute(cur, "SELECT * FROM memories WHERE type=? AND content LIKE ? ORDER BY created_at DESC LIMIT ?", (type, f"%{query}%", limit))
            else:
                self._execute(cur, "SELECT * FROM memories WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?", (f"%{query}%", limit))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            try:
                cur.close()
            except:
                pass
            conn.close()

    def get_by_mission(self, mission_id: str) -> List[Dict]:
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            self._execute(cur, "SELECT * FROM memories WHERE mission_id=? ORDER BY created_at DESC", (mission_id,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            try:
                cur.close()
            except:
                pass
            conn.close()

    def list_recent(self, limit: int = 20) -> List[Dict]:
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            self._execute(cur, "SELECT * FROM memories ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            try:
                cur.close()
            except:
                pass
            conn.close()

memory_manager = MemoryManager()
