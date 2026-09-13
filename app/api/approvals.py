"""
API Approvals — GET /approvals, POST /approvals/{id}/approve|deny
Local AI Brain §16
"""
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/approvals")
def list_approvals(status: str = None):
    from app.security.approval import approval_manager
    if status == "pending":
        approvals = approval_manager.list_pending()
    else:
        approvals = approval_manager.list_all()
    return {"approvals": [a.model_dump() for a in approvals], "count": len(approvals)}

@router.get("/approvals/{approval_id}")
def get_approval(approval_id: str):
    from app.security.approval import approval_manager
    ap = approval_manager.get(approval_id)
    if not ap:
        raise HTTPException(status_code=404, detail="Approval não encontrada")
    return ap.model_dump()

@router.post("/approvals/{approval_id}/approve")
def approve(approval_id: str, resolved_by: str = "user"):
    from app.security.approval import approval_manager
    from app.security.audit import audit_manager, AuditLog, EventType
    ap = approval_manager.approve(approval_id, resolved_by=resolved_by)
    if not ap:
        raise HTTPException(status_code=404, detail="Approval não encontrada")
    audit_manager.log(AuditLog.create(event_type=EventType.ApprovalGranted, actor=resolved_by, details={"approval_id": approval_id}))
    return ap.model_dump()

@router.post("/approvals/{approval_id}/deny")
def deny(approval_id: str, resolved_by: str = "user"):
    from app.security.approval import approval_manager
    from app.security.audit import audit_manager, AuditLog, EventType
    ap = approval_manager.deny(approval_id, resolved_by=resolved_by)
    if not ap:
        raise HTTPException(status_code=404, detail="Approval não encontrada")
    audit_manager.log(AuditLog.create(event_type=EventType.ApprovalDenied, actor=resolved_by, details={"approval_id": approval_id}))
    return ap.model_dump()
