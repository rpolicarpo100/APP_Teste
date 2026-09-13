"""
Base Agent — Contrato Universal GOD §6
"""
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
from datetime import datetime

class AgentStatus(str, Enum):
    IDLE = "IDLE"
    READY = "READY"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    DISABLED = "DISABLED"

class TaskInput(BaseModel):
    task_id: str
    mission_id: str
    agent_id: str
    objective: str
    context: Dict[str, Any] = {}
    inputs: List[Dict[str, Any]] = []
    acceptance_criteria: List[str] = []
    permissions: Dict[str, Any] = {}

class TaskOutput(BaseModel):
    task_id: str
    status: str  # completed, failed, needs_review
    summary: str
    artifacts: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    tests: List[Dict[str, Any]] = []
    limitations: List[str] = []
    confidence: str = "medium"  # low, medium, high
    requires_review: bool = True
    next_recommendations: List[str] = []

class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, specialty: str, version: str = "1.0.0"):
        self.agent_id = agent_id
        self.name = name
        self.specialty = specialty
        self.version = version
        self.status = AgentStatus.IDLE
        self.skills: List[str] = []
        self.tools: List[str] = []
        self.limitations: List[str] = []

    @abstractmethod
    def execute(self, task_input: TaskInput) -> TaskOutput:
        """Método principal — cada agente implementa"""
        pass

    def validate_input(self, task_input: TaskInput) -> tuple[bool, str]:
        if not task_input.task_id:
            return False, "task_id obrigatório"
        if not task_input.objective:
            return False, "objective obrigatório"
        if task_input.agent_id != self.agent_id:
            return False, f"agent_id mismatch: esperado {self.agent_id}, recebido {task_input.agent_id}"
        return True, "OK"

    def get_info(self) -> dict:
        return {
            "id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "specialty": self.specialty,
            "skills": self.skills,
            "tools": self.tools,
            "status": self.status,
            "limitations": self.limitations,
            "contract_version": "1.0.0"
        }
