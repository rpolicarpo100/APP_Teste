"""
Coding & QA Agent — GOD §4.2
Responsabilidades: inspeccionar código, diagnosticar erros, propor alterações, executar testes, rever código
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput
import os
import subprocess
from pathlib import Path

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="coding_qa", name="Coding & QA Agent", specialty="Coding e QA", version="1.0.0")
        self.skills = ["code_inspection", "debugging", "testing", "refactoring", "code_review"]
        self.tools = ["filesystem.read", "filesystem.write", "filesystem.list", "python.execute"]
        self.limitations = ["Não faz deploy automático sem aprovação", "Não altera branch principal sem autorização"]

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = "RUNNING"
        try:
            valid, msg = self.validate_input(task_input)
            if not valid:
                return TaskOutput(task_id=task_input.task_id, status="failed", summary=f"Input inválido: {msg}", confidence="low", requires_review=True)

            objective = task_input.objective
            context = task_input.context
            evidence = []
            artifacts = []
            tests = []

            from app.tools.registry import tool_registry
            fs_read = tool_registry.get_implementation("filesystem.read")
            fs_list = tool_registry.get_implementation("filesystem.list")
            fs_write = tool_registry.get_implementation("filesystem.write")

            # Inspecciona repositório se path fornecido
            repo_path = context.get("repo_path", "") or context.get("path", "")
            if repo_path and fs_read:
                read_res = fs_read(repo_path)
                evidence.append({"type": "code_inspection", "path": repo_path, "result": read_res})
                content = read_res.get("content") or ""
                artifacts.append({"type": "file_content", "path": repo_path, "preview": content[:2000]})

            # Lista ficheiros se workspace
            if fs_list:
                list_res = fs_list("")
                evidence.append({"type": "file_list", "result": {"count": list_res.get("count", 0)}})

            # Se houver código para analisar nos inputs
            for inp in task_input.inputs:
                if inp.get("type") == "code":
                    code = inp.get("content", "")
                    evidence.append({"type": "code_analysis", "length": len(code), "objective": objective})
                    # Análise estática simples
                    issues = []
                    if "TODO" in code:
                        issues.append("TODO encontrado")
                    if "print(" in code and "logging" not in code:
                        issues.append("Uso de print em vez de logging")
                    artifacts.append({"type": "analysis", "issues": issues})

            # Tenta executar testes se pedido
            if "test" in objective.lower() and context.get("run_tests"):
                try:
                    result = subprocess.run(["python", "-m", "pytest", "-q"], capture_output=True, text=True, timeout=30, cwd="/home/user/ai-brain")
                    tests.append({"name": "pytest", "stdout": result.stdout[:2000], "stderr": result.stderr[:2000], "returncode": result.returncode})
                    evidence.append({"type": "test_execution", "result": {"returncode": result.returncode}})
                except Exception as e:
                    tests.append({"name": "pytest", "error": str(e), "status": "failed"})

            summary = f"Análise de código para: {objective}\n"
            summary += f"- Ficheiros inspeccionados: {len([e for e in evidence if 'file' in e['type']])}\n"
            summary += f"- Testes executados: {len(tests)}\n"
            if tests:
                for t in tests:
                    summary += f"  - {t.get('name')}: returncode {t.get('returncode', 'N/A')}\n"
            summary += "\n[Limitações] Não declara sucesso sem execução verificada."

            self.status = "READY"
            return TaskOutput(
                task_id=task_input.task_id,
                status="completed",
                summary=summary,
                artifacts=artifacts,
                evidence=evidence,
                tests=tests,
                confidence="medium",
                requires_review=True,
                limitations=self.limitations
            )
        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(
                task_id=task_input.task_id,
                status="failed",
                summary=f"Erro em coding_qa: {str(e)}",
                confidence="low",
                requires_review=True,
                limitations=self.limitations + [str(e)]
            )
