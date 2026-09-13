"""Setup script"""
from pathlib import Path
import sys
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.config.settings import settings
from app.database.connection import init_db
from app.brain.router import init_default_agents
from app.tools.registry import tool_registry
import app.tools.filesystem, app.tools.web, app.tools.python, app.tools.scheduler, app.tools.browser

print("=== GOD Cerebro Core Setup ===")
print(f"Resolving paths...")
settings.resolve_paths()
print(f"Init DB...")
init_db()
print(f"Init agents...")
registry = init_default_agents()
print(f"Agents: {[a.agent_id for a in registry.list_agents()]}")
print(f"Tools: {[t.id for t in tool_registry.list_available()]}")
print("Setup OK")
