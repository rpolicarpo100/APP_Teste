"""
Execution Engine — GOD §5.6 + Local AI Brain §8
Responsável por iniciar tarefas, comunicar com agentes, controlar tempo, retries, recolher resultados
"""
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import time

from app.brain.state import TaskState, validate_task_transition, can_transition_task
from app.security.permissions import check_permission, requires_approval, get_risk_level
from app.security.approval import approval_manager, ApprovalRequest
from app.security.audit import audit_manager, AuditLog, EventType
from app.agents.base import TaskInput
from app.tools.registry import tool_registry

from pydantic import BaseModel

class TaskExecutionResult(BaseModel):
    task_id: str
    status: TaskState
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 1
    duration_ms: int = 0
    approval_required: bool = False
    approval_id: Optional[str] = None

class Executor:
    def __init__(self, agent_registry, tool_registry_ref=None):
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry_ref or tool_registry
        self.max_attempts = 3

    def _check_tool_permissions(self, agent_id: str, required_tools: List[str], autonomy_level: int) -> tuple[bool, List[str], Optional[str]]:
        """
        Verifica permissões para todas as ferramentas requeridas.
        Retorna (permitido, bloqueadas, approval_id se necessário)
        """
        blocked = []
        approval_needed_for = []

        for tool_id in required_tools:
            allowed, reason = check_permission(agent_id, tool_id, autonomy_level)
            if not allowed:
                blocked.append(f"{tool_id}: {reason}")
            elif requires_approval(tool_id):
                approval_needed_for.append(tool_id)

        if blocked:
            return False, blocked, None

        # Se alguma ferramenta requer aprovação, cria approval request
        if approval_needed_for:
            # Para MVP, se autonomy_level >=3 e require_approval config, ainda cria approval
            # Mas retorna indicação de que precisa aprovação
            return True, [], "NEEDS_APPROVAL"

        return True, [], None

    def execute_task(self, task_def: Dict[str, Any], mission_context: Dict[str, Any] = None) -> TaskExecutionResult:
        """
        Executa uma tarefa com agente real.
        """
        mission_context = mission_context or {}
        task_id = task_def.get("id")
        agent_id = task_def.get("agent_id")
        autonomy_level = mission_context.get("autonomy_level", 2)

        start_time = time.time()

        # Audit: TaskStarted
        audit_manager.log(AuditLog.create(
            event_type=EventType.TaskStarted,
            actor=f"executor:{agent_id}",
            mission_id=task_def.get("mission_id"),
            task_id=task_id,
            agent_id=agent_id,
            details={"objective": task_def.get("objective")}
        ))

        # Verifica agente existe
        agent = self.agent_registry.get(agent_id) if hasattr(self.agent_registry, 'get') else self.agent_registry.get_agent(agent_id)
        if not agent:
            audit_manager.log(AuditLog.create(
                event_type=EventType.TaskFailed,
                actor="executor",
                task_id=task_id,
                details={"error": f"Agente {agent_id} não encontrado"},
                severity="ERROR"
            ))
            return TaskExecutionResult(
                task_id=task_id,
                status=TaskState.FAILED,
                error=f"Agente {agent_id} não encontrado — CAPACIDADE NÃO DISPONÍVEL",
                duration_ms=int((time.time() - start_time)*1000)
            )

        # Verifica permissões de ferramentas
        required_tools = task_def.get("required_tools", [])
        allowed, blocked, approval_flag = self._check_tool_permissions(agent_id, required_tools, autonomy_level)

        if not allowed:
            audit_manager.log(AuditLog.create(
                event_type=EventType.PermissionDenied,
                actor=agent_id,
                task_id=task_id,
                details={"blocked_tools": blocked},
                severity="WARN"
            ))
            return TaskExecutionResult(
                task_id=task_id,
                status=TaskState.BLOCKED,
                error=f"Permissões negadas: {blocked}",
                duration_ms=int((time.time() - start_time)*1000)
            )

        if approval_flag == "NEEDS_APPROVAL":
            # Cria approval request para primeira ferramenta que requer
            tool_requiring = None
            for t in required_tools:
                if requires_approval(t):
                    tool_requiring = t
                    break
            approval = ApprovalRequest.create(
                task_id=task_id,
                mission_id=task_def.get("mission_id", "unknown"),
                agent_id=agent_id,
                tool_id=tool_requiring,
                action=f"Executar tarefa {task_def.get('objective')}",
                target=tool_requiring,
                risk=get_risk_level(tool_requiring).value if hasattr(get_risk_level(tool_requiring), 'value') else str(get_risk_level(tool_requiring)),
                payload={"task": task_def}
            )
            approval_manager.request(approval)
            audit_manager.log(AuditLog.create(
                event_type=EventType.ApprovalRequested,
                actor=agent_id,
                task_id=task_id,
                details={"approval_id": approval.id, "tool": tool_requiring}
            ))
            return TaskExecutionResult(
                task_id=task_id,
                status=TaskState.BLOCKED,
                approval_required=True,
                approval_id=approval.id,
                error=f"Aprovação necessária para {tool_requiring}",
                duration_ms=int((time.time() - start_time)*1000)
            )

        # Executa agente real
        try:
            # Prepara TaskInput conforme contrato universal GOD §6
            task_input = TaskInput(
                task_id=task_id,
                mission_id=task_def.get("mission_id", "unknown"),
                agent_id=agent_id,
                objective=task_def.get("objective", ""),
                context=mission_context,
                inputs=task_def.get("inputs", []),
                acceptance_criteria=task_def.get("acceptance_criteria", []),
                permissions={}
            )

            # Chama agente
            output = agent.execute(task_input)

            # Converte TaskOutput para dict
            output_dict = output.model_dump() if hasattr(output, 'model_dump') else output.__dict__

            duration = int((time.time() - start_time)*1000)

            # Audit success
            audit_manager.log(AuditLog.create(
                event_type=EventType.AgentCompleted,
                actor=agent_id,
                task_id=task_id,
                details={"status": output_dict.get("status"), "duration_ms": duration}
            ))

            # Determina TaskState a partir do output
            if output_dict.get("status") == "completed":
                final_state = TaskState.SUCCEEDED
            elif output_dict.get("status") == "failed":
                final_state = TaskState.FAILED
            else:
                final_state = TaskState.SUCCEEDED  # default para needs_review ainda é sucesso com review

            return TaskExecutionResult(
                task_id=task_id,
                status=final_state,
                output=output_dict,
                duration_ms=duration
            )

        except Exception as e:
            duration = int((time.time() - start_time)*1000)
            audit_manager.log(AuditLog.create(
                event_type=EventType.TaskFailed,
                actor=agent_id,
                task_id=task_id,
                details={"error": str(e)},
                severity="ERROR"
            ))
            return TaskExecutionResult(
                task_id=task_id,
                status=TaskState.FAILED,
                error=str(e),
                duration_ms=duration
            )
