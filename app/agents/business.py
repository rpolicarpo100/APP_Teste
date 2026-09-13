"""
Business & E-commerce Agent — GOD §4.4
Responsabilidades: analisar mercados, concorrência, modelos de negócio, sem inventar métricas
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput
import json

class BusinessAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="business", name="Business Agent", specialty="Negócio e e-commerce", version="1.0.0")
        self.skills = ["market_analysis", "competitor_analysis", "business_model", "kpi_analysis", "ecommerce_strategy"]
        self.tools = ["web.search", "web.fetch", "filesystem.read", "filesystem.write"]
        self.limitations = ["Não inventa vendas, tráfego, margens ou fornecedores", "Distingue dados reais de estimativas", "Não garante previsões"]

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = "RUNNING"
        try:
            valid, msg = self.validate_input(task_input)
            if not valid:
                return TaskOutput(task_id=task_input.task_id, status="failed", summary=f"Input inválido: {msg}", confidence="low", requires_review=True)

            objective = task_input.objective
            context = task_input.context
            evidence = []
            artifacts = []

            from app.tools.registry import tool_registry
            web_search = tool_registry.get_implementation("web.search")
            web_fetch = tool_registry.get_implementation("web.fetch")

            # Análise estruturada sem inventar
            market_data = context.get("market_data")
            competitor_urls = context.get("competitor_urls", [])
            costs = context.get("costs", {})

            # Pesquisa concorrência se URLs fornecidos
            if competitor_urls and web_fetch:
                for url in competitor_urls[:3]:
                    res = web_fetch(url)
                    evidence.append({"type": "competitor_fetch", "url": url, "length": res.get("length"), "status": res.get("status_code")})

            # Pesquisa geral
            if web_search:
                search_res = web_search(objective, count=3)
                evidence.append({"type": "market_search", "query": objective, "result": search_res})

            # Cálculo transparente de margens — apenas se dados fornecidos
            margin_calc = "NÃO CALCULADO — dados insuficientes"
            if costs and "cost" in costs and "price" in costs:
                try:
                    cost = float(costs["cost"])
                    price = float(costs["price"])
                    margin = ((price - cost) / price * 100) if price != 0 else 0
                    margin_calc = f"Custo: {cost} | Preço: {price} | Margem: {margin:.2f}% | Fórmula: (price-cost)/price*100"
                    evidence.append({"type": "margin_calc", "cost": cost, "price": price, "margin": margin, "formula": "(price-cost)/price*100"})
                except Exception as e:
                    margin_calc = f"Erro cálculo: {str(e)}"

            # Modelo de negócio estruturado
            business_model = {
                "objective": objective,
                "value_proposition": context.get("value_proposition", "A definir com dados reais"),
                "customer_segments": context.get("customer_segments", ["A definir"]),
                "channels": context.get("channels", ["Online"]),
                "cost_structure": costs if costs else "NÃO VERIFICADO — requer dados reais",
                "revenue_streams": context.get("revenue", "NÃO VERIFICADO"),
                "kpis": ["CAC", "LTV", "Margem", "Conversão", "Churn"] if not context.get("kpis") else context.get("kpis"),
                "risks": ["Operacional", "Financeiro", "Legal", "Mercado"],
                "data_status": "ESTIMATIVA" if not market_data else "VERIFICADO" if market_data.get("verified") else "NÃO VERIFICADO"
            }

            artifacts.append({"type": "business_model", "content": business_model})

            summary = f"Análise de negócio para: {objective}\n\n"
            summary += f"[Modelo de Negócio]\n{json.dumps(business_model, indent=2, ensure_ascii=False)}\n\n"
            summary += f"[Margem] {margin_calc}\n\n"
            summary += "[Riscos identificados]\n- Operacional: dependência de fornecedores não verificados\n- Financeiro: margens dependem de custos reais\n- Legal: requer verificação de regulamentação local\n- Mercado: concorrência não analisada sem dados reais\n\n"
            summary += "[Distinção Factos vs Estimativas]\n"
            summary += f"- Factos: objectivo = {objective}\n"
            summary += f"- Estimativas: {business_model['data_status']} — não apresentar como garantia\n"
            summary += f"- NÃO VERIFICADO: tráfego, vendas, fornecedores sem fonte\n\n"
            summary += "[Limitações] " + "; ".join(self.limitations)

            self.status = "READY"
            return TaskOutput(
                task_id=task_input.task_id,
                status="completed",
                summary=summary,
                artifacts=artifacts,
                evidence=evidence,
                confidence="low" if business_model["data_status"] != "VERIFICADO" else "medium",
                requires_review=True,
                limitations=self.limitations
            )
        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(task_id=task_input.task_id, status="failed", summary=f"Erro business: {str(e)}", confidence="low", requires_review=True)
