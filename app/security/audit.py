"""
Audit logging — GOD §5.7 e Local AI Brain §22
"""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime
import json
import logging
from pathlib import Path

from app.config.settings import settings, ROOT_DIR

class EventType(str, Enum):
    TaskCreated = "TaskCreated"
    TaskStarted = "TaskStarted"
    AgentStarted = "AgentStarted"
    ToolCalled = "ToolCalled"
    ToolCompleted = "ToolCompleted"
    ApprovalRequested = "ApprovalRequested"
    ApprovalGranted = "ApprovalGranted"
    ApprovalDenied = "ApprovalDenied"
    AgentCompleted = "AgentCompleted"
    TaskCompleted = "TaskCompleted"
    TaskFailed = "TaskFailed"
    MemoryUpdated = "MemoryUpdated"
    MissionCreated = "MissionCreated"
    MissionStateChanged = "MissionStateChanged"
    TaskStateChanged = "TaskStateChanged"
    PermissionDenied = "PermissionDenied"
    SecurityViolation = "SecurityViolation"

class AuditLog(BaseModel):
    id: str
    timestamp: datetime
    event_type: EventType
    mission_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    tool_id: Optional[str] = None
    actor: str
    details: Dict[str, Any] = {}
    severity: str = "INFO"

    @classmethod
    def create(cls, event_type: EventType, actor: str, mission_id: str = None, task_id: str = None, agent_id: str = None, tool_id: str = None, details: dict = None, severity: str = "INFO"):
        return cls(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            mission_id=mission_id,
            task_id=task_id,
            agent_id=agent_id,
            tool_id=tool_id,
            actor=actor,
            details=details or {},
            severity=severity
        )

class AuditManager:
    def __init__(self):
        self._logs: list[AuditLog] = []
        # Setup file logger
        log_path = ROOT_DIR / settings.log_path / "audit.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_logger = logging.getLogger("audit")
        if not self.file_logger.handlers:
            handler = logging.FileHandler(log_path)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.file_logger.addHandler(handler)
            self.file_logger.setLevel(logging.INFO)

    def log(self, entry: AuditLog):
        self._logs.append(entry)
        # Evita guardar secrets
        safe_details = {k: v for k, v in entry.details.items() if "password" not in k.lower() and "token" not in k.lower() and "secret" not in k.lower()}
        self.file_logger.info(f"{entry.event_type} actor={entry.actor} mission={entry.mission_id} task={entry.task_id} agent={entry.agent_id} tool={entry.tool_id} details={json.dumps(safe_details)[:500]}")

    def get_by_mission(self, mission_id: str):
        return [l for l in self._logs if l.mission_id == mission_id]

    def get_by_task(self, task_id: str):
        return [l for l in self._logs if l.task_id == task_id]

    def get_all(self):
        return self._logs

audit_manager = AuditManager()
