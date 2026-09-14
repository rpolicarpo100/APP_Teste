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
    Detecta se user quer construir app/site
    Retorna (é_build, tipo, estilo)
    """
    msg_lower = message.lower()
    
    build_keywords = [
        "criar app", "cria app", "construir app", "fazer app",
        "criar site", "cria site", "construir site", "fazer site",
        "landing page", "website", "página web", "pagina web",
        "criar landing", "cria landing", "portfolio", "portfólio",
        "loja online", "ecommerce", "e-commerce", "shop",
        "app de", "site de", "constrói", "build app", "build site"
    ]
    
    is_build = any(kw in msg_lower for kw in build_keywords)
    
    # Detecta tipo
    tipo = "site"
    if "app" in msg_lower:
        tipo = "app"
    if "landing" in msg_lower:
        tipo = "landing"
    if "loja" in msg_lower or "ecommerce" in msg_lower or "shop" in msg_lower:
        tipo = "loja"
    if "portfolio" in msg_lower or "portfólio" in msg_lower:
        tipo = "portfolio"
    
    # Detecta estilo
    estilo = "moderno minimalista"
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

        # assistant_content já vem do llm_client (Groq/Gemini/OpenRouter/Ollama)
        if not assistant_content:
            msg_lower = request.message.lower()
            if "app" in msg_lower or "site" in msg_lower:
                assistant_content = f"Queres construir: '{request.message}'? Consigo! Vou criar uma missão com Builder Agent que gera HTML bonito e leve em data/workspace. Diz por exemplo: 'Cria um site de trading minimalista' ou 'Cria uma landing page para loja online' e eu construo na hora com preview em /workspace."
            elif "pesquisa" in msg_lower or "research" in msg_lower:
                assistant_content = f"Entendi: '{request.message}'. Posso criar missão de investigação com Research Agent."
            elif "código" in msg_lower or "code" in msg_lower:
                assistant_content = f"Pedido coding: '{request.message}'. Delego ao Coding_QA Agent."
            elif "design" in msg_lower:
                assistant_content = f"Pedido design: '{request.message}'. Design Agent cria SVG + spec."
            elif "negócio" in msg_lower or "negocio" in msg_lower:
                assistant_content = f"Pedido negócio: '{request.message}'. Business Agent com cálculo margem transparente."
            else:
                assistant_content = f"Recebi: '{request.message}'. Sou o Brain — DASHBOARD | CHAT | NEGÓCIOS | DEFINIÇÕES. Pelo CHAT consigo construir apps e sites reais — diz 'Cria um site...' e eu gero HTML leve e bonito com preview. LLM: {llm_resp.get('provider','fallback')} disponível: {llm_resp.get('available', False)} — Custo 0: GROQ_API_KEY free 14.4k/dia em console.groq.com"


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
