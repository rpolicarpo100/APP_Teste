"""
Automation Agent — Local AI Brain spec
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput

class AutomationAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="automation", name="Automation Agent", specialty="Automação e workflows", version="1.0.0")
        self.skills = ["workflow_creation", "scheduling", "task_chaining"]
        self.tools = ["scheduler.create", "filesystem.read", "filesystem.write"]
        self.limitations = ["Não executa automação financeira sem aprovação", "Requer validação de cron"]

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = "RUNNING"
        try:
            from app.tools.registry import tool_registry
            scheduler_create = tool_registry.get_implementation("scheduler.create")

            objective = task_input.objective
            cron = task_input.context.get("cron", "0 9 * * *")  # default daily 9am
            evidence = []

            if scheduler_create and "agendar" in objective.lower() or "schedule" in objective.lower() or "todos os dias" in objective.lower():
                res = scheduler_create(name=objective, cron=cron, agent="research", payload=task_input.context)
                evidence.append({"type": "scheduler_create", "result": res})
                summary = f"Automação criada: {objective} com cron {cron} — {res}"
            else:
                summary = f"Workflow de automação planeado para: {objective}\nCron: {cron}\nPara activar, usar scheduler.create"

            self.status = "READY"
            return TaskOutput(task_id=task_input.task_id, status="completed", summary=summary, evidence=evidence, confidence="medium", requires_review=True)
        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(task_id=task_input.task_id, status="failed", summary=str(e), confidence="low", requires_review=True)
