# GOD — Cerebro Core / Local AI Brain v1.0

> Orquestrador Universal de Agentes de IA — implementação real, verificável e extensível

## Arquitectura

```
┌─────────────────────────┐
│       AI BRAIN UI       │  frontend/index.html
│      Desktop/Web        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       FastAPI            │  app/main.py + app/api/*
│      API Gateway         │
└────────────┬────────────┘
             │
             ▼
┌────────────────────────────────────┐
│             ORCHESTRATOR            │  app/brain/orchestrator.py
│  Planner → Executor → Validator    │
└───────────────┬────────────────────┘
                │
  ┌─────────────┼──────────────────────┐
  │             │                      │
  ▼             ▼                      ▼
Agents       Tools                  Memory
  │             │                      │
  ├─ Research   ├─ Web                ├─ Short
  ├─ Browser    ├─ Browser             ├─ Long
  ├─ Automation ├─ Filesystem          ├─ Episodic
  ├─ Coding     ├─ Python              └─ Semantic
  └─ Monitor    └─ Scheduler
                ▼
         ┌─────────────┐
         │   Ollama    │  app/models/ollama.py
         │ Local LLM   │
         └─────────────┘
                │
                ▼
           SQLite DB  data/brain.db
```

## Estrutura

```
ai-brain/
├── app/
│   ├── main.py                 # FastAPI entry
│   ├── brain/
│   │   ├── orchestrator.py     # Cérebro operacional
│   │   ├── planner.py          # Só planeia, não executa
│   │   ├── executor.py         # Verifica permissões + executa
│   │   ├── validator.py        # Nunca confia cegamente
│   │   ├── router.py           # Agent Registry
│   │   └── state.py            # Máquina de estados formal
│   ├── agents/
│   │   ├── base.py             # Contrato Universal GOD §6
│   │   ├── research.py         # Investigação profunda
│   │   ├── coding.py           # Coding & QA
│   │   ├── design.py           # Design
│   │   ├── business.py         # Negócio e e-commerce
│   │   ├── browser.py          # Browser (Playwright)
│   │   ├── automation.py       # Automação
│   │   └── monitor.py          # Monitor
│   ├── tools/
│   │   ├── registry.py         # Tool Registry
│   │   ├── filesystem.py       # Leitura/escrita controlada
│   │   ├── web.py              # web.search + web.fetch
│   │   ├── python.py           # Execução controlada
│   │   ├── scheduler.py        # APScheduler
│   │   └── browser.py          # Playwright wrapper
│   ├── memory/
│   │   ├── manager.py          # Manager SQLite
│   │   ├── short_term.py
│   │   ├── long_term.py
│   │   ├── episodic.py         # TASK, ACTION, RESULT, LESSON
│   │   └── semantic.py
│   ├── security/
│   │   ├── permissions.py      # RBAC + autonomy levels
│   │   ├── policies.py         # Path restrictions + injection check
│   │   ├── approval.py         # Approval system
│   │   └── audit.py            # Audit logs + eventos §21
│   ├── models/
│   │   └── ollama.py           # Ollama client
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── schema.sql
│   ├── api/
│   │   ├── chat.py
│   │   ├── tasks.py
│   │   ├── agents.py
│   │   ├── memory.py
│   │   ├── approvals.py
│   │   └── system.py
│   └── config/
│       └── settings.py
├── frontend/
│   └── index.html              # Dashboard
├── data/
│   ├── brain.db
│   ├── workspace/              # Ficheiros de trabalho
│   ├── documents/
│   ├── memory/
│   ├── logs/
│   └── cache/
├── tests/
├── scripts/
├── requirements.txt
└── .env.example
```

## Instalação

```bash
git clone <repo>
cd ai-brain
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou source .venv/bin/activate # Linux/Mac

pip install -r requirements.txt
playwright install chromium  # opcional

# Ollama (opcional, para LLM local)
ollama pull qwen3:8b

python -m app.main
# API em http://127.0.0.1:8000
# Docs em http://127.0.0.1:8000/docs
# Dashboard em http://127.0.0.1:8000/dashboard
```

## Ciclo de execução

```
ANALISAR → PLANEAR → SELECCIONAR AGENTES → SELECCIONAR FERRAMENTAS → VALIDAR PERMISSÕES → EXECUTAR → MONITORIZAR → VALIDAR → AUDITAR → ENTREGAR
```

### Regra de segurança fundamental

> **O LLM não controla directamente o computador. O LLM pede acções ao Brain e o Brain decide se essas acções são permitidas.**

## Estados

Missão: PENDING → PLANNING → WAITING_APPROVAL → READY → RUNNING → VALIDATING → COMPLETED
Tarefa: PENDING → READY → RUNNING → SUCCEEDED / FAILED / BLOCKED

Transições validadas em `app/brain/state.py` — impede PENDING→SUCCEEDED directo.

## Testes v1.0

Conforme spec §28:

- Teste 1 — Chat: User → Brain → LLM → resposta
- Teste 2 — Research: User → Research Agent → pesquisa → relatório
- Teste 3 — Tool: Agent → Tool Registry → tool → resultado
- Teste 4 — Permission: Agent → acção proibida → BLOCK
- Teste 5 — Approval: Agent → acção sensível → Approval → User → Execute
- Teste 6 — Memory: Task A → Memory → Task B recupera experiência
- Teste 7 — Automation: Schedule → Task → Agent → Result
- Teste 8 — Recovery: FAIL → retry → log → notify
- Teste 9 — Safety: nenhum agente apaga sistema, lê credenciais, etc.

## Agentes-piloto

- **research**: pesquisa profunda, distingue factos de hipóteses
- **coding_qa**: inspecciona código, executa testes, não declara sucesso sem executar
- **design**: propostas visuais SVG inline, specs UI/UX, distingue proposta de desenho certificado
- **business**: analisa mercado sem inventar métricas, margens com fórmula transparente
- **browser**: Playwright wrapper (CAPACIDADE NÃO DISPONÍVEL se não instalado)
- **automation**: workflows + scheduler
- **monitor**: health checks

## MVP Checklist

- [x] Cerebro recebe missão
- [x] Sistema cria tarefas estruturadas
- [x] Agent Registry funciona
- [x] 4 agentes-piloto + 3 extra integrados
- [x] Sistema delega a agentes reais
- [x] Contratos validados
- [x] Dependências respeitadas
- [x] Estados persistentes
- [x] Resultados registados
- [x] Falhas tratadas
- [x] Permissões aplicadas
- [x] Testes executáveis
- [x] Auditoria produz evidência
- [x] Sistema não inventa execuções
- [x] Sem regressões (greenfield)
- [x] Utilizador consulta estado das missões via API/dashboard
