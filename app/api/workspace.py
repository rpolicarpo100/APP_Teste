"""
Workspace API — ranking após sessão fechada, deploy se tiver info + persistência Supabase/R2/GitHub
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.tools.workspace_ranking import workspace_ranking, workspace_cleanup
from app.tools.deploy import site_deploy, session_close, _get_available_platforms
from app.tools.persistent_storage import workspace_persist, workspace_persist_status

router = APIRouter()

class DeployRequest(BaseModel):
    filename: str
    platform: str = "auto"
    message: str = "Deploy via Builder"

class SessionCloseRequest(BaseModel):
    session_id: Optional[str] = None
    auto_cleanup: bool = False

class PersistRequest(BaseModel):
    filename: Optional[str] = None
    all: bool = False

@router.get("/workspace/ranking")
def get_ranking():
    """Analisa workspace do utilizador, dá ranking 0-100, se bom guarda se não esquece"""
    result = workspace_ranking()
    return result

@router.post("/workspace/ranking")
def post_ranking(session_id: Optional[str] = None):
    result = workspace_ranking(session_id=session_id)
    return result

@router.post("/workspace/cleanup")
def cleanup_workspace(min_score: int = 70, dry_run: bool = True):
    """Após ranking, se mau esquece totalmente (apaga ficheiros maus)"""
    result = workspace_cleanup(min_score=min_score, dry_run=dry_run)
    return result

@router.get("/workspace/deploy/platforms")
def get_deploy_platforms():
    """Lista plataformas de deploy disponíveis (se tem token)"""
    platforms = _get_available_platforms()
    return {
        "available": platforms,
        "has_info": len(platforms) > 0,
        "can_deploy": len(platforms) > 0,
        "how_to": "Adiciona NETLIFY_TOKEN (free) em Render env vars para deploy Netlify, ou VERCEL_TOKEN para Vercel, ou GITHUB_TOKEN para GitHub Pages",
        "message": f"Builder tem workspace limitado, mas é capaz de fazer deploy se tiver a info — plataformas disponíveis: {platforms}" if platforms else "Sem info de deploy — adiciona NETLIFY_TOKEN"
    }

@router.post("/workspace/deploy")
def deploy_site(req: DeployRequest):
    """Faz deploy do site se tiver info"""
    result = site_deploy(filename=req.filename, platform=req.platform, message=req.message)
    return result

@router.get("/workspace/persist/status")
def persist_status():
    """Status persistência — Supabase 1GB free + R2 10GB free + GitHub Pages"""
    return workspace_persist_status()

@router.post("/workspace/persist")
def persist_workspace(req: PersistRequest):
    """Persiste workspace em Supabase 1GB free ou R2 10GB free ou GitHub Pages gh-pages"""
    result = workspace_persist(filename=req.filename, all=req.all)
    return result

@router.get("/workspace/persist")
def persist_workspace_get(filename: Optional[str] = None, all: bool = False):
    result = workspace_persist(filename=filename, all=all)
    return result

@router.post("/session/close")
def close_session(req: SessionCloseRequest):
    """
    Após sessão fechada, workspace do utilizador é analisado dado 1 ranking,
    se for algo bom guardar se não esquecer totalmente
    """
    result = session_close(session_id=req.session_id, auto_cleanup=req.auto_cleanup)
    return result

@router.get("/session/close/{session_id}")
def close_session_get(session_id: str, auto_cleanup: bool = False):
    result = session_close(session_id=session_id, auto_cleanup=auto_cleanup)
    return result
