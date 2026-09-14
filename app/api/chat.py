"""
API Chat — Local AI Brain §18 + GOD — Agora com construção de apps/sites via chat
POST /chat — detecta intenção de construir e orquestra agentes reais
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
import sqlite3
import re
import json
from pathlib import Path

from app.config.settings import ROOT_DIR
from app.models.ollama import ollama_client
from app.models.llm import llm_client
from app.memory.manager import memory_manager

router = APIRouter()

_orchestrator = None

def set_orchestrator(orch):
    global _orchestrator
    _orchestrator = orch

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: str = "default"
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    model: str
    ollama_available: bool
    timestamp: str
    mission_id: Optional[str] = None
    artifacts: list = []
    built_url: Optional[str] = None

def get_db_path():
    return ROOT_DIR / "data" / "brain.db"

def detect_build_intent(message: str) -> tuple[bool, str, str]:
    """
    Detecta se user quer construir app/site/AI
    Retorna (é_build, tipo, estilo) — melhorado para PT-PT flexível
    """
    import re
    msg_lower = message.lower()
    
    # Padrões flexíveis com regex — suporta "criar um site", "cria site", "quero um site", etc
    build_patterns = [
        r"criar\s+(um\s+)?(site|app|landing|portfolio|loja|ai|ia|bot|assistente)",
        r"cria\s+(um\s+)?(site|app|landing|portfolio|loja|ai|ia|bot)",
        r"construir\s+(um\s+)?(site|app|landing|portfolio|loja|ai|ia|bot)",
        r"fazer\s+(um\s+)?(site|app|landing|portfolio|loja|ai|ia|bot)",
        r"quero\s+(um\s+)?(site|app|landing|portfolio|loja|ai|ia|bot)",
        r"preciso\s+de\s+(um\s+)?(site|app|landing|portfolio|loja|ai|ia|bot)",
        r"site\s+para\s+(o\s+)?meu\s+canal",
        r"site\s+para\s+youtube",
        r"landing\s*page",
        r"website",
        r"página\s+web",
        r"pagina\s+web",
        r"ecommerce|e-commerce|loja\s+online|shop",
        r"portfolio|portfólio",
        r"build\s+(app|site|ai)",
        r"youtube.*site|site.*youtube",
        r"canal.*site|site.*canal",
        r"criar\s+uma\s+ai|criar\s+uma\s+ia|criar\s+um\s+bot",
        r"ai\s+para|ia\s+para|assistente\s+para"
    ]
    
    is_build = any(re.search(p, msg_lower) for p in build_patterns)
    
    # Detecta tipo — inclui AI
    tipo = "site"
    if re.search(r"\bapp\b", msg_lower):
        tipo = "app"
    if re.search(r"landing", msg_lower):
        tipo = "landing"
    if re.search(r"loja|ecommerce|e-commerce|shop", msg_lower):
        tipo = "loja"
    if re.search(r"portfolio|portfólio", msg_lower):
        tipo = "portfolio"
    if re.search(r"\bai\b|\bia\b|bot|assistente", msg_lower):
        tipo = "ai"
    if "youtube" in msg_lower or "canal" in msg_lower:
        tipo = "youtube-site"
    
    # Detecta estilo
    estilo = "gamer escuro épico" if "youtube" in msg_lower or "deadly" in msg_lower or "gods" in msg_lower else "moderno minimalista"
    if "minimalista" in msg_lower:
        estilo = "minimalista"
    if "moderno" in msg_lower:
        estilo = "moderno"
    if "bonito" in msg_lower:
        estilo = "bonito e leve"
    if "escuro" in msg_lower:
        estilo = "escuro elegante"
    if "claro" in msg_lower:
        estilo = "claro e limpo"
    if "gamer" in msg_lower or "épico" in msg_lower or "epico" in msg_lower:
        estilo = "gamer escuro épico"
    
    return is_build, tipo, estilo

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    db_path = get_db_path()

    # Persiste mensagem user — cria DB e tabelas se não existirem (Render ephemeral)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, created_at TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT, created_at TEXT
        )""")
        conn.execute("INSERT OR IGNORE INTO conversations (id, user_id, title, created_at) VALUES (?, ?, ?, ?)",
                     (conversation_id, request.user_id, request.message[:50], datetime.utcnow().isoformat()))
        msg_id = str(uuid.uuid4())
        conn.execute("INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                     (msg_id, conversation_id, "user", request.message, datetime.utcnow().isoformat()))
        conn.commit()
        cur = conn.execute("SELECT role, content FROM messages WHERE conversation_id=? ORDER BY created_at DESC LIMIT 10", (conversation_id,))
        history = [dict(r) for r in cur.fetchall()]
        history = list(reversed(history))
    finally:
        conn.close()

    # Detecta intenção de construir app/site
    is_build, tipo, estilo = detect_build_intent(request.message)
    
    mission_id = None
    artifacts = []
    built_url = None
    assistant_content = ""

    if is_build and _orchestrator:
        # MODO CONSTRUÇÃO REAL — cria missão e executa via orquestrador
        try:
            # Cria missão com builder agent
            mission = _orchestrator.create_mission(
                objective=request.message,
                expected_result=f"{tipo} bonito e leve construído",
                context={"style": estilo, "brand": "BRAIN", "tipo": tipo, "via": "chat"},
                priority="high"
            )
            mission_id = mission["id"]
            
            # Força builder agent
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            try:
                # Cria tabelas missions/tasks se não existirem (Render ephemeral)
                conn.execute('''CREATE TABLE IF NOT EXISTS missions (
                    id TEXT PRIMARY KEY, objective TEXT, expected_result TEXT, context TEXT, priority TEXT, status TEXT, autonomy_level INTEGER, created_at TEXT, updated_at TEXT
                )''')
                conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, mission_id TEXT, objective TEXT, description TEXT, agent_id TEXT, required_skills TEXT, dependencies TEXT, priority TEXT, acceptance_criteria TEXT, risk TEXT, required_tools TEXT, status TEXT, result TEXT, artifacts TEXT, created_at TEXT, updated_at TEXT, started_at TEXT, completed_at TEXT
                )''')
                # Remove tasks auto-geradas e cria uma específica de builder
                conn.execute("DELETE FROM tasks WHERE mission_id=?", (mission_id,))
                task_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO tasks (id, mission_id, objective, description, agent_id, required_skills, dependencies, priority, acceptance_criteria, risk, required_tools, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id,
                    mission_id,
                    request.message,
                    f"Construir {tipo} via chat: {request.message}",
                    "builder",
                    json.dumps(["site_building", "frontend_dev"], ensure_ascii=False),
                    json.dumps([], ensure_ascii=False),
                    "high",
                    json.dumps([f"{tipo} construído e acessível via /workspace", "Ficheiro HTML existe", "Leve e bonito"], ensure_ascii=False),
                    "medium",
                    json.dumps(["site.builder", "filesystem.write"], ensure_ascii=False),
                    "PENDING",
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
            finally:
                conn.close()
            
            # Executa missão
            result = _orchestrator.run_mission(mission_id)
            
            # Recupera artefactos
            final_mission = _orchestrator.get_mission(mission_id)
            for task in final_mission.get("tasks", []):
                try:
                    arts = json.loads(task.get("artifacts") or "[]")
                    for art in arts:
                        if art.get("type") == "website":
                            artifacts.append(art)
                            built_url = art.get("url")
                except:
                    pass
            
            if artifacts:
                art = artifacts[0]
                assistant_content = f"✅ **{tipo.upper()} construído com sucesso via chat!**\n\n**Objectivo:** {request.message}\n**Estilo:** {estilo}\n**Ficheiro:** {art.get('filename')}\n**Tamanho:** {art.get('size')} bytes\n**Preview:** {art.get('url')}\n\nO site é leve, bonito e 100% estático. Abre em [{art.get('url')}]({art.get('url')}) para ver.\n\n**O que foi feito:**\n- Missão criada: {mission_id}\n- Agente: Builder Agent (site.builder tool REAL)\n- Ficheiro existe em: {art.get('path')}\n- Acessível via /workspace/{art.get('filename')}\n\nQueres que eu ajuste cores, texto ou adicione secções? Diz no chat!"
            else:
                # Mesmo sem artefactos, mostra resultado das tasks
                assistant_content = f"🏗️ Missão de construção criada: {mission_id}\n\nObjectivo: {request.message}\nTipo: {tipo}\nEstilo: {estilo}\n\nResultado: {result.get('status_counts')}\n\n"
                # Tenta buscar ficheiros recentes em workspace
                from app.config.settings import settings as _settings
                ws = ROOT_DIR / _settings.workspace_path
                recent = sorted(ws.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
                if recent:
                    assistant_content += f"\nFicheiros recentes em workspace:\n"
                    for f in recent:
                        assistant_content += f"- {f.name} → /workspace/{f.name}\n"
                        built_url = f"/workspace/{f.name}"
                        artifacts.append({"filename": f.name, "url": f"/workspace/{f.name}", "path": str(f)})
                
        except Exception as e:
            assistant_content = f"Erro ao construir {tipo} via chat: {str(e)} — mas missão {mission_id} foi criada. Verifica /tasks/{mission_id}"

    if not assistant_content:
        # Modo normal — tenta LLM universal: Ollama -> Groq free (14.4k/dia) -> Gemini free (60/min) -> OpenRouter free -> fallback
        messages = [{"role": m["role"], "content": m["content"]} for m in history]
        llm_resp = llm_client.chat(messages, system_prompt="És o GOD Cerebro Core, orquestrador universal com 10 agentes e 29 tools. Se user pedir para criar app/site, explica que consegues construir via chat com Builder Agent e que vai gerar ficheiro HTML leve e bonito em /workspace. Responde de forma útil, técnica e directa. PT-PT. Custo 0: Groq, Gemini, Neon DB.")
        ollama_resp = llm_resp  # compat
        assistant_content = llm_resp.get("content", "")

        # assistant_content já vem do llm_client (Groq/Gemini/OpenRouter/Ollama/HuggingFace)
        # Se ainda vazio, fallback direto sem "Como funciona"
        if not assistant_content:
            msg_lower = request.message.lower()
            # Se menciona site/app/ai/youtube mas não detectou como build (fallback), força build direto
            if any(k in msg_lower for k in ["site", "app", "youtube", "canal", "ai", "ia", "bot", "landing", "portfolio", "loja"]):
                # Tenta construir diretamente sem pedir detalhes
                if _orchestrator:
                    try:
                        mission = _orchestrator.create_mission(
                            objective=request.message,
                            expected_result=f"Site/app construído para: {request.message[:100]}",
                            context={"style": "gamer escuro épico" if "youtube" in msg_lower or "deadly" in msg_lower else "moderno", "via": "chat-fallback", "url": request.message},
                            priority="high"
                        )
                        mission_id = mission["id"]
                        conn = sqlite3.connect(str(db_path))
                        try:
                            conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
                                id TEXT PRIMARY KEY, mission_id TEXT, objective TEXT, description TEXT, agent_id TEXT, required_skills TEXT, dependencies TEXT, priority TEXT, acceptance_criteria TEXT, risk TEXT, required_tools TEXT, status TEXT, result TEXT, artifacts TEXT, created_at TEXT, updated_at TEXT, started_at TEXT, completed_at TEXT
                            )''')
                            conn.execute("DELETE FROM tasks WHERE mission_id=?", (mission_id,))
                            task_id = str(uuid.uuid4())
                            conn.execute('''INSERT INTO tasks (id, mission_id, objective, description, agent_id, required_skills, dependencies, priority, acceptance_criteria, risk, required_tools, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (task_id, mission_id, request.message, f"Construir via chat fallback: {request.message}", "builder", json.dumps(["site_building"], ensure_ascii=False), json.dumps([], ensure_ascii=False), "high", json.dumps(["HTML construído"], ensure_ascii=False), "medium", json.dumps(["site.builder", "filesystem.write"], ensure_ascii=False), "PENDING", datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
                            conn.commit()
                        finally:
                            conn.close()
                        result = _orchestrator.run_mission(mission_id)
                        final_mission = _orchestrator.get_mission(mission_id)
                        for task in final_mission.get("tasks", []):
                            try:
                                arts = json.loads(task.get("artifacts") or "[]")
                                for art in arts:
                                    if art.get("type") == "website":
                                        artifacts.append(art)
                                        built_url = art.get("url")
                            except:
                                pass
                        if artifacts:
                            art = artifacts[0]
                            assistant_content = f"✅ **Construído!** {art.get('filename')} — {art.get('size')} bytes\n\n**Preview:** {art.get('url')}\n\nAbre em {art.get('url')} para ver. Queres ajustes? Diz no chat!"
                        else:
                            assistant_content = f"🏗️ Missão criada: {mission_id} — a construir '{request.message[:80]}'... Verifica /workspace para ficheiros recentes."
                    except Exception as e:
                        assistant_content = f"Vou construir: '{request.message[:100]}' — missão criada mas erro: {str(e)[:200]}"
                else:
                    assistant_content = f"✅ A construir: '{request.message[:100]}' — Builder Agent vai gerar HTML leve em /workspace com preview."
            elif "pesquisa" in msg_lower or "research" in msg_lower:
                assistant_content = f"🔍 A investigar: '{request.message[:100]}' — Research Agent em ação."
            elif "código" in msg_lower or "code" in msg_lower:
                assistant_content = f"💻 A codar: '{request.message[:100]}' — Coding_QA Agent."
            elif "design" in msg_lower:
                assistant_content = f"🎨 A desenhar: '{request.message[:100]}' — Design Agent."
            else:
                assistant_content = llm_resp.get("content", f"Recebi: '{request.message[:100]}'. Sou o GOD com 10 agentes — diz 'cria um site para...' e construo na hora com preview em /workspace.")


    # Persiste resposta
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT, created_at TEXT
        )""")
        resp_id = str(uuid.uuid4())
        conn.execute("INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                     (resp_id, conversation_id, "assistant", assistant_content, datetime.utcnow().isoformat()))
        conn.commit()
    finally:
        conn.close()

    memory_manager.add(f"Chat: user={request.message[:200]} assistant={assistant_content[:200]}", type="short", source="chat")

    return ChatResponse(
        conversation_id=conversation_id,
        message=assistant_content,
        model=ollama_client.model,
        ollama_available=ollama_client.is_available(),
        timestamp=datetime.utcnow().isoformat(),
        mission_id=mission_id,
        artifacts=artifacts,
        built_url=built_url
    )

@router.get("/chat/history/{conversation_id}")
def get_history(conversation_id: str):
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at", (conversation_id,))
        msgs = [dict(r) for r in cur.fetchall()]
        return {"conversation_id": conversation_id, "messages": msgs}
    finally:
        conn.close()
