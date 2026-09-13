"""
Design Agent — GOD §4.3
Responsabilidades: interpretar briefings, criar propostas visuais, wireframes, specs UI/UX
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput

class DesignAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="design", name="Design Agent", specialty="Design e desenho", version="1.0.0")
        self.skills = ["ui_ux", "wireframing", "visual_concept", "brand_design", "spec_writing"]
        self.tools = ["filesystem.read", "filesystem.write", "web.search"]
        self.limitations = ["Não declara desenho tecnicamente certificado", "Proposta visual distingue-se de resultado final"]

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

            # Interpreta briefing
            briefing = context.get("briefing", objective)
            style = context.get("style", "moderno, minimalista")
            target = context.get("target_audience", "geral")

            # Cria proposta visual em formato texto + SVG inline (para preview sem dependências externas)
            svg_concept = f'''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="200" fill="#f5f5f5"/>
  <text x="20" y="40" font-family="Arial" font-size="16" font-weight="bold" fill="#333">Conceito: {objective[:40]}</text>
  <text x="20" y="70" font-family="Arial" font-size="12" fill="#666">Estilo: {style}</text>
  <text x="20" y="90" font-family="Arial" font-size="12" fill="#666">Público: {target}</text>
  <rect x="20" y="110" width="100" height="40" rx="8" fill="#4F46E5"/>
  <text x="70" y="135" font-family="Arial" font-size="12" fill="white" text-anchor="middle">CTA</text>
  <rect x="140" y="110" width="100" height="40" rx="8" fill="white" stroke="#ccc"/>
  <text x="190" y="135" font-family="Arial" font-size="12" fill="#333" text-anchor="middle">Secundário</text>
</svg>'''

            # Tenta salvar artefato
            from app.tools.registry import tool_registry
            fs_write = tool_registry.get_implementation("filesystem.write")
            if fs_write:
                # Salva SVG
                import uuid
                artifact_path = f"design_concept_{task_input.task_id[:8]}.svg"
                write_res = fs_write(artifact_path, svg_concept)
                evidence.append({"type": "artifact_write", "path": artifact_path, "result": write_res})
                artifacts.append({"type": "svg_concept", "path": artifact_path, "content": svg_concept})

            # Especificação UI/UX
            spec = f"""
# Especificação UI/UX — {objective}

## Briefing
{briefing}

## Requisitos visuais
- Estilo: {style}
- Público-alvo: {target}
- Tom: {context.get('tone', 'profissional e acessível')}

## Wireframe textual
[Header] Logo | Navegação | CTA
[Hero] Título + Subtítulo + Imagem conceito + CTA primário
[Features] 3 colunas com ícones
[Footer] Links + Contacto

## Paleta proposta
- Primária: #4F46E5 (Indigo)
- Secundária: #10B981 (Emerald)
- Neutro: #F5F5F5 / #333
- Alerta: #EF4444

## Tipografia
- Headings: Inter Bold
- Body: Inter Regular 16px
- Line-height: 1.6

## Coerência visual
- Raio de borda: 8px
- Sombra: 0 4px 6px rgba(0,0,0,0.1)
- Espaçamento: 8pt grid

## Nota legal
PROPOSTA — NÃO CERTIFICADA. Requer revisão humana para consequências técnicas ou legais.
"""
            artifacts.append({"type": "ui_spec", "content": spec})

            summary = f"Proposta de design criada para: {objective}\n"
            summary += f"- Estilo: {style}\n"
            summary += f"- Artefactos: {len(artifacts)} (SVG + spec)\n"
            summary += f"- Coerência visual mantida com sistema 8pt grid\n"
            summary += "\n[PROPOSTA — NÃO IMPLEMENTADA como desenho técnico certificado]"

            self.status = "READY"
            return TaskOutput(
                task_id=task_input.task_id,
                status="completed",
                summary=summary,
                artifacts=artifacts,
                evidence=evidence,
                confidence="medium",
                requires_review=True,
                limitations=self.limitations + ["Requer revisão humana"]
            )
        except Exception as e:
            self.status = "FAILED"
            return TaskOutput(task_id=task_input.task_id, status="failed", summary=f"Erro design: {str(e)}", confidence="low", requires_review=True)
