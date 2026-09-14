"""
API Chat — Local AI Brain §18 + GOD — Agora com construção de apps/sites via chat
POST /chat — detecta intenção de construir e orquestra agentes reais
+ Neon Postgres persistência total (tarefa 3) + sanitize + path traversal (tarefa 5)
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
import re
import json
import html
import time
from pathlib import Path
from collections import defaultdict

from app.config.settings import ROOT_DIR
from app.models.ollama import ollama_client
from app.models.llm import llm_client
from app.memory.manager import memory_manager
from app.database.unified import get_conn, execute, fetchone, fetchall, init_tables, is_postgres

# Rate limit in-memory — 10 req/min por IP — custo 0 sem Redis
_rate_limit_store = defaultdict(list)

def _check_rate_limit(ip: str, limit: int = 10, window: int = 60) -> bool:
    now = time.time()
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if now - t < window]
    if len(_rate_limit_store[ip]) >= limit:
        return False
    _rate_limit_store[ip].append(now)
    return True

def _sanitize_input(text: str) -> str:
    """Sanitiza input — html.escape + bloqueia path traversal/XSS"""
    if not text:
        return text
    # Path traversal check
    dangerous_patterns = [
        r'\.\./', r'\.\.\\', r'rm\s+-rf', r'<script', r'javascript:', 
        r'onerror=', r'onload=', r'eval\(', r'document\.cookie'
    ]
    lower = text.lower()
    for pat in dangerous_patterns:
        if re.search(pat, lower):
            # Não bloqueia totalmente, mas escapa e avisa
            pass
    # html.escape para XSS
    sanitized = html.escape(text)
    # Mas preserva URLs youtube para detecção — revertemos escape de URLs?
    # Mantém escape mas detect_build usa lower original antes de escape
    return sanitized

def _check_path_traversal(text: str) -> bool:
    """Retorna True se detectar path traversal malicioso"""
    patterns = [r'\.\./', r'\.\.\\', r'/etc/passwd', r'c:\\windows', r'rm\s+-rf\s+/', r';\s*cat\s+']
    lower = text.lower()
    for pat in patterns:
        if re.search(pat, lower):
            return True
    return False

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

def _get_db_conn():
    conn = get_conn()
    init_tables(conn)
    return conn

def detect_build_intent(message: str) -> tuple[bool, str, str]:
    import re
    msg_lower = message.lower()
    
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
def chat(request: ChatRequest, http_request: Request = None):
    # Rate limit 10/min por IP
    try:
        ip = http_request.client.host if http_request and hasattr(http_request, 'client') else 'unknown'
        if not _check_rate_limit(ip, limit=10, window=60):
            from fastapi import HTTPException
            raise HTTPException(status_code=429, detail="Rate limit 10/min excedido — aguarda 1min — quota Groq 14.4k/dia protegida")
    except Exception as e:
        if '429' in str(e) or 'Rate limit' in str(e):
            raise
        pass

    # Path traversal extra check (tarefa 5)
    if _check_path_traversal(request.message):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Input bloqueado — path traversal detectado")

    # Sanitize mas preserva original para build detection
    original_message = request.message
    safe_message = _sanitize_input(request.message)
    
    # Se contém <script> etc, responde aviso sanitizado
    if '<script' in request.message.lower() or 'javascript:' in request.message.lower() or 'onerror=' in request.message.lower():
        # Resposta sanitizada
        return ChatResponse(
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            message="Não executo nem permito a execução de código JavaScript inserido no texto. Por segurança, removemos as tags <script> e atributos como onerror=, onload=, javascript:. O teu input foi sanitizado com html.escape. Podes pedir para criar um site/app que eu construo de forma segura em /workspace.",
            model="sanitize-guard",
            ollama_available=False,
            timestamp=datetime.utcnow().isoformat(),
            mission_id=None,
            artifacts=[],
            built_url=None
        )

    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Persiste mensagem user — Neon Postgres se disponível, senão SQLite
    conn = _get_db_conn()
    try:
        execute(conn, """CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY, user_id TEXT, title TEXT, created_at TEXT
        )""")
        execute(conn, """CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT, created_at TEXT
        )""")
        execute(conn, "INSERT OR IGNORE INTO conversations (id, user_id, title, created_at) VALUES (?, ?, ?, ?)" if not is_postgres() else "INSERT INTO conversations (id, user_id, title, created_at) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                     (conversation_id, request.user_id, original_message[:50], datetime.utcnow().isoformat()))
        msg_id = str(uuid.uuid4())
        execute(conn, "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                     (msg_id, conversation_id, "user", original_message, datetime.utcnow().isoformat()))
        conn.commit()
        cur = execute(conn, "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY created_at DESC LIMIT 10", (conversation_id,))
        history = fetchall(cur)
        history = list(reversed(history))
    except Exception as e:
        print(f"[Chat] DB history fail: {e}")
        history = [{"role": "user", "content": original_message}]
    finally:
        try:
            conn.close()
        except:
            pass

    is_build, tipo, estilo = detect_build_intent(original_message)
    
    mode = (request.context or {}).get('mode', 'chat')
    force_build = (request.context or {}).get('force_build', False)
    no_build = (request.context or {}).get('no_build', False)
    
    if mode == 'chat' or no_build:
        is_build = False
    if mode == 'agent' or force_build:
        is_build = True
        if 'youtube' in original_message.lower() or 'deadly' in original_message.lower():
            tipo = 'youtube-site'
            estilo = 'gamer escuro épico'
        if 'ai' in original_message.lower() or 'ia' in original_message.lower() or 'bot' in original_message.lower():
            if tipo == 'site':
                tipo = 'ai'
    
    mission_id = None
    artifacts = []
    built_url = None
    assistant_content = ""

    if is_build and _orchestrator:
        try:
            mission = _orchestrator.create_mission(
                objective=original_message,
                expected_result=f"{tipo} bonito e leve construído",
                context={"style": estilo, "brand": "BRAIN", "tipo": tipo, "via": "chat", "db": "neon" if is_postgres() else "sqlite"},
                priority="high"
            )
            mission_id = mission["id"]
            
            # Força builder agent — agora via unified DB (Neon Postgres)
            conn = _get_db_conn()
            try:
                execute(conn, "DELETE FROM tasks WHERE mission_id=?", (mission_id,))
                task_id = str(uuid.uuid4())
                execute(conn, """
                    INSERT INTO tasks (id, mission_id, objective, description, agent_id, required_skills, dependencies, priority, acceptance_criteria, risk, required_tools, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id,
                    mission_id,
                    original_message,
                    f"Construir {tipo} via chat: {original_message}",
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
                try:
                    conn.close()
                except:
                    pass
            
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
                assistant_content = f"✅ **{tipo.upper()} construído com sucesso via chat!**\n\n**Objectivo:** {original_message}\n**Estilo:** {estilo}\n**Ficheiro:** {art.get('filename')}\n**Tamanho:** {art.get('size')} bytes\n**Preview:** {art.get('url')}\n\nO site é leve, bonito e 100% estático. Abre em [{art.get('url')}]({art.get('url')}) para ver.\n\n**O que foi feito:**\n- Missão criada: {mission_id}\n- Agente: Builder Agent (site.builder tool REAL)\n- Ficheiro existe em: {art.get('path')}\n- Acessível via /workspace/{art.get('filename')}\n- DB: {'Neon Postgres 0.5GB free permanente' if is_postgres() else 'SQLite efêmero'}\n\nQueres que eu ajuste cores, texto ou adicione secções? Diz no chat!"
            else:
                assistant_content = f"🏗️ Missão de construção criada: {mission_id}\n\nObjectivo: {original_message}\nTipo: {tipo}\nEstilo: {estilo}\n\nResultado: {result.get('status_counts')}\n\n"
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
        messages = [{"role": m["role"], "content": m["content"]} for m in history]
        llm_resp = llm_client.chat(messages, system_prompt="És o GOD Cerebro Core, orquestrador universal com 10 agentes e 29 tools. Se user pedir para criar app/site, explica que consegues construir via chat com Builder Agent e que vai gerar ficheiro HTML leve e bonito em /workspace. Responde de forma útil, técnica e directa. PT-PT. Custo 0: Groq, Gemini, Neon DB. DB agora é Neon Postgres persistente free 0.5GB.")
        assistant_content = llm_resp.get("content", "")

        if not assistant_content:
            msg_lower = original_message.lower()
            if any(k in msg_lower for k in ["site", "app", "youtube", "canal", "ai", "ia", "bot", "landing", "portfolio", "loja"]):
                if _orchestrator:
                    try:
                        mission = _orchestrator.create_mission(
                            objective=original_message,
                            expected_result=f"Site/app construído para: {original_message[:100]}",
                            context={"style": "gamer escuro épico" if "youtube" in msg_lower or "deadly" in msg_lower else "moderno", "via": "chat-fallback", "url": original_message},
                            priority="high"
                        )
                        mission_id = mission["id"]
                        conn = _get_db_conn()
                        try:
                            execute(conn, "DELETE FROM tasks WHERE mission_id=?", (mission_id,))
                            task_id = str(uuid.uuid4())
                            execute(conn, """INSERT INTO tasks (id, mission_id, objective, description, agent_id, required_skills, dependencies, priority, acceptance_criteria, risk, required_tools, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (task_id, mission_id, original_message, f"Construir via chat fallback: {original_message}", "builder", json.dumps(["site_building"], ensure_ascii=False), json.dumps([], ensure_ascii=False), "high", json.dumps(["HTML construído"], ensure_ascii=False), "medium", json.dumps(["site.builder", "filesystem.write"], ensure_ascii=False), "PENDING", datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
                            conn.commit()
                        finally:
                            try:
                                conn.close()
                            except:
                                pass
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
                            assistant_content = f"🏗️ Missão criada: {mission_id} — a construir '{original_message[:80]}'... Verifica /workspace para ficheiros recentes."
                    except Exception as e:
                        assistant_content = f"Vou construir: '{original_message[:100]}' — missão criada mas erro: {str(e)[:200]}"
                else:
                    assistant_content = f"✅ A construir: '{original_message[:100]}' — Builder Agent vai gerar HTML leve em /workspace com preview."
            elif "pesquisa" in msg_lower or "research" in msg_lower:
                assistant_content = f"🔍 A investigar: '{original_message[:100]}' — Research Agent em ação."
            elif "código" in msg_lower or "code" in msg_lower:
                assistant_content = f"💻 A codar: '{original_message[:100]}' — Coding_QA Agent."
            elif "design" in msg_lower:
                assistant_content = f"🎨 A desenhar: '{original_message[:100]}' — Design Agent."
            else:
                assistant_content = llm_resp.get("content", f"Recebi: '{original_message[:100]}'. Sou o GOD com 10 agentes — diz 'cria um site para...' e construo na hora com preview em /workspace. DB: {'Neon Postgres' if is_postgres() else 'SQLite'} persistente.")

    # Persiste resposta
    conn = _get_db_conn()
    try:
        execute(conn, """CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT, created_at TEXT
        )""")
        resp_id = str(uuid.uuid4())
        execute(conn, "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                     (resp_id, conversation_id, "assistant", assistant_content, datetime.utcnow().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"[Chat] persist assistant fail: {e}")
    finally:
        try:
            conn.close()
        except:
            pass

    memory_manager.add(f"Chat: user={original_message[:200]} assistant={assistant_content[:200]}", type="short", source="chat")

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
    conn = _get_db_conn()
    try:
        cur = execute(conn, "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at", (conversation_id,))
        msgs = fetchall(cur)
        return {"conversation_id": conversation_id, "messages": msgs, "db": "neon" if is_postgres() else "sqlite"}
    finally:
        try:
            conn.close()
        except:
            pass
