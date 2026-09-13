"""Short term memory — wrapper"""
from app.memory.manager import memory_manager, MemoryType

def add_short(content: str, mission_id: str = None, task_id: str = None):
    return memory_manager.add(content, type=MemoryType.SHORT, mission_id=mission_id, task_id=task_id, expires_in_days=1)

def search_short(query: str, limit: int = 10):
    return memory_manager.search(query, type=MemoryType.SHORT, limit=limit)
