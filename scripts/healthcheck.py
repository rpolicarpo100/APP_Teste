"""Healthcheck — verifica componentes"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.config.settings import settings
from app.models.ollama import ollama_client
from app.brain.state import can_transition_mission, can_transition_task, MissionState, TaskState

checks = []

# DB
try:
    from app.database.connection import get_engine
    engine = get_engine()
    checks.append(("database", True, f"Engine {engine}"))
except Exception as e:
    checks.append(("database", False, str(e)))

# Ollama
ollama_avail = ollama_client.is_available()
checks.append(("ollama", ollama_avail, f"Host {ollama_client.host} model {ollama_client.model} available={ollama_avail}"))

# State machine
try:
    assert can_transition_mission(MissionState.PENDING, MissionState.PLANNING)
    assert not can_transition_mission(MissionState.PENDING, MissionState.COMPLETED)
    assert can_transition_task(TaskState.PENDING, TaskState.READY)
    assert not can_transition_task(TaskState.PENDING, TaskState.SUCCEEDED)
    checks.append(("state_machine", True, "Transições validadas"))
except Exception as e:
    checks.append(("state_machine", False, str(e)))

# Agents
try:
    from app.brain.router import init_default_agents
    reg = init_default_agents()
    count = len(reg.list_agents())
    checks.append(("agents", count>=4, f"{count} agentes registados"))
except Exception as e:
    checks.append(("agents", False, str(e)))

# Tools
try:
    from app.tools.registry import tool_registry
    import app.tools.filesystem, app.tools.web, app.tools.python, app.tools.scheduler, app.tools.browser
    count = len(tool_registry.list_available())
    checks.append(("tools", count>=3, f"{count} ferramentas disponíveis"))
except Exception as e:
    checks.append(("tools", False, str(e)))

print("=== Healthcheck ===")
for name, ok, detail in checks:
    status = "✅" if ok else "❌"
    print(f"{status} {name}: {detail}")

all_ok = all(ok for _, ok, _ in checks)
sys.exit(0 if all_ok else 1)
