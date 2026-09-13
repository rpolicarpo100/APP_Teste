"""
Research Agent — GOD §4.1 + Local AI Brain Research Agent
Responsabilidades: pesquisar questões complexas, elaborar planos, analisar documentos, distinguir factos
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput
from typing import List
import json

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="research", name="Research Agent", specialty="Investigação profunda", version="1.0.0")
        self.skills = ["deep_research", "source_analysis", "fact_checking", "report_writing", "evidence_collection"]
        self.tools = ["web.search", "web.fetch", "filesystem.read", "filesystem.write"]
        self.limitations = ["Não tem acesso a APIs pagas sem configuração", "Pesquisa web depende de disponibilidade externa"]

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = "RUNNING"
        try:
            valid, msg = self.validate_input(task_input)
            if not valid:
                return TaskOutput(
                    task_id=task_input.task_id,
                    status="failed",
                    summary=f"Input inválido: {msg}",
                    confidence="low",
                    requires_review=True,
                    limitations=self.limitations
                )

            # Extrai contexto
            objective = task_input.objective
            context = task_input.context

            # Tenta usar ferramentas reais
            evidence = []
            artifacts = []
            summary_parts = []

            # Se houver inputs com URLs, faz fetch
            from app.tools.registry import tool_registry
            web_search = tool_registry.get_implementation("web.search")
            web_fetch = tool_registry.get_implementation("web.fetch")
            fs_read = tool_registry.get_implementation("filesystem.read")

            # Pesquisa
            if web_search:
                search_result = web_search(objective, count=5)
                evidence.append({"type": "web_search", "query": objective, "result": search_result})
                if search_result.get("results"):
                    summary_parts.append(f"Pesquisa encontrou {len(search_result['results'])} resultados.")
                    for r in search_result["results"][:3]:
                        summary_parts.append(f"- {r.get('title')}: {r.get('url')}")
                else:
                    summary_parts.append(f"Pesquisa web: {search_result.get('limitation', 'sem resultados')}")

            # Se contexto tiver files, lê
            if context.get("files"):
                for file_path in context["files"]:
                    if fs_read:
                        read_res = fs_read(file_path)
                        evidence.append({"type": "file_read", "path": file_path, "result": read_res})
                        if read_res.get("content"):
                            summary_parts.append(f"Documento {file_path} analisado ({read_res.get('size', 0)} chars)")

            # Se inputs tiver URLs
            for inp in task_input.inputs:
                if inp.get("type") == "url" and web_fetch:
                    fetch_res = web_fetch(inp.get("url"))
                    evidence.append({"type": "web_fetch", "url": inp.get("url"), "result": {"length": fetch_res.get("length"), "status": fetch_res.get("status_code")}})
                    if fetch_res.get("content"):
                        summary_parts.append(f"URL {inp.get('url')} fetched ({fetch_res.get('length')} chars)")

            # Produz relatório estruturado — distingue factos de hipóteses
            summary = f"Investigação sobre: {objective}\n\n"
            summary += "\n".join(summary_parts) if summary_parts else "Análise inicial concluída com base no objectivo fornecido."
            summary += "\n\n[Factos Verificados]\n"
            summary += f"- Objectivo: {objective}\n"
            summary += f"- Contexto fornecido: {json.dumps(context, ensure_ascii=False)[:500]}\n"
            summary += "\n[Limitações]\n- " + "\n- ".join(self.limitations)
            summary += "\n\n[Confiança] medium — requer validação cruzada de fontes independentes."

            self.status = "READY"
            return TaskOutput(
                task_id=task_input.task_id,
                status="completed",
                summary=summary,
                artifacts=artifacts,
                evidence=evidence,
                confidence="medium",
                requires_review=True,
                limitations=self.limitations,
                next_recommendations=["Validar fontes independentes", "Comparar informação com documentos locais"]
            )
        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(
                task_id=task_input.task_id,
                status="failed",
                summary=f"Erro na investigação: {str(e)}",
                confidence="low",
                requires_review=True,
                limitations=self.limitations + [str(e)]
            )
