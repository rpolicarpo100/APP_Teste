"""
Builder Agent — Constrói apps e sites reais via chat
GOD §4 + Local AI Brain — Especialidade construção
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput

class BuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="builder", name="Builder Agent", specialty="Construção de Apps e Sites", version="1.0.0")
        self.skills = ["site_building", "app_building", "frontend_dev", "ui_ux_implementation"]
        self.tools = ["site.builder", "filesystem.read", "filesystem.write", "filesystem.list"]
        self.limitations = ["Gera sites estáticos leves por defeito", "Para backend dinâmico requer aprovação"]

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = "RUNNING"
        try:
            valid, msg = self.validate_input(task_input)
            if not valid:
                return TaskOutput(task_id=task_input.task_id, status="failed", summary=f"Input inválido: {msg}", confidence="low", requires_review=True)

            objective = task_input.objective
            context = task_input.context
            style = context.get("style", "moderno minimalista")
            brand = context.get("brand", "BRAIN")

            from app.tools.registry import tool_registry
            site_builder = tool_registry.get_implementation("site.builder")

            evidence = []
            artifacts = []

            if site_builder:
                result = site_builder(objective=objective, style=style, brand=brand)
                evidence.append({"type": "site_builder", "result": result})
                if result.get("built"):
                    artifacts.append({
                        "type": "website",
                        "path": result.get("path"),
                        "filename": result.get("filename"),
                        "url": result.get("url"),
                        "preview_url": result.get("preview_url"),
                        "size": result.get("size")
                    })
                    summary = f"✅ Site/App construído com sucesso!\n\nObjectivo: {objective}\nEstilo: {style}\nFicheiro: {result.get('filename')}\nTamanho: {result.get('size')} bytes\nURL preview: {result.get('url')}\n\nO site é leve, bonito e 100% estático — abre em /workspace/{result.get('filename')}\n\n[Artefacto REAL] Ficheiro existe em {result.get('path')}"
                    self.status = "READY"
                    return TaskOutput(
                        task_id=task_input.task_id,
                        status="completed",
                        summary=summary,
                        artifacts=artifacts,
                        evidence=evidence,
                        confidence="high",
                        requires_review=False,
                        limitations=self.limitations
                    )
                else:
                    summary = f"Falha ao construir site: {result.get('error')}"
                    self.status = "FAILED"
                    return TaskOutput(task_id=task_input.task_id, status="failed", summary=summary, evidence=evidence, confidence="low", requires_review=True)
            else:
                return TaskOutput(task_id=task_input.task_id, status="failed", summary="Ferramenta site.builder não disponível — CAPACIDADE NÃO DISPONÍVEL", confidence="low", requires_review=True)

        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(task_id=task_input.task_id, status="failed", summary=f"Erro builder: {str(e)}", confidence="low", requires_review=True)
