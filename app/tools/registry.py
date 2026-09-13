"""
Tool Registry — GOD §5.4 e Local AI Brain §11
Catálogo de ferramentas reais com implementação verificável.
"""
from typing import Dict, Optional, Callable, Any
from pydantic import BaseModel
from enum import Enum
import uuid

class ToolStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"

class ToolDefinition(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    description: str
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    status: ToolStatus = ToolStatus.AVAILABLE
    requires_approval: bool = False
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    implementation: Optional[str] = None  # path to function for traceability

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._implementations: Dict[str, Callable] = {}

    def register(self, definition: ToolDefinition, implementation: Callable):
        """Regista ferramenta com implementação verificável"""
        if not callable(implementation):
            raise ValueError(f"Implementação da ferramenta {definition.id} não é callable — CAPACIDADE NÃO DISPONÍVEL")
        self._tools[definition.id] = definition
        self._implementations[definition.id] = implementation

    def get(self, tool_id: str) -> Optional[ToolDefinition]:
        return self._tools.get(tool_id)

    def get_implementation(self, tool_id: str) -> Optional[Callable]:
        return self._implementations.get(tool_id)

    def list_available(self):
        return [t for t in self._tools.values() if t.status == ToolStatus.AVAILABLE]

    def list_all(self):
        return list(self._tools.values())

    def is_available(self, tool_id: str) -> bool:
        tool = self._tools.get(tool_id)
        if not tool:
            return False
        return tool.status == ToolStatus.AVAILABLE

    def set_status(self, tool_id: str, status: ToolStatus):
        if tool_id in self._tools:
            self._tools[tool_id].status = status

# Singleton
tool_registry = ToolRegistry()

def register_tool(id: str, name: str, description: str, risk_level: str = "LOW", requires_approval: bool = False, input_schema: dict = None, output_schema: dict = None):
    """Decorator para registar ferramentas"""
    def decorator(func: Callable):
        definition = ToolDefinition(
            id=id,
            name=name,
            description=description,
            risk_level=risk_level,
            requires_approval=requires_approval,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            implementation=f"{func.__module__}.{func.__name__}"
        )
        tool_registry.register(definition, func)
        return func
    return decorator
