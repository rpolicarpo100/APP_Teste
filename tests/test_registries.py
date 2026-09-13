"""
Testes registries — Agent + Tool
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.brain.router import AgentRegistry, init_default_agents
from app.tools.registry import ToolRegistry, tool_registry
import app.tools.filesystem, app.tools.web, app.tools.python, app.tools.scheduler, app.tools.browser

def test_agent_registry():
    reg = AgentRegistry()
    from app.agents.research import ResearchAgent
    agent = ResearchAgent()
    reg.register(agent)
    assert reg.get("research") is not None
    assert reg.get("nonexistent") is None
    assert len(reg.list_agents()) == 1

def test_default_agents():
    reg = init_default_agents()
    agents = reg.list_agents()
    assert len(agents) >= 4, f"Esperado >=4 agentes-piloto, obtido {len(agents)}"
    ids = [a.agent_id for a in agents]
    assert "research" in ids
    assert "coding_qa" in ids
    assert "design" in ids
    assert "business" in ids

def test_tool_registry():
    # tool_registry já tem ferramentas registadas via import
    available = tool_registry.list_available()
    assert len(available) >= 3
    assert tool_registry.is_available("filesystem.read")
    assert not tool_registry.is_available("nonexistent.tool")

def test_tool_implementation_exists():
    impl = tool_registry.get_implementation("filesystem.read")
    assert callable(impl), "Implementação deve ser callable — CAPACIDADE NÃO DISPONÍVEL se não for"

if __name__ == "__main__":
    test_agent_registry()
    test_default_agents()
    test_tool_registry()
    test_tool_implementation_exists()
    print("✅ test_registries passed")
