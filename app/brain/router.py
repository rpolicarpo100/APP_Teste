"""
Brain Router — decide qual agente usar baseado em competências
GOD §5.3 Agent Registry + §5.5 Scheduler + Provider Health Agent
"""
from typing import Dict, List, Optional

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, object] = {}

    def register(self, agent):
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str):
        return self._agents.get(agent_id)

    def get_agent(self, agent_id: str):
        return self.get(agent_id)

    def list_agents(self):
        return list(self._agents.values())

    def list_available(self):
        return [a for a in self._agents.values() if getattr(a, 'status', 'READY') != 'DISABLED']

    def find_by_skill(self, skill: str):
        return [a for a in self._agents.values() if skill in getattr(a, 'skills', [])]

    def find_by_specialty(self, specialty: str):
        return [a for a in self._agents.values() if specialty.lower() in getattr(a, 'specialty', '').lower()]

# Singleton
agent_registry = AgentRegistry()

def init_default_agents():
    """Regista os 9 agentes-piloto do Local AI Brain + GOD + Builder + Provider Health"""
    from app.agents.research import ResearchAgent
    from app.agents.coding import CodingAgent
    from app.agents.design import DesignAgent
    from app.agents.business import BusinessAgent
    from app.agents.browser import BrowserAgent
    from app.agents.automation import AutomationAgent
    from app.agents.monitor import MonitorAgent
    from app.agents.builder import BuilderAgent
    from app.agents.provider_health import ProviderHealthAgent

    agents = [
        ResearchAgent(),
        CodingAgent(),
        DesignAgent(),
        BusinessAgent(),
        BrowserAgent(),
        AutomationAgent(),
        MonitorAgent(),
        BuilderAgent(),
        ProviderHealthAgent()
    ]
    for ag in agents:
        agent_registry.register(ag)
    return agent_registry
