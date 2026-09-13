"""
Monitor Agent — Local AI Brain spec
Verificações periódicas
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput
import time

class MonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="monitor", name="Monitor Agent", specialty="Monitorização", version="1.0.0")
        self.skills = ["health_check", "log_analysis", "alerting"]
        self.tools = ["filesystem.read", "web.fetch"]
        self.limitations = ["Apenas leitura", "Não toma acções correctivas sem aprovação"]

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = "RUNNING"
        try:
            from app.tools.registry import tool_registry
            fs_list = tool_registry.get_implementation("filesystem.list")

            objective = task_input.objective
            evidence = []

            # Health check básico
            checks = []
            # Verifica se DB existe
            from pathlib import Path
            from app.config.settings import settings, ROOT_DIR
            db_path = ROOT_DIR / "data" / "brain.db"
            checks.append({"check": "database_exists", "exists": db_path.exists(), "path": str(db_path)})

            # Verifica workspace
            ws_path = ROOT_DIR / settings.workspace_path
            checks.append({"check": "workspace_exists", "exists": ws_path.exists()})

            # Lista logs
            if fs_list:
                logs = fs_list("logs")
                evidence.append({"type": "logs_list", "count": logs.get("count", 0)})

            summary = f"Monitorização: {objective}\n"
            for c in checks:
                summary += f"- {c['check']}: {c['exists']}\n"

            self.status = "READY"
            return TaskOutput(task_id=task_input.task_id, status="completed", summary=summary, evidence=evidence + checks, confidence="high", requires_review=False)
        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(task_id=task_input.task_id, status="failed", summary=str(e), confidence="low", requires_review=True)
