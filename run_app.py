"""
AI Brain — Launcher leve e bonito para PC
Abre o servidor e o browser automaticamente
"""
import webbrowser
import time
import threading
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from app.config.settings import settings
from app.database.connection import init_db
from app.brain.router import init_default_agents
from app.tools.registry import tool_registry
import app.tools.filesystem, app.tools.web, app.tools.python, app.tools.scheduler, app.tools.browser

def open_browser_delayed():
    time.sleep(1.5)
    url = f"http://127.0.0.1:{settings.app_port}/dashboard"
    print(f"🌸 Abrindo {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Abre manualmente: {url} — {e}")

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════╗
    ║  🧠 AI BRAIN — Leve & Bonita      ║
    ║  GOD Cerebro Core v1.0            ║
    ║  100% local, sem cloud            ║
    ╚════════════════════════════════════╝
    """)
    settings.resolve_paths()
    init_db()
    reg = init_default_agents()
    print(f"✅ {len(reg.list_agents())} agentes prontos")
    print(f"✅ {len(tool_registry.list_available())} ferramentas")
    print(f"✅ DB: data/brain.db")
    print(f"✅ Dashboard: http://127.0.0.1:{settings.app_port}/dashboard")
    print(f"✅ Docs: http://127.0.0.1:{settings.app_port}/docs")
    print("")
    print("💡 Dica: Deixa esta janela aberta. Fecha com Ctrl+C para parar.")
    print("")

    # Abre browser em thread separada
    threading.Thread(target=open_browser_delayed, daemon=True).start()

    # Inicia servidor
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.app_port, log_level="info")
