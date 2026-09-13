"""
Browser Agent — Local AI Brain spec
Usa Playwright quando disponível
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput

class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="browser", name="Browser Agent", specialty="Automação browser", version="1.0.0")
        self.skills = ["web_navigation", "form_filling", "data_extraction", "screenshot"]
        self.tools = ["browser.open", "web.fetch", "filesystem.write"]
        self.limitations = ["Requer Playwright instalado", "Não submete formulários sem aprovação"]

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = "RUNNING"
        try:
            from app.tools.registry import tool_registry
            browser_open = tool_registry.get_implementation("browser.open")
            web_fetch = tool_registry.get_implementation("web.fetch")

            objective = task_input.objective
            url = task_input.context.get("url") or (task_input.inputs[0].get("url") if task_input.inputs else None)

            evidence = []
            if not url:
                return TaskOutput(task_id=task_input.task_id, status="failed", summary="URL não fornecida para browser agent", confidence="low", requires_review=True)

            if browser_open:
                res = browser_open(url)
                evidence.append({"type": "browser_open", "url": url, "result": res})
                summary = f"Browser: tentativa de abrir {url}\nResultado: {res.get('error', 'OK') if 'error' in res else 'Conteúdo obtido'}"
            elif web_fetch:
                res = web_fetch(url)
                evidence.append({"type": "web_fetch_fallback", "url": url, "length": res.get("length")})
                summary = f"Browser fallback via web.fetch para {url} — {res.get('length', 0)} chars"
            else:
                summary = f"CAPACIDADE NÃO DISPONÍVEL — browser tools não registadas"

            self.status = "READY"
            return TaskOutput(task_id=task_input.task_id, status="completed", summary=summary, evidence=evidence, confidence="medium", requires_review=True, limitations=self.limitations)
        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(task_id=task_input.task_id, status="failed", summary=str(e), confidence="low", requires_review=True)
