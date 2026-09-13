"""
Orchestrator — O verdadeiro cérebro operacional
Local AI Brain §6 + GOD §5

Ciclo: PLAN → EXECUTE → OBSERVE → VALIDATE → MEMORY → RESULT
"""
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json
import sqlite3
from pathlib import Path

from app.brain.state import MissionState, TaskState, can_transition_mission, can_transition_task
from app.brain.planner import planner
from app.brain.validator import validator
from app.security.audit import audit_manager, AuditLog, EventType
from app.memory.manager import memory_manager
from app.memory.episodic import add_experience
from app.config.settings import ROOT_DIR, settings

class Orchestrator:
    def __init__(self, agent_registry, executor):
        self.agent_registry = agent_registry
        self.executor = executor
        self.db_path = ROOT_DIR / "data" / "brain.db"

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def create_mission(self, objective: str, expected_result: str = None, context: Dict[str, Any] = None, priority: str = "medium", autonomy_level: int = None) -> Dict[str, Any]:
        mission_id = str(uuid.uuid4())
        autonomy_level = autonomy_level if autonomy_level is not None else settings.autonomy_level
        context_json = json.dumps(context or {}, ensure_ascii=False)

        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT INTO missions (id, objective, expected_result, context, priority, status, autonomy_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mission_id, objective, expected_result, context_json, priority, MissionState.PENDING.value, autonomy_level, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
            conn.commit()
        finally:
            conn.close()

        audit_manager.log(AuditLog.create(
            event_type=EventType.MissionCreated,
            actor="orchestrator",
            mission_id=mission_id,
            details={"objective": objective, "priority": priority}
        ))

        memory_manager.add(f"Missao criada: {objective}", type="short", mission_id=mission_id, source="orchestrator")

        return {
            "id": mission_id,
            "objective": objective,
            "expected_result": expected_result,
            "context": context,
            "priority": priority,
            "status": MissionState.PENDING.value,
            "autonomy_level": autonomy_level
        }

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT * FROM missions WHERE id=?", (mission_id,))
            row = cur.fetchone()
            if not row:
                return None
            mission = dict(row)
            # Parse context
            try:
                mission["context"] = json.loads(mission["context"]) if mission["context"] else {}
            except:
                mission["context"] = {}
            # Get tasks
            cur2 = conn.execute("SELECT * FROM tasks WHERE mission_id=? ORDER BY created_at", (mission_id,))
            tasks = [dict(r) for r in cur2.fetchall()]
            mission["tasks"] = tasks
            return mission
        finally:
            conn.close()

    def list_missions(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT * FROM missions ORDER BY created_at DESC LIMIT ?", (limit,))
            missions = []
            for row in cur.fetchall():
                m = dict(row)
                try:
                    m["context"] = json.loads(m["context"]) if m["context"] else {}
                except:
                    m["context"] = {}
                missions.append(m)
            return missions
        finally:
            conn.close()

    def _update_mission_status(self, mission_id: str, new_status: MissionState):
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT status FROM missions WHERE id=?", (mission_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Missao {mission_id} nao encontrada")
            current = row["status"]
            if not can_transition_mission(current, new_status.value):
                raise ValueError(f"Transicao invalida: {current} -> {new_status.value}")
            conn.execute("UPDATE missions SET status=?, updated_at=? WHERE id=?", (new_status.value, datetime.utcnow().isoformat(), mission_id))
            conn.commit()
            audit_manager.log(AuditLog.create(
                event_type=EventType.MissionStateChanged,
                actor="orchestrator",
                mission_id=mission_id,
                details={"from": current, "to": new_status.value}
            ))
        finally:
            conn.close()

    def plan_mission(self, mission_id: str) -> Dict[str, Any]:
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Missao {mission_id} nao encontrada")

        self._update_mission_status(mission_id, MissionState.PLANNING)

        # Usa planner
        plan = planner.plan(mission_id=mission_id, objective=mission["objective"], context=mission["context"])

        # Persiste tasks
        conn = self._get_conn()
        try:
            for task in plan.tasks:
                conn.execute("""
                    INSERT INTO tasks (id, mission_id, objective, description, agent_id, required_skills, dependencies, priority, acceptance_criteria, risk, required_tools, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.id,
                    mission_id,
                    task.objective,
                    task.description,
                    task.agent_id,
                    json.dumps(task.required_skills, ensure_ascii=False),
                    json.dumps(task.dependencies, ensure_ascii=False),
                    task.priority,
                    json.dumps(task.acceptance_criteria, ensure_ascii=False),
                    task.risk,
                    json.dumps(task.required_tools, ensure_ascii=False),
                    task.status,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                ))
                audit_manager.log(AuditLog.create(
                    event_type=EventType.TaskCreated,
                    actor="planner",
                    mission_id=mission_id,
                    task_id=task.id,
                    agent_id=task.agent_id,
                    details={"objective": task.objective}
                ))
            conn.commit()
        finally:
            conn.close()

        self._update_mission_status(mission_id, MissionState.READY)

        return {
            "mission_id": mission_id,
            "plan": plan.model_dump(),
            "tasks_created": len(plan.tasks)
        }

    def _get_ready_tasks(self, mission_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            # Tarefas PENDING ou READY cujas dependências estão SUCCEEDED
            cur = conn.execute("SELECT * FROM tasks WHERE mission_id=? AND status IN ('PENDING','READY','RETRYING') ORDER BY created_at", (mission_id,))
            all_tasks = [dict(r) for r in cur.fetchall()]
            # Verifica dependências
            ready = []
            task_status_map = {}
            cur2 = conn.execute("SELECT id, status FROM tasks WHERE mission_id=?", (mission_id,))
            for r in cur2.fetchall():
                task_status_map[r["id"]] = r["status"]

            for task in all_tasks:
                try:
                    deps = json.loads(task["dependencies"]) if task["dependencies"] else []
                except:
                    deps = []
                if not deps:
                    ready.append(task)
                else:
                    # Todas as deps devem estar SUCCEEDED
                    if all(task_status_map.get(d) == TaskState.SUCCEEDED.value for d in deps):
                        ready.append(task)
            return ready
        finally:
            conn.close()

    def _update_task_status(self, task_id: str, new_status: TaskState, result_summary: str = None, artifacts: str = None, evidence: str = None):
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT status FROM tasks WHERE id=?", (task_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Task {task_id} nao encontrada")
            current = row["status"]
            if not can_transition_task(current, new_status.value):
                # Permite forçar se for de PENDING para READY (primeira transição)
                if not (current == "PENDING" and new_status.value == "READY"):
                    raise ValueError(f"Transicao tarefa invalida: {current} -> {new_status.value}")

            if new_status == TaskState.RUNNING:
                conn.execute("UPDATE tasks SET status=?, started_at=?, updated_at=? WHERE id=?", (new_status.value, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), task_id))
            elif new_status in [TaskState.SUCCEEDED, TaskState.FAILED, TaskState.BLOCKED, TaskState.CANCELLED]:
                conn.execute("UPDATE tasks SET status=?, completed_at=?, updated_at=?, result_summary=?, artifacts=?, evidence=? WHERE id=?",
                             (new_status.value, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), result_summary, artifacts, evidence, task_id))
            else:
                conn.execute("UPDATE tasks SET status=?, updated_at=? WHERE id=?", (new_status.value, datetime.utcnow().isoformat(), task_id))
            conn.commit()

            audit_manager.log(AuditLog.create(
                event_type=EventType.TaskStateChanged,
                actor="orchestrator",
                task_id=task_id,
                details={"from": current, "to": new_status.value}
            ))
        finally:
            conn.close()

    def run_mission(self, mission_id: str) -> Dict[str, Any]:
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Missao {mission_id} nao encontrada")

        if mission["status"] not in [MissionState.READY.value, MissionState.RUNNING.value, MissionState.NEEDS_REVIEW.value]:
            if mission["status"] == MissionState.PENDING.value:
                # Auto-plan
                self.plan_mission(mission_id)
                mission = self.get_mission(mission_id)

        self._update_mission_status(mission_id, MissionState.RUNNING)

        # Loop de execução — conforme spec §20 MAX_AGENT_STEPS
        max_steps = settings.max_agent_steps
        steps = 0
        results = []

        while steps < max_steps:
            ready_tasks = self._get_ready_tasks(mission_id)
            if not ready_tasks:
                # Verifica se há tarefas bloqueadas ou pendentes
                conn = self._get_conn()
                try:
                    cur = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE mission_id=? AND status IN ('PENDING','READY','RUNNING','RETRYING')", (mission_id,))
                    remaining = cur.fetchone()["c"]
                    if remaining == 0:
                        break  # todas concluídas
                finally:
                    conn.close()
                # Se não há ready mas há remaining, significa deadlock de dependências ou bloqueadas
                break

            # Executa tarefas prontas — para MVP, sequencial; futuro paralelo
            for task in ready_tasks:
                if steps >= max_steps:
                    break

                # Transição para READY se PENDING
                if task["status"] == TaskState.PENDING.value:
                    self._update_task_status(task["id"], TaskState.READY)

                self._update_task_status(task["id"], TaskState.RUNNING)

                # Prepara definição para executor
                try:
                    task_def = {
                        "id": task["id"],
                        "mission_id": mission_id,
                        "objective": task["objective"],
                        "description": task["description"],
                        "agent_id": task["agent_id"],
                        "required_skills": json.loads(task["required_skills"]) if task["required_skills"] else [],
                        "dependencies": json.loads(task["dependencies"]) if task["dependencies"] else [],
                        "acceptance_criteria": json.loads(task["acceptance_criteria"]) if task["acceptance_criteria"] else [],
                        "required_tools": json.loads(task["required_tools"]) if task["required_tools"] else [],
                    }
                except Exception as e:
                    task_def = {"id": task["id"], "mission_id": mission_id, "objective": task["objective"], "agent_id": task["agent_id"], "required_tools": []}

                exec_result = self.executor.execute_task(task_def, mission_context=mission["context"])

                # Valida resultado
                if exec_result.output:
                    validation = validator.validate(exec_result.output, task_def)
                    # Se inválido, marca como NEEDS_REVIEW
                    if validation.result.value == "INVALID":
                        self._update_task_status(
                            task["id"],
                            TaskState.FAILED,
                            result_summary=exec_result.output.get("summary", "") + f"\n[VALIDATION FAILED] {validation.issues}",
                            artifacts=json.dumps(exec_result.output.get("artifacts", []), ensure_ascii=False),
                            evidence=json.dumps(exec_result.output.get("evidence", []), ensure_ascii=False)
                        )
                        add_experience(
                            task=task["objective"],
                            agent=task["agent_id"],
                            action="execute",
                            result="failed validation",
                            error=str(validation.issues),
                            lesson="Validar output contra critérios de aceitação"
                        )
                    else:
                        final_status = TaskState.SUCCEEDED if exec_result.status == TaskState.SUCCEEDED else exec_result.status
                        self._update_task_status(
                            task["id"],
                            final_status,
                            result_summary=exec_result.output.get("summary", ""),
                            artifacts=json.dumps(exec_result.output.get("artifacts", []), ensure_ascii=False),
                            evidence=json.dumps(exec_result.output.get("evidence", []), ensure_ascii=False)
                        )
                        # Memória episódica
                        add_experience(
                            task=task["objective"],
                            agent=task["agent_id"],
                            action="execute",
                            result=exec_result.output.get("summary", "")[:500],
                            lesson=f"Confiança {exec_result.output.get('confidence')}"
                        )
                        memory_manager.add(
                            content=f"Task {task['objective']} concluída por {task['agent_id']}: {exec_result.output.get('summary','')[:500]}",
                            type="episodic",
                            mission_id=mission_id,
                            task_id=task["id"],
                            source=task["agent_id"]
                        )
                else:
                    # Sem output — falha ou bloqueada
                    if exec_result.status == TaskState.BLOCKED and exec_result.approval_required:
                        self._update_task_status(task["id"], TaskState.BLOCKED, result_summary=exec_result.error)
                    else:
                        self._update_task_status(task["id"], exec_result.status, result_summary=exec_result.error or "Sem output")

                results.append({
                    "task_id": task["id"],
                    "status": exec_result.status.value,
                    "duration_ms": exec_result.duration_ms,
                    "approval_required": exec_result.approval_required
                })

                steps += 1

            # Re-avalia ready tasks após cada ronda

        # Após loop, verifica estado final da missão
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT status, COUNT(*) as c FROM tasks WHERE mission_id=? GROUP BY status", (mission_id,))
            status_counts = {row["status"]: row["c"] for row in cur.fetchall()}
        finally:
            conn.close()

        failed = status_counts.get(TaskState.FAILED.value, 0)
        blocked = status_counts.get(TaskState.BLOCKED.value, 0)
        succeeded = status_counts.get(TaskState.SUCCEEDED.value, 0)
        total = sum(status_counts.values())

        if failed > 0 and succeeded == 0:
            self._update_mission_status(mission_id, MissionState.FAILED)
        elif blocked > 0:
            self._update_mission_status(mission_id, MissionState.BLOCKED)
        elif succeeded == total and total > 0:
            self._update_mission_status(mission_id, MissionState.VALIDATING)
            # Validação final da missão
            self._update_mission_status(mission_id, MissionState.COMPLETED)
        else:
            # Parcial
            if blocked > 0 or failed > 0:
                self._update_mission_status(mission_id, MissionState.NEEDS_REVIEW)
            else:
                self._update_mission_status(mission_id, MissionState.COMPLETED)

        final_mission = self.get_mission(mission_id)

        audit_manager.log(AuditLog.create(
            event_type=EventType.TaskCompleted,
            actor="orchestrator",
            mission_id=mission_id,
            details={"steps": steps, "results": results, "status_counts": status_counts}
        ))

        return {
            "mission": final_mission,
            "steps_executed": steps,
            "results": results,
            "status_counts": status_counts
        }
