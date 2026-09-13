"""
Testes unitários — Máquina de estados
GOD §15 Testes obrigatórios
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.brain.state import MissionState, TaskState, can_transition_mission, can_transition_task, validate_mission_transition, validate_task_transition
import pytest

def test_mission_pending_to_planning_valid():
    assert can_transition_mission(MissionState.PENDING, MissionState.PLANNING) == True

def test_mission_pending_to_completed_invalid():
    assert can_transition_mission(MissionState.PENDING, MissionState.COMPLETED) == False

def test_mission_completed_terminal():
    assert can_transition_mission(MissionState.COMPLETED, MissionState.RUNNING) == False
    assert can_transition_mission(MissionState.CANCELLED, MissionState.PENDING) == False

def test_task_pending_to_ready_valid():
    assert can_transition_task(TaskState.PENDING, TaskState.READY) == True

def test_task_pending_to_succeeded_invalid():
    # Regra absoluta: tarefa não pode passar directo de PENDING para SUCCEEDED
    assert can_transition_task(TaskState.PENDING, TaskState.SUCCEEDED) == False

def test_task_running_to_succeeded_valid():
    assert can_transition_task(TaskState.RUNNING, TaskState.SUCCEEDED) == True

def test_task_cancelled_terminal():
    assert can_transition_task(TaskState.CANCELLED, TaskState.PENDING) == False

def test_validate_raises():
    try:
        validate_mission_transition("PENDING", "COMPLETED")
        assert False, "Deveria ter lançado excepção"
    except ValueError:
        assert True

    try:
        validate_task_transition("PENDING", "SUCCEEDED")
        assert False, "Deveria ter lançado excepção"
    except ValueError:
        assert True

if __name__ == "__main__":
    test_mission_pending_to_planning_valid()
    test_mission_pending_to_completed_invalid()
    test_mission_completed_terminal()
    test_task_pending_to_ready_valid()
    test_task_pending_to_succeeded_invalid()
    test_task_running_to_succeeded_valid()
    test_task_cancelled_terminal()
    test_validate_raises()
    print("✅ test_state_machine passed")
