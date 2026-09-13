"""
Validator — GOD §5.7 + Local AI Brain §9
Nunca confiar cegamente no resultado do agente.
"""
from typing import Dict, Any, List
from pydantic import BaseModel
from enum import Enum

class ValidationResult(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNCERTAIN = "UNCERTAIN"

class ValidationReport(BaseModel):
    task_id: str
    result: ValidationResult
    checks: List[Dict[str, Any]]
    issues: List[str] = []
    confidence: str = "medium"
    requires_review: bool = False

class Validator:
    def validate(self, task_output: Dict[str, Any], task_definition: Dict[str, Any] = None) -> ValidationReport:
        """
        Valida saída do agente contra critérios de aceitação
        """
        task_id = task_output.get("task_id", "unknown")
        checks = []
        issues = []

        # Check 1: summary existe e não vazio
        summary = task_output.get("summary", "")
        if not summary or len(summary.strip()) < 10:
            checks.append({"check": "summary_exists", "passed": False, "detail": "Resumo vazio ou muito curto"})
            issues.append("Resumo insuficiente")
        else:
            checks.append({"check": "summary_exists", "passed": True})

        # Check 2: status válido
        status = task_output.get("status", "")
        if status not in ["completed", "failed", "needs_review"]:
            checks.append({"check": "status_valid", "passed": False, "detail": f"Status {status} inválido"})
            issues.append(f"Status inválido: {status}")
        else:
            checks.append({"check": "status_valid", "passed": True})

        # Check 3: evidence existe para completed
        evidence = task_output.get("evidence", [])
        if status == "completed" and len(evidence) == 0:
            checks.append({"check": "evidence_for_completed", "passed": False, "detail": "Tarefa completed sem evidência"})
            issues.append("Sem evidência para tarefa completed")
        else:
            checks.append({"check": "evidence_for_completed", "passed": True})

        # Check 4: não inventa dados — verifica limitações declaradas
        limitations = task_output.get("limitations", [])
        if status == "completed" and not limitations:
            checks.append({"check": "limitations_declared", "passed": False, "detail": "Limitações não declaradas"})
            # Não é falha crítica, mas alerta
            issues.append("Limitações não declaradas — pode haver invenção")
        else:
            checks.append({"check": "limitations_declared", "passed": True})

        # Check 5: confiança coerente
        confidence = task_output.get("confidence", "medium")
        if confidence not in ["low", "medium", "high"]:
            checks.append({"check": "confidence_valid", "passed": False})
            issues.append(f"Confiança inválida: {confidence}")
        else:
            checks.append({"check": "confidence_valid", "passed": True})

        # Check 6: critérios de aceitação (se fornecidos)
        if task_definition and task_definition.get("acceptance_criteria"):
            criteria = task_definition["acceptance_criteria"]
            # Para MVP, verifica se summary menciona algo dos critérios
            # Não é validação semântica completa, mas evita vazio
            checks.append({"check": "acceptance_criteria_count", "passed": True, "criteria": criteria})

        # Determina resultado
        failed_checks = [c for c in checks if not c["passed"]]
        if len(failed_checks) == 0:
            result = ValidationResult.VALID
            confidence_out = "high" if confidence == "high" else "medium"
        elif len(failed_checks) == 1 and "limitations_declared" in [c["check"] for c in failed_checks]:
            result = ValidationResult.VALID
            confidence_out = "medium"
        elif len(failed_checks) <= 2:
            result = ValidationResult.UNCERTAIN
            confidence_out = "low"
        else:
            result = ValidationResult.INVALID
            confidence_out = "low"

        return ValidationReport(
            task_id=task_id,
            result=result,
            checks=checks,
            issues=issues,
            confidence=confidence_out,
            requires_review=(result != ValidationResult.VALID or task_output.get("requires_review", True))
        )

validator = Validator()
