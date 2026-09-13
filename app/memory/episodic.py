"""
Episodic memory — TASK, ACTION, RESULT, ERROR, LESSON — Local AI Brain §15
"""
from app.memory.manager import memory_manager, MemoryType
import uuid
import sqlite3
from pathlib import Path
from app.config.settings import ROOT_DIR
from datetime import datetime

def add_experience(task: str, agent: str, action: str, result: str, error: str = None, lesson: str = None):
    db_path = ROOT_DIR / "data" / "brain.db"
    conn = sqlite3.connect(str(db_path))
    try:
        exp_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO experiences (id, task, agent, action, result, error, lesson, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (exp_id, task, agent, action, result, error, lesson, datetime.utcnow().isoformat()))
        conn.commit()
        # Também adiciona à memória episódica
        content = f"TASK: {task} | AGENT: {agent} | ACTION: {action} | RESULT: {result} | ERROR: {error} | LESSON: {lesson}"
        memory_manager.add(content, type=MemoryType.EPISODIC, source=agent, confidence="medium")
        return exp_id
    finally:
        conn.close()

def search_experiences(query: str, limit: int = 5):
    db_path = ROOT_DIR / "data" / "brain.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("SELECT * FROM experiences WHERE task LIKE ? OR lesson LIKE ? ORDER BY created_at DESC LIMIT ?", (f"%{query}%", f"%{query}%", limit))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
