"""
Orchestrator — O verdadeiro cérebro operacional
Local AI Brain §6 + GOD §5 — Agora com Neon Postgres persistência total

Ciclo: PLAN → EXECUTE → OBSERVE → VALIDATE → MEMORY → RESULT
Migração SQLite efêmero → Neon Postgres free 0.5GB permanente (tarefa 3)
"""
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import json
from pathlib import Path

from app.brain.state import MissionState, TaskState, can_transition_mission, can_transition_task
from app.brain.planner import planner
from app.brain.validator import validator
from app.security.audit import audit_manager, AuditLog, EventType
from app.memory.manager import memory_manager
from app.memory.episodic import add_experience
from app.config.settings import ROOT_DIR, settings
from app.database.unified import get_conn, execute, fetchone, fetchall, init_tables, is_postgres

class Orchestrator:
    def __init__(self, agent_registry, executor):
        self.agent_registry = agent_registry
        self.executor = executor
        self.db_path = ROOT_DIR / "data" / "brain.db"

    def _get_conn(self):
        conn = get_conn()
        init_tables(conn)
        # Migração SQLite antiga se necessário (só SQLite)
        if not is_postgres():
            try:
                cur = conn.execute("PRAGMA table_info(tasks)")
                cols = [row[1] for row in cur.fetchall()]
                if "result_summary" not in cols:
                    conn.execute("ALTER TABLE tasks ADD COLUMN result_summary TEXT")
                if "evidence" not in cols:
                    conn.execute("ALTER TABLE tasks ADD COLUMN evidence TEXT")
                if "attempts" not in cols:
                    conn.execute("ALTER TABLE tasks ADD COLUMN attempts INTEGER DEFAULT 0")
                if "max_attempts" not in cols:
                    conn.execute("ALTER TABLE tasks ADD COLUMN max_attempts INTEGER DEFAULT 3")
                if "started_at" not in cols:
                    conn.execute("ALTER TABLE tasks ADD COLUMN started_at TIMESTAMP")
                cur2 = conn.execute("PRAGMA table_info(missions)")
                mcols = [row[1] for row in cur2.fetchall()]
                if "constraints_text" not in mcols:
                    conn.execute("ALTER TABLE missions ADD COLUMN constraints_text TEXT")
                if "completed_at" not in mcols:
                    conn.execute("ALTER TABLE missions ADD COLUMN completed_at TIMESTAMP")
                conn.commit()
            except Exception:
                pass
        return conn

    def create_mission(self, objective: str, expected_result: str = None, context: Dict[str, Any] = None, priority: str = "medium", autonomy_level: int = None) -> Dict[str, Any]:
        mission_id = str(uuid.uuid4())
        autonomy_level = autonomy_level if autonomy_level is not None else settings.autonomy_level
        context_json = json.dumps(context or {}, ensure_ascii=False)

        conn = self._get_conn()
        try:
            execute(conn, """
                INSERT INTO missions (id, objective, expected_result, context, priority, status, autonomy_level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mission_id, objective, expected_result, context_json, priority, MissionState.PENDING.value, autonomy_level, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
            conn.commit()
        finally:
            try:
                conn.close()
            except:
                pass

        audit_manager.log(AuditLog.create(
            event_type=EventType.MissionCreated,
            actor="orchestrator",
            mission_id=mission_id,
            details={"objective": objective, "priority": priority, "db": "neon" if is_postgres() else "sqlite"}
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
            cur = execute(conn, "SELECT * FROM missions WHERE id=?", (mission_id,))
            row = fetchone(cur)
            if not row:
                return None
            mission = dict(row)
            try:
                mission["context"] = json.loads(mission["context"]) if mission["context"] else {}
            except:
                mission["context"] = {}
            cur2 = execute(conn, "SELECT * FROM tasks WHERE mission_id=? ORDER BY created_at", (mission_id,))
            tasks = fetchall(cur2)
            mission["tasks"] = tasks
            return mission
        finally:
            try:
                conn.close()
            except:
                pass

    def list_missions(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cur = execute(conn, "SELECT * FROM missions ORDER BY created_at DESC LIMIT ?", (limit,))
            missions = []
            for row in fetchall(cur):
                m = dict(row)
                try:
                    m["context"] = json.loads(m["context"]) if m["context"] else {}
                except:
                    m["context"] = {}
                missions.append(m)
            return missions
        finally:
            try:
                conn.close()
            except:
                pass

    def _update_mission_status(self, mission_id: str, new_status: MissionState):
        conn = self._get_conn()
        try:
            cur = execute(conn, "SELECT status FROM missions WHERE id=?", (mission_id,))
            row = fetchone(cur)
            if not row:
                raise ValueError(f"Missao {mission_id} nao encontrada")
            current = row["status"]
            if not can_transition_mission(current, new_status.value):
                raise ValueError(f"Transicao invalida: {current} -> {new_status.value}")
            execute(conn, "UPDATE missions SET status=?, updated_at=? WHERE id=?", (new_status.value, datetime.utcnow().isoformat(), mission_id))
            conn.commit()
            audit_manager.log(AuditLog.create(
                event_type=EventType.MissionStateChanged,
                actor="orchestrator",
                mission_id=mission_id,
                details={"from": current, "to": new_status.value}
            ))
        finally:
            try:
                conn.close()
            except:
                pass

    def plan_mission(self, mission_id: str) -> Dict[str, Any]:
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Missao {mission_id} nao encontrada")

        self._update_mission_status(mission_id, MissionState.PLANNING)

        plan = planner.plan(mission_id=mission_id, objective=mission["objective"], context=mission["context"])

        conn = self._get_conn()
        try:
            for task in plan.tasks:
                execute(conn, """
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
            try:
                conn.close()
            except:
                pass

        self._update_mission_status(mission_id, MissionState.READY)

        return {
            "mission_id": mission_id,
            "plan": plan.model_dump(),
            "tasks_created": len(plan.tasks)
        }

    def _get_ready_tasks(self, mission_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cur = execute(conn, "SELECT * FROM tasks WHERE mission_id=? AND status IN ('PENDING','READY','RETRYING') ORDER BY created_at", (mission_id,))
            all_tasks = fetchall(cur)
            ready = []
            task_status_map = {}
            cur2 = execute(conn, "SELECT id, status FROM tasks WHERE mission_id=?", (mission_id,))
            for r in fetchall(cur2):
                task_status_map[r["id"]] = r["status"]

            for task in all_tasks:
                try:
                    deps = json.loads(task["dependencies"]) if task["dependencies"] else []
                except:
                    deps = []
                if not deps:
                    ready.append(task)
                else:
                    if all(task_status_map.get(d) == TaskState.SUCCEEDED.value for d in deps):
                        ready.append(task)
            return ready
        finally:
            try:
                conn.close()
            except:
                pass

    def _update_task_status(self, task_id: str, new_status: TaskState, result_summary: str = None, artifacts: str = None, evidence: str = None):
        conn = self._get_conn()
        try:
            cur = execute(conn, "SELECT status FROM tasks WHERE id=?", (task_id,))
            row = fetchone(cur)
            if not row:
                raise ValueError(f"Task {task_id} nao encontrada")
            current = row["status"]
            if not can_transition_task(current, new_status.value):
                if not (current == "PENDING" and new_status.value == "READY"):
                    raise ValueError(f"Transicao tarefa invalida: {current} -> {new_status.value}")

            if new_status == TaskState.RUNNING:
                execute(conn, "UPDATE tasks SET status=?, started_at=?, updated_at=? WHERE id=?", (new_status.value, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), task_id))
            elif new_status in [TaskState.SUCCEEDED, TaskState.FAILED, TaskState.BLOCKED, TaskState.CANCELLED]:
                execute(conn, "UPDATE tasks SET status=?, completed_at=?, updated_at=?, result_summary=?, artifacts=?, evidence=? WHERE id=?",
                             (new_status.value, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), result_summary, artifacts, evidence, task_id))
            else:
                execute(conn, "UPDATE tasks SET status=?, updated_at=? WHERE id=?", (new_status.value, datetime.utcnow().isoformat(), task_id))
            conn.commit()

            audit_manager.log(AuditLog.create(
                event_type=EventType.TaskStateChanged,
                actor="orchestrator",
                task_id=task_id,
                details={"from": current, "to": new_status.value}
            ))
        finally:
            try:
                conn.close()
            except:
                pass

    def run_mission(self, mission_id: str) -> Dict[str, Any]:
        mission = self.get_mission(mission_id)
        if not mission:
            raise ValueError(f"Missao {mission_id} nao encontrada")

        if mission["status"] not in [MissionState.READY.value, MissionState.RUNNING.value, MissionState.NEEDS_REVIEW.value]:
            if mission["status"] == MissionState.PENDING.value:
                self.plan_mission(mission_id)
                mission = self.get_mission(mission_id)

        self._update_mission_status(mission_id, MissionState.RUNNING)

        max_steps = settings.max_agent_steps
        steps = 0
        results = []

        while steps < max_steps:
            ready_tasks = self._get_ready_tasks(mission_id)
            if not ready_tasks:
                conn = self._get_conn()
                try:
                    cur = execute(conn, "SELECT COUNT(*) as c FROM tasks WHERE mission_id=? AND status IN ('PENDING','READY','RUNNING','RETRYING')", (mission_id,))
                    row = fetchone(cur)
                    remaining = row["c"] if isinstance(row, dict) else row[0] if row else 0
                    if remaining == 0:
                        break
                finally:
                    try:
                        conn.close()
                    except:
                        pass
                break

            for task in ready_tasks:
                if steps >= max_steps:
                    break

                if task["status"] == TaskState.PENDING.value:
                    self._update_task_status(task["id"], TaskState.READY)

                self._update_task_status(task["id"], TaskState.RUNNING)

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
                except Exception:
                    task_def = {"id": task["id"], "mission_id": mission_id, "objective": task["objective"], "agent_id": task["agent_id"], "required_tools": []}

                exec_result = self.executor.execute_task(task_def, mission_context=mission["context"])

                if exec_result.output:
                    validation = validator.validate(exec_result.output, task_def)
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

        conn = self._get_conn()
        try:
            cur = execute(conn, "SELECT status, COUNT(*) as c FROM tasks WHERE mission_id=? GROUP BY status", (mission_id,))
            rows = fetchall(cur)
            status_counts = {}
            for row in rows:
                if isinstance(row, dict):
                    status_counts[row["status"]] = row["c"]
                else:
                    status_counts[row[0]] = row[1]
        finally:
            try:
                conn.close()
            except:
                pass

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
            self._update_mission_status(mission_id, MissionState.COMPLETED)
        else:
            if blocked > 0 or failed > 0:
                self._update_mission_status(mission_id, MissionState.NEEDS_REVIEW)
            else:
                self._update_mission_status(mission_id, MissionState.COMPLETED)

        final_mission = self.get_mission(mission_id)

        audit_manager.log(AuditLog.create(
            event_type=EventType.TaskCompleted,
            actor="orchestrator",
            mission_id=mission_id,
            details={"steps": steps, "results": results, "status_counts": status_counts, "db": "neon" if is_postgres() else "sqlite"}
        ))

        return {
            "mission": final_mission,
            "steps_executed": steps,
            "results": results,
            "status_counts": status_counts
        }
