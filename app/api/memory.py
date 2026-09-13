"""
API Memory — GET /memory, POST /memory
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class MemoryCreate(BaseModel):
    content: str
    type: str = "short"
    source: Optional[str] = None
    mission_id: Optional[str] = None
    task_id: Optional[str] = None

@router.get("/memory")
def list_memory(query: str = "", type: str = None, limit: int = 20):
    from app.memory.manager import memory_manager
    if query:
        results = memory_manager.search(query, type=type, limit=limit)
    else:
        results = memory_manager.list_recent(limit=limit)
    return {"memories": results, "count": len(results)}

@router.post("/memory")
def create_memory(req: MemoryCreate):
    from app.memory.manager import memory_manager
    mem_id = memory_manager.add(content=req.content, type=req.type, source=req.source, mission_id=req.mission_id, task_id=req.task_id)
    return {"id": mem_id, "type": req.type, "content": req.content}

@router.get("/memory/episodic")
def get_episodic(query: str = "", limit: int = 10):
    from app.memory.episodic import search_experiences
    results = search_experiences(query, limit=limit)
    return {"experiences": results, "count": len(results)}
