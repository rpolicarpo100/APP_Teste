from app.memory.manager import memory_manager, MemoryType

def add_long(content: str, source: str = None, mission_id: str = None):
    return memory_manager.add(content, type=MemoryType.LONG, source=source, mission_id=mission_id)

def search_long(query: str, limit: int = 10):
    return memory_manager.search(query, type=MemoryType.LONG, limit=limit)
