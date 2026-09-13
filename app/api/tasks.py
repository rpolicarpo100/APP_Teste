"""
API Tasks — Local AI Brain §18 + GOD Mission Intake
POST /tasks, GET /tasks, GET /tasks/{id}
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

router = APIRouter()

class TaskCreateRequest(BaseModel):
    objective: str
    expected_result: Optional[str] = None
    context: Dict[str, Any] = {}
    priority: str = "medium"
    autonomy_level: Optional[int] = None

class TaskCreateResponse(BaseModel):
    mission_id: str
    objective: str
    status: str
    tasks_created: int = 0

# Estas variáveis serão injectadas no main.py
_orchestrator = None

def set_orchestrator(orch):
    global _orchestrator
    _orchestrator = orch

@router.post("/tasks", response_model=TaskCreateResponse)
def create_task(request: TaskCreateRequest):
    if not _orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator não inicializado")
    mission = _orchestrator.create_mission(
        objective=request.objective,
        expected_result=request.expected_result,
        context=request.context,
        priority=request.priority,
        autonomy_level=request.autonomy_level
    )
    # Auto plan
    try:
        plan_res = _orchestrator.plan_mission(mission["id"])
        tasks_created = plan_res["tasks_created"]
    except Exception as e:
        tasks_created = 0

    return TaskCreateResponse(
        mission_id=mission["id"],
        objective=mission["objective"],
        status=mission["status"],
        tasks_created=tasks_created
    )

@router.get("/tasks")
def list_tasks(limit: int = 20):
    if not _orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator não inicializado")
    missions = _orchestrator.list_missions(limit=limit)
    return {"missions": missions, "count": len(missions)}

@router.get("/tasks/{mission_id}")
def get_task(mission_id: str):
    if not _orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator não inicializado")
    mission = _orchestrator.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Missão não encontrada")
    return mission

@router.post("/tasks/{mission_id}/run")
def run_task(mission_id: str):
    if not _orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator não inicializado")
    try:
        result = _orchestrator.run_mission(mission_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{mission_id}/plan")
def plan_task(mission_id: str):
    if not _orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator não inicializado")
    try:
        result = _orchestrator.plan_mission(mission_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
