"""
Memory Manager — GOD §5.8 + Local AI Brain §14-15
"""
from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

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

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, content: str, type: str = MemoryType.SHORT, source: str = None, confidence: str = "medium", mission_id: str = None, task_id: str = None, expires_in_days: int = None) -> str:
        mem_id = str(uuid.uuid4())
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()

        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT INTO memories (id, type, content, source, confidence, mission_id, task_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (mem_id, type, content, source, confidence, mission_id, task_id, expires_at))
            conn.commit()
        finally:
            conn.close()
        return mem_id

    def search(self, query: str, type: str = None, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        try:
            if type:
                cur = conn.execute("SELECT * FROM memories WHERE type=? AND content LIKE ? ORDER BY created_at DESC LIMIT ?", (type, f"%{query}%", limit))
            else:
                cur = conn.execute("SELECT * FROM memories WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?", (f"%{query}%", limit))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_by_mission(self, mission_id: str) -> List[Dict]:
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT * FROM memories WHERE mission_id=? ORDER BY created_at DESC", (mission_id,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def list_recent(self, limit: int = 20) -> List[Dict]:
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT * FROM memories ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

memory_manager = MemoryManager()
