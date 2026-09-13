"""
Sistema de aprovação — Local AI Brain §16, GOD §9
"""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"

class ApprovalRequest(BaseModel):
    id: str
    task_id: str
    mission_id: str
    agent_id: str
    tool_id: str
    action: str
    target: Optional[str] = None
    risk: str = "MEDIUM"
    payload: Dict[str, Any] = {}
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: datetime = datetime.utcnow()
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    @classmethod
    def create(cls, task_id: str, mission_id: str, agent_id: str, tool_id: str, action: str, target: str = None, risk: str = "MEDIUM", payload: dict = None):
        return cls(
            id=str(uuid.uuid4()),
            task_id=task_id,
            mission_id=mission_id,
            agent_id=agent_id,
            tool_id=tool_id,
            action=action,
            target=target,
            risk=risk,
            payload=payload or {}
        )

class ApprovalManager:
    """Gestor de aprovações em memória para MVP — depois persistido em SQLite"""
    def __init__(self):
        self._approvals: Dict[str, ApprovalRequest] = {}

    def request(self, approval: ApprovalRequest) -> ApprovalRequest:
        self._approvals[approval.id] = approval
        return approval

    def approve(self, approval_id: str, resolved_by: str = "user") -> Optional[ApprovalRequest]:
        ap = self._approvals.get(approval_id)
        if not ap:
            return None
        ap.status = ApprovalStatus.APPROVED
        ap.resolved_at = datetime.utcnow()
        ap.resolved_by = resolved_by
        return ap

    def deny(self, approval_id: str, resolved_by: str = "user") -> Optional[ApprovalRequest]:
        ap = self._approvals.get(approval_id)
        if not ap:
            return None
        ap.status = ApprovalStatus.DENIED
        ap.resolved_at = datetime.utcnow()
        ap.resolved_by = resolved_by
        return ap

    def get(self, approval_id: str) -> Optional[ApprovalRequest]:
        return self._approvals.get(approval_id)

    def list_pending(self):
        return [a for a in self._approvals.values() if a.status == ApprovalStatus.PENDING]

    def list_all(self):
        return list(self._approvals.values())

# Singleton para MVP
approval_manager = ApprovalManager()
