"""
Planner — GOD §5.2 Mission Planner + Local AI Brain §7
Transforma missão em tarefas estruturadas.
Não executa ferramentas, só planeia.
"""
from typing import List, Dict, Any
import uuid
from pydantic import BaseModel
from enum import Enum

class TaskDefinition(BaseModel):
    id: str
    objective: str
    description: str
    agent_id: str
    required_skills: List[str] = []
    dependencies: List[str] = []
    priority: str = "medium"
    acceptance_criteria: List[str] = []
    risk: str = "low"
    required_tools: List[str] = []
    status: str = "PENDING"
    max_attempts: int = 3

class MissionPlan(BaseModel):
    mission_id: str
    objective: str
    tasks: List[TaskDefinition]
    estimated_steps: int

class Planner:
    """
    Planner que divide missão em tarefas.
    Usa heurísticas + opcionalmente Ollama para decomposição.
    """

    # Mapeamento de palavras-chave para agentes — baseado em competências — agora com builder para apps/sites via chat
    KEYWORD_AGENT_MAP = {
        "pesquisa": "research",
        "investiga": "research",
        "research": "research",
        "analisa mercado": "business",
        "concorrência": "business",
        "negócio": "business",
        "ecommerce": "business",
        "e-commerce": "business",
        "design": "design",
        "ui": "design",
        "ux": "design",
        "wireframe": "design",
        "visual": "design",
        "código": "coding_qa",
        "coding": "coding_qa",
        "programa": "coding_qa",
        "bug": "coding_qa",
        "teste": "coding_qa",
        "test": "coding_qa",
        "browser": "browser",
        "navega": "browser",
        "automatiza": "automation",
        "automation": "automation",
        "agendar": "automation",
        "monitor": "monitor",
        "verifica": "monitor",
        # Builder — construção de apps e sites via chat — NOVO
        "criar app": "builder",
        "cria app": "builder",
        "construir app": "builder",
        "criar site": "builder",
        "cria site": "builder",
        "construir site": "builder",
        "landing page": "builder",
        "website": "builder",
        "página web": "builder",
        "portfolio": "builder",
        "portfólio": "builder",
        "loja online": "builder",
        "site de": "builder",
        "app de": "builder",
    }

    def _detect_agent(self, text: str) -> str:
        text_lower = text.lower()
        for keyword, agent in self.KEYWORD_AGENT_MAP.items():
            if keyword in text_lower:
                return agent
        return "research"  # default

    def _detect_skills(self, agent_id: str) -> List[str]:
        mapping = {
            "research": ["deep_research", "source_analysis"],
            "business": ["market_analysis", "business_model"],
            "design": ["ui_ux", "visual_concept"],
            "coding_qa": ["code_inspection", "testing"],
            "browser": ["web_navigation"],
            "automation": ["workflow_creation"],
            "monitor": ["health_check"],
            "builder": ["site_building", "frontend_dev", "ui_ux_implementation"]
        }
        return mapping.get(agent_id, [])

    def _detect_tools(self, agent_id: str) -> List[str]:
        mapping = {
            "research": ["web.search", "web.fetch", "filesystem.read"],
            "business": ["web.search", "filesystem.read"],
            "design": ["filesystem.read", "filesystem.write", "site.builder"],
            "coding_qa": ["filesystem.read", "filesystem.write", "filesystem.list", "site.builder"],
            "browser": ["browser.open", "web.fetch"],
            "automation": ["scheduler.create", "filesystem.write"],
            "monitor": ["filesystem.read"],
            "builder": ["site.builder", "filesystem.write", "filesystem.read"]
        }
        return mapping.get(agent_id, [])

    def plan(self, mission_id: str, objective: str, context: Dict[str, Any] = None) -> MissionPlan:
        """
        Cria plano estruturado.
        Se objectivo contém múltiplas partes (e, depois, com, etc), divide.
        """
        context = context or {}
        objective_lower = objective.lower()

        tasks: List[TaskDefinition] = []

        # Heurística: se missão menciona múltiplas áreas, cria tarefas multidisciplinares
        # Exemplo: "Pesquisar mercado e criar design" => 2 tarefas
        # Split por conectores
        connectors = [" e depois ", " depois ", " e também ", " e ", " com ", " + "]
        sub_objectives = [objective]
        for conn in connectors:
            if conn in objective_lower:
                # Split simples
                parts = objective.split(conn)
                if len(parts) > 1 and len(parts) <= 4:
                    sub_objectives = [p.strip() for p in parts if p.strip()]
                    break

        # Se ainda for 1, mas contiver palavras de múltiplos domínios, divide
        if len(sub_objectives) == 1:
            # Detecta múltiplos agentes no mesmo objectivo
            detected_agents = set()
            for kw, ag in self.KEYWORD_AGENT_MAP.items():
                if kw in objective_lower:
                    detected_agents.add(ag)
            if len(detected_agents) > 1:
                # Cria uma tarefa por agente detectado
                sub_objectives = [f"{objective} - foco {ag}" for ag in detected_agents]

        prev_task_id = None
        for idx, sub_obj in enumerate(sub_objectives):
            agent_id = self._detect_agent(sub_obj)
            task_id = str(uuid.uuid4())
            deps = [prev_task_id] if prev_task_id else []

            # Ajusta dependências: se for design após research, mantém; se for paralelo, sem deps
            # Para MVP, tarefas multidisciplinares podem ser paralelas se não houver "depois"
            if "depois" in objective_lower and prev_task_id:
                deps = [prev_task_id]
            elif len(sub_objectives) > 1 and idx > 0:
                # Se não tem "depois", permite paralelo — sem dependência
                deps = []

            task = TaskDefinition(
                id=task_id,
                objective=sub_obj,
                description=f"Tarefa {idx+1}/{len(sub_objectives)} para missão {mission_id}: {sub_obj}",
                agent_id=agent_id,
                required_skills=self._detect_skills(agent_id),
                dependencies=deps,
                priority=context.get("priority", "medium"),
                acceptance_criteria=[
                    f"Resultado relevante para: {sub_obj}",
                    "Evidência registada",
                    "Sem invenção de dados"
                ],
                risk="low" if agent_id in ["research", "monitor"] else "medium",
                required_tools=self._detect_tools(agent_id),
                max_attempts=3
            )
            tasks.append(task)
            prev_task_id = task_id

        # Se nenhuma divisão, cria 1 tarefa única
        if not tasks:
            agent_id = self._detect_agent(objective)
            tasks.append(TaskDefinition(
                id=str(uuid.uuid4()),
                objective=objective,
                description=objective,
                agent_id=agent_id,
                required_skills=self._detect_skills(agent_id),
                dependencies=[],
                priority=context.get("priority", "medium"),
                acceptance_criteria=["Resultado entregue", "Evidência registada"],
                risk="low",
                required_tools=self._detect_tools(agent_id)
            ))

        return MissionPlan(
            mission_id=mission_id,
            objective=objective,
            tasks=tasks,
            estimated_steps=len(tasks)
        )

planner = Planner()
