"""
Brain Router — 8-10 agentes, provider_health e tools_health opcionais para Render
"""
from typing import Dict
import os

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

agent_registry = AgentRegistry()

def init_default_agents():
    from app.agents.research import ResearchAgent
    from app.agents.coding import CodingAgent
    from app.agents.design import DesignAgent
    from app.agents.business import BusinessAgent
    from app.agents.browser import BrowserAgent
    from app.agents.automation import AutomationAgent
    from app.agents.monitor import MonitorAgent
    from app.agents.builder import BuilderAgent

    agents = [
        ResearchAgent(),
        CodingAgent(),
        DesignAgent(),
        BusinessAgent(),
        BrowserAgent(),
        AutomationAgent(),
        MonitorAgent(),
        BuilderAgent()
    ]
    
    # Provider Health opcional — desativa no Render via DISABLE_PROVIDER_HEALTH=true
    if os.getenv('DISABLE_PROVIDER_HEALTH') != 'true':
        try:
            from app.agents.provider_health import ProviderHealthAgent
            agents.append(ProviderHealthAgent())
            print("[Router] Provider Health Agent registado — 9 agentes")
        except Exception as e:
            print(f"[Router] Provider Health não registado: {e} — 8 agentes")
    else:
        print("[Router] Provider Health desativado via env — 8 agentes")

    # Tools Health opcional — similar ao provider mas para tools
    if os.getenv('DISABLE_TOOLS_HEALTH') != 'true':
        try:
            from app.agents.tools_health import ToolsHealthAgent
            agents.append(ToolsHealthAgent())
            print(f"[Router] Tools Health Agent registado — {len(agents)} agentes")
        except Exception as e:
            print(f"[Router] Tools Health não registado: {e} — {len(agents)} agentes")
    else:
        print(f"[Router] Tools Health desativado via env — {len(agents)} agentes")

    for ag in agents:
        agent_registry.register(ag)
    return agent_registry
