"""
Semantic memory — para V1.1 com embeddings. MVP: busca textual simples.
Local AI Brain §14
"""
from app.memory.manager import memory_manager, MemoryType

def add_semantic(content: str, source: str = None):
    return memory_manager.add(content, type=MemoryType.SEMANTIC, source=source, confidence="high")

def search_semantic(query: str, limit: int = 10):
    # MVP: busca textual. Futuro: embeddings
    return memory_manager.search(query, type=MemoryType.SEMANTIC, limit=limit)
