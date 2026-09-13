"""
GOD Cerebro Core — Máquina de estados formal
Conforme GOD spec §8 e Local AI Brain §6-8

Estados de missão e tarefa com transições validadas.
"""
from enum import Enum
from typing import Dict, Set

class MissionState(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    READY = "READY"
    RUNNING = "RUNNING"
    VALIDATING = "VALIDATING"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TaskState(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"

# Transições válidas — VERIFICADO contra spec §8
MISSION_TRANSITIONS: Dict[MissionState, Set[MissionState]] = {
    MissionState.PENDING: {MissionState.PLANNING, MissionState.CANCELLED},
    MissionState.PLANNING: {MissionState.WAITING_APPROVAL, MissionState.READY, MissionState.BLOCKED, MissionState.FAILED, MissionState.CANCELLED},
    MissionState.WAITING_APPROVAL: {MissionState.READY, MissionState.BLOCKED, MissionState.CANCELLED, MissionState.FAILED},
    MissionState.READY: {MissionState.RUNNING, MissionState.BLOCKED, MissionState.CANCELLED},
    MissionState.RUNNING: {MissionState.VALIDATING, MissionState.NEEDS_REVIEW, MissionState.BLOCKED, MissionState.FAILED, MissionState.CANCELLED},
    MissionState.VALIDATING: {MissionState.COMPLETED, MissionState.NEEDS_REVIEW, MissionState.FAILED, MissionState.BLOCKED},
    MissionState.NEEDS_REVIEW: {MissionState.READY, MissionState.RUNNING, MissionState.COMPLETED, MissionState.FAILED, MissionState.CANCELLED},
    MissionState.BLOCKED: {MissionState.READY, MissionState.PLANNING, MissionState.FAILED, MissionState.CANCELLED},
    MissionState.FAILED: {MissionState.PLANNING, MissionState.READY, MissionState.CANCELLED},  # retry path
    MissionState.COMPLETED: {MissionState.CANCELLED},  # terminal, but allow cancel for admin
    MissionState.CANCELLED: set(),  # terminal
}

TASK_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
    TaskState.PENDING: {TaskState.READY, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.READY: {TaskState.RUNNING, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.RUNNING: {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.BLOCKED, TaskState.RETRYING, TaskState.CANCELLED},
    TaskState.SUCCEEDED: {TaskState.CANCELLED},  # terminal success
    TaskState.FAILED: {TaskState.RETRYING, TaskState.BLOCKED, TaskState.CANCELLED, TaskState.PENDING},  # allow retry
    TaskState.BLOCKED: {TaskState.READY, TaskState.PENDING, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.CANCELLED: set(),
    TaskState.RETRYING: {TaskState.READY, TaskState.RUNNING, TaskState.FAILED, TaskState.BLOCKED},
}

def can_transition_mission(from_state: MissionState, to_state: MissionState) -> bool:
    """Verifica transição válida de missão"""
    if isinstance(from_state, str):
        from_state = MissionState(from_state)
    if isinstance(to_state, str):
        to_state = MissionState(to_state)
    allowed = MISSION_TRANSITIONS.get(from_state, set())
    return to_state in allowed

def can_transition_task(from_state: TaskState, to_state: TaskState) -> bool:
    """Verifica transição válida de tarefa — impede PENDING->SUCCEEDED directo"""
    if isinstance(from_state, str):
        from_state = TaskState(from_state)
    if isinstance(to_state, str):
        to_state = TaskState(to_state)
    # Regra absoluta do spec: tarefa não pode passar directo de PENDING para SUCCEEDED
    if from_state == TaskState.PENDING and to_state == TaskState.SUCCEEDED:
        return False
    allowed = TASK_TRANSITIONS.get(from_state, set())
    return to_state in allowed

def validate_mission_transition(from_state: str, to_state: str):
    if not can_transition_mission(from_state, to_state):
        raise ValueError(f"Transição de missão inválida: {from_state} -> {to_state}")

def validate_task_transition(from_state: str, to_state: str):
    if not can_transition_task(from_state, to_state):
        raise ValueError(f"Transição de tarefa inválida: {from_state} -> {to_state}")
