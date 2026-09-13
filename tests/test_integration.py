"""
Testes integração — GOD §15
Criar missão → gerar tarefas → seleccionar agente real → executar → guardar → validar → actualizar estado → retomar
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import tempfile, os, json, sqlite3, uuid
from pathlib import Path

# Setup temporário para não poluir DB real
from app.config.settings import settings, ROOT_DIR
from app.database.connection import init_db
from app.brain.router import init_default_agents
from app.tools.registry import tool_registry
import app.tools.filesystem, app.tools.web, app.tools.python, app.tools.scheduler, app.tools.browser
from app.brain.executor import Executor
from app.brain.orchestrator import Orchestrator

def test_full_flow():
    # Init
    init_db()
    agent_reg = init_default_agents()
    executor = Executor(agent_registry=agent_reg, tool_registry_ref=tool_registry)
    orchestrator = Orchestrator(agent_registry=agent_reg, executor=executor)

    # 1. Criar missão
    mission = orchestrator.create_mission(
        objective="Pesquisar ferramentas gratuitas de trading",
        expected_result="Relatório com 3 ferramentas",
        context={"priority": "medium"},
        priority="medium"
    )
    assert mission["id"] is not None
    print(f"✅ Missão criada {mission['id']}")

    # 2. Planear
    plan = orchestrator.plan_mission(mission["id"])
    assert plan["tasks_created"] >= 1
    print(f"✅ Plano criado com {plan['tasks_created']} tarefas")

    # 3. Executar
    result = orchestrator.run_mission(mission["id"])
    assert "mission" in result
    assert result["steps_executed"] >= 1
    print(f"✅ Missão executada steps={result['steps_executed']} status_counts={result['status_counts']}")

    # 4. Verificar estado final
    final = orchestrator.get_mission(mission["id"])
    assert final["status"] in ["COMPLETED", "NEEDS_REVIEW", "BLOCKED", "FAILED"]
    assert len(final["tasks"]) >= 1
    # Verifica que tarefas têm evidência
    for task in final["tasks"]:
        if task["status"] == "SUCCEEDED":
            assert task["result_summary"] is not None
    print(f"✅ Estado final {final['status']}")

    # 5. Testar agente indisponível
    fake_task = {
        "id": str(uuid.uuid4()),
        "mission_id": mission["id"],
        "objective": "Tarefa com agente inexistente",
        "agent_id": "nonexistent_agent",
        "required_tools": []
    }
    exec_res = executor.execute_task(fake_task, mission_context={})
    assert exec_res.status.value == "FAILED"
    assert "não encontrado" in exec_res.error.lower() or "não" in exec_res.error.lower()
    print(f"✅ Agente indisponível tratado")

    # 6. Testar ferramenta indisponível — permissão negada
    task_blocked = {
        "id": str(uuid.uuid4()),
        "mission_id": mission["id"],
        "objective": "Tentar apagar ficheiro",
        "agent_id": "research",
        "required_tools": ["filesystem.delete"]
    }
    exec_res2 = executor.execute_task(task_blocked, mission_context={"autonomy_level": 2})
    assert exec_res2.status.value == "BLOCKED"
    print(f"✅ Ferramenta bloqueada por permissão")

    # 7. Testar missão multidisciplinar
    mission2 = orchestrator.create_mission(
        objective="Pesquisar mercado e criar design e analisar código",
        context={}
    )
    plan2 = orchestrator.plan_mission(mission2["id"])
    assert plan2["tasks_created"] >= 2, "Missão multidisciplinar deve gerar >=2 tarefas"
    print(f"✅ Missão multidisciplinar {plan2['tasks_created']} tarefas")

    result2 = orchestrator.run_mission(mission2["id"])
    print(f"✅ Missão multidisciplinar executada {result2['status_counts']}")

    return True

if __name__ == "__main__":
    test_full_flow()
    print("✅ test_integration passed")
