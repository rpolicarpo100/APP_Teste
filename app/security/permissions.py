"""
GOD Cerebro Core — Sistema de Permissões
Conforme GOD §9 e Local AI Brain §12-13, §19

Regra fundamental: LLM não controla directamente o computador. Brain decide.
"""
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Permission(str, Enum):
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    FILE_DELETE = "file.delete"
    WEB_SEARCH = "web.search"
    WEB_FETCH = "web.fetch"
    BROWSER_OPEN = "browser.open"
    BROWSER_CLICK = "browser.click"
    BROWSER_WRITE = "browser.write"
    PYTHON_EXEC = "python.execute"
    SHELL_EXEC = "shell.execute"
    MISSION_CREATE = "mission.create"
    MISSION_READ = "mission.read"
    TASK_EXECUTE = "task.execute"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    APPROVAL_REQUEST = "approval.request"

class ToolPermission(BaseModel):
    tool_id: str
    risk_level: RiskLevel
    required_permissions: List[Permission]
    requires_approval: bool
    allowed_paths: Optional[List[str]] = None
    autonomy_level_required: int = 0  # 0-4

# Catálogo inicial de permissões por ferramenta — VERIFICADO contra spec
TOOL_PERMISSIONS: Dict[str, ToolPermission] = {
    "filesystem.read": ToolPermission(
        tool_id="filesystem.read",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.FILE_READ],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "filesystem.write": ToolPermission(
        tool_id="filesystem.write",
        risk_level=RiskLevel.MEDIUM,
        required_permissions=[Permission.FILE_WRITE],
        requires_approval=False,
        autonomy_level_required=2
    ),
    "filesystem.list": ToolPermission(
        tool_id="filesystem.list",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.FILE_READ],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "filesystem.delete": ToolPermission(
        tool_id="filesystem.delete",
        risk_level=RiskLevel.HIGH,
        required_permissions=[Permission.FILE_DELETE],
        requires_approval=True,
        autonomy_level_required=3
    ),
    "web.search": ToolPermission(
        tool_id="web.search",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_SEARCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "web.fetch": ToolPermission(
        tool_id="web.fetch",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "browser.open": ToolPermission(
        tool_id="browser.open",
        risk_level=RiskLevel.MEDIUM,
        required_permissions=[Permission.BROWSER_OPEN],
        requires_approval=False,
        autonomy_level_required=2
    ),
    "python.execute": ToolPermission(
        tool_id="python.execute",
        risk_level=RiskLevel.HIGH,
        required_permissions=[Permission.PYTHON_EXEC],
        requires_approval=True,
        autonomy_level_required=3
    ),
    "shell.execute": ToolPermission(
        tool_id="shell.execute",
        risk_level=RiskLevel.HIGH,
        required_permissions=[Permission.SHELL_EXEC],
        requires_approval=True,
        autonomy_level_required=4
    ),
    "mission.store": ToolPermission(
        tool_id="mission.store",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.MISSION_CREATE, Permission.MEMORY_WRITE],
        requires_approval=False,
        autonomy_level_required=0
    ),
    "scheduler.create": ToolPermission(
        tool_id="scheduler.create",
        risk_level=RiskLevel.MEDIUM,
        required_permissions=[Permission.TASK_EXECUTE],
        requires_approval=False,
        autonomy_level_required=2
    ),
    "scheduler.list": ToolPermission(
        tool_id="scheduler.list",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.TASK_EXECUTE],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "browser.screenshot": ToolPermission(
        tool_id="browser.screenshot",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.BROWSER_OPEN],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "site.builder": ToolPermission(
        tool_id="site.builder",
        risk_level=RiskLevel.MEDIUM,
        required_permissions=[Permission.FILE_WRITE],
        requires_approval=False,
        autonomy_level_required=2
    ),
    # News tools — REAL e FIÁVEIS
    "news.portugal": ToolPermission(
        tool_id="news.portugal",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "news.world": ToolPermission(
        tool_id="news.world",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "news.markets": ToolPermission(
        tool_id="news.markets",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "news.crypto": ToolPermission(
        tool_id="news.crypto",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "news.all": ToolPermission(
        tool_id="news.all",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    # Market data — REAL e FIÁVEIS
    "crypto.markets": ToolPermission(
        tool_id="crypto.markets",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "crypto.gainers_losers": ToolPermission(
        tool_id="crypto.gainers_losers",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "stocks.markets": ToolPermission(
        tool_id="stocks.markets",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "stocks.gainers_losers": ToolPermission(
        tool_id="stocks.gainers_losers",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
    "dashboard.market_overview": ToolPermission(
        tool_id="dashboard.market_overview",
        risk_level=RiskLevel.LOW,
        required_permissions=[Permission.WEB_FETCH],
        requires_approval=False,
        autonomy_level_required=1
    ),
}

class AgentPermissions(BaseModel):
    agent_id: str
    allowed_tools: List[str]
    allowed_permissions: List[Permission]
    max_autonomy_level: int
    can_request_approval: bool = True

# Permissões por agente-piloto
AGENT_PERMISSIONS: Dict[str, AgentPermissions] = {
    "research": AgentPermissions(
        agent_id="research",
        allowed_tools=["filesystem.read", "web.search", "web.fetch", "mission.store", "news.portugal", "news.world", "news.markets", "news.crypto", "news.all", "crypto.markets", "crypto.gainers_losers", "stocks.markets", "stocks.gainers_losers", "dashboard.market_overview"],
        allowed_permissions=[Permission.FILE_READ, Permission.WEB_SEARCH, Permission.WEB_FETCH, Permission.MEMORY_READ, Permission.MEMORY_WRITE],
        max_autonomy_level=2
    ),
    "coding_qa": AgentPermissions(
        agent_id="coding_qa",
        allowed_tools=["filesystem.read", "filesystem.write", "filesystem.list", "python.execute", "mission.store", "site.builder"],
        allowed_permissions=[Permission.FILE_READ, Permission.FILE_WRITE, Permission.PYTHON_EXEC, Permission.MISSION_READ, Permission.TASK_EXECUTE],
        max_autonomy_level=2
    ),
    "design": AgentPermissions(
        agent_id="design",
        allowed_tools=["filesystem.read", "filesystem.write", "web.search", "mission.store", "site.builder"],
        allowed_permissions=[Permission.FILE_READ, Permission.FILE_WRITE, Permission.WEB_SEARCH, Permission.MEMORY_WRITE],
        max_autonomy_level=2
    ),
    "builder": AgentPermissions(
        agent_id="builder",
        allowed_tools=["filesystem.read", "filesystem.write", "filesystem.list", "site.builder", "mission.store"],
        allowed_permissions=[Permission.FILE_READ, Permission.FILE_WRITE, Permission.MISSION_READ, Permission.TASK_EXECUTE, Permission.MEMORY_WRITE],
        max_autonomy_level=2
    ),
    "business": AgentPermissions(
        agent_id="business",
        allowed_tools=["filesystem.read", "web.search", "web.fetch", "mission.store"],
        allowed_permissions=[Permission.FILE_READ, Permission.WEB_SEARCH, Permission.WEB_FETCH, Permission.MEMORY_READ],
        max_autonomy_level=2
    ),
    "browser": AgentPermissions(
        agent_id="browser",
        allowed_tools=["browser.open", "web.fetch", "filesystem.read", "filesystem.write"],
        allowed_permissions=[Permission.BROWSER_OPEN, Permission.BROWSER_CLICK, Permission.WEB_FETCH, Permission.FILE_READ],
        max_autonomy_level=2
    ),
    "automation": AgentPermissions(
        agent_id="automation",
        allowed_tools=["filesystem.read", "filesystem.write", "filesystem.list", "python.execute", "mission.store", "scheduler.create", "scheduler.list"],
        allowed_permissions=[Permission.FILE_READ, Permission.FILE_WRITE, Permission.TASK_EXECUTE, Permission.MEMORY_WRITE],
        max_autonomy_level=3
    ),
    "monitor": AgentPermissions(
        agent_id="monitor",
        allowed_tools=["filesystem.read", "filesystem.list", "web.fetch", "mission.store"],
        allowed_permissions=[Permission.FILE_READ, Permission.WEB_FETCH, Permission.MEMORY_READ],
        max_autonomy_level=2
    ),
}

def check_permission(agent_id: str, tool_id: str, autonomy_level: int = 0) -> tuple[bool, str]:
    """
    Verifica se agente pode usar ferramenta.
    Retorna (permitido, motivo)
    Regra: LLM pede, Brain decide.
    """
    agent_perm = AGENT_PERMISSIONS.get(agent_id)
    if not agent_perm:
        return False, f"Agente {agent_id} não registado"

    tool_perm = TOOL_PERMISSIONS.get(tool_id)
    if not tool_perm:
        return False, f"Ferramenta {tool_id} não registada"

    if tool_id not in agent_perm.allowed_tools:
        return False, f"Agente {agent_id} não tem permissão para ferramenta {tool_id}"

    if autonomy_level < tool_perm.autonomy_level_required:
        return False, f"Nível de autonomia {autonomy_level} insuficiente, requer {tool_perm.autonomy_level_required} para {tool_id}"

    if agent_perm.max_autonomy_level < tool_perm.autonomy_level_required:
        return False, f"Agente {agent_id} max autonomy {agent_perm.max_autonomy_level} < required {tool_perm.autonomy_level_required}"

    # Verifica permissões individuais
    for req_perm in tool_perm.required_permissions:
        if req_perm not in agent_perm.allowed_permissions:
            return False, f"Agente {agent_id} falta permissão {req_perm}"

    return True, "Permitido"

def requires_approval(tool_id: str) -> bool:
    perm = TOOL_PERMISSIONS.get(tool_id)
    if not perm:
        return True  # por defeito, exige aprovação se desconhecida
    return perm.requires_approval

def get_risk_level(tool_id: str) -> RiskLevel:
    perm = TOOL_PERMISSIONS.get(tool_id)
    if not perm:
        return RiskLevel.HIGH
    return perm.risk_level
