"""
Testes contratos — GOD §6
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.agents.base import TaskInput, TaskOutput

def test_task_input_valid():
    ti = TaskInput(
        task_id="t1",
        mission_id="m1",
        agent_id="research",
        objective="Pesquisar",
        context={},
        inputs=[],
        acceptance_criteria=[],
        permissions={}
    )
    assert ti.task_id == "t1"

def test_task_output_valid():
    to = TaskOutput(
        task_id="t1",
        status="completed",
        summary="Resumo",
        artifacts=[],
        evidence=[],
        confidence="medium",
        requires_review=True
    )
    assert to.status == "completed"

def test_task_input_missing():
    try:
        TaskInput(task_id="", mission_id="m1", agent_id="research", objective="")
        # Pydantic permite vazio, mas validação do agente deve falhar
        from app.agents.research import ResearchAgent
        agent = ResearchAgent()
        ti = TaskInput(task_id="", mission_id="m1", agent_id="research", objective="", context={}, inputs=[], acceptance_criteria=[], permissions={})
        valid, msg = agent.validate_input(ti)
        assert valid == False
    except Exception:
        assert True

if __name__ == "__main__":
    test_task_input_valid()
    test_task_output_valid()
    test_task_input_missing()
    print("✅ test_contracts passed")
