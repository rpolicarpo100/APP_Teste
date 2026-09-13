"""
API Agents — GET /agents, POST /agents/{id}/run
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter()

_agent_registry = None

def set_agent_registry(registry):
    global _agent_registry
    _agent_registry = registry

@router.get("/agents")
def list_agents():
    if not _agent_registry:
        raise HTTPException(status_code=500, detail="Agent registry não inicializado")
    agents = _agent_registry.list_agents()
    return {"agents": [a.get_info() for a in agents], "count": len(agents)}

@router.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    if not _agent_registry:
        raise HTTPException(status_code=500, detail="Agent registry não inicializado")
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    return agent.get_info()

class AgentRunRequest(BaseModel):
    objective: str
    context: Dict[str, Any] = {}
    inputs: List[Dict[str, Any]] = []

@router.post("/agents/{agent_id}/run")
def run_agent(agent_id: str, request: AgentRunRequest):
    if not _agent_registry:
        raise HTTPException(status_code=500, detail="Agent registry não inicializado")
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")

    from app.agents.base import TaskInput
    import uuid

    task_input = TaskInput(
        task_id=str(uuid.uuid4()),
        mission_id="direct-run",
        agent_id=agent_id,
        objective=request.objective,
        context=request.context,
        inputs=request.inputs,
        acceptance_criteria=[],
        permissions={}
    )

    try:
        output = agent.execute(task_input)
        return output.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
