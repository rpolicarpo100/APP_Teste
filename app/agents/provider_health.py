"""
Provider Health Agent — Verifica se providers do cérebro estão a funcionar, faz failover e ranking por experiência
GOD §5 + novo requisito: agente que verifica providers, troca por outro se falhar, ranking por experiência
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput
from datetime import datetime
import sqlite3
import time
import httpx
from pathlib import Path
import json
import os

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"

PROVIDERS_CONFIG = {
    "coingecko": {
        "name": "CoinGecko",
        "type": "external_api",
        "url": "https://api.coingecko.com/api/v3/ping",
        "alternatives": ["coingecko_pro", "coinmarketcap", "coindesk"],
        "category": "crypto",
        "critical": True
    },
    "yahoo_finance": {
        "name": "Yahoo Finance",
        "type": "external_api",
        "url": "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=1d&interval=1d",
        "alternatives": ["alpha_vantage", "finnhub", "yahoo_backup"],
        "category": "stocks",
        "critical": True
    },
    "google_news_pt": {
        "name": "Google News PT",
        "type": "rss",
        "url": "https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt",
        "alternatives": ["newsapi", "rss_backup", "google_news_world"],
        "category": "news",
        "critical": False
    },
    "google_news_world": {
        "name": "Google News World",
        "type": "rss",
        "url": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
        "alternatives": ["newsapi", "bbc_rss"],
        "category": "news",
        "critical": False
    },
    "coindesk": {
        "name": "CoinDesk RSS",
        "type": "rss",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "alternatives": ["cointelegraph", "coingecko"],
        "category": "crypto",
        "critical": False
    },
    "ollama": {
        "name": "Ollama LLM",
        "type": "llm",
        "url": "http://127.0.0.1:11434/api/tags",
        "alternatives": ["openai", "fallback_local", "qwen_local"],
        "category": "llm",
        "critical": False
    },
    "filesystem": {
        "name": "Filesystem Tool",
        "type": "tool",
        "url": "internal",
        "alternatives": ["memory_only"],
        "category": "tool",
        "critical": True
    },
    "database": {
        "name": "SQLite Brain DB",
        "type": "internal",
        "url": "internal",
        "alternatives": ["memory_fallback"],
        "category": "internal",
        "critical": True
    }
}

def ensure_provider_tables():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS provider_rankings (
        provider_id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        category TEXT,
        success_count INTEGER DEFAULT 0,
        fail_count INTEGER DEFAULT 0,
        consecutive_fails INTEGER DEFAULT 0,
        avg_latency_ms REAL DEFAULT 0,
        last_latency_ms REAL DEFAULT 0,
        last_check TIMESTAMP,
        last_success TIMESTAMP,
        last_fail TIMESTAMP,
        status TEXT DEFAULT 'unknown',
        score REAL DEFAULT 0,
        rank INTEGER DEFAULT 999,
        alternative_in_use TEXT,
        experience_points INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS provider_health_history (
        id TEXT PRIMARY KEY,
        provider_id TEXT,
        check_time TIMESTAMP,
        status TEXT,
        latency_ms REAL,
        error TEXT,
        score REAL,
        FOREIGN KEY(provider_id) REFERENCES provider_rankings(provider_id)
    )
    """)
    # Seed providers if not exists
    for pid, cfg in PROVIDERS_CONFIG.items():
        cur.execute("SELECT provider_id FROM provider_rankings WHERE provider_id=?", (pid,))
        if not cur.fetchone():
            cur.execute("""
            INSERT INTO provider_rankings (provider_id, name, type, category, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'unknown', ?, ?)
            """, (pid, cfg["name"], cfg["type"], cfg["category"], datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

try:
    ensure_provider_tables()
except Exception as e:
    print(f"[ProviderHealth] Erro ao criar tabelas: {e}")


class ProviderHealthAgent(BaseAgent):
    def __init__(self):
        try:
            ensure_provider_tables()
        except Exception as e:
            print(f"[ProviderHealth] Erro ensure tables no __init__: {e}")
        super().__init__(
            agent_id="provider_health",
            name="Provider Health & Rank Agent",
            specialty="Verifica providers, failover automático e ranking por experiência",
            version="1.0.0"
        )
        self.skills = ["provider_check", "health_monitoring", "failover", "ranking", "experience_learning", "auto_healing"]
        self.tools = ["web.fetch", "filesystem.read", "filesystem.write", "provider.health_check", "provider.ranking"]
        self.limitations = ["Não pode criar novos providers, só rankear e fazer failover entre existentes"]

    def _check_provider(self, provider_id: str, config: dict) -> dict:
        """Verifica um provider e retorna resultado"""
        import os
        if os.getenv('DISABLE_PROVIDER_CHECK') == 'true':
            return {
                "provider_id": provider_id,
                "name": config["name"],
                "status": "ok",
                "latency_ms": 10,
                "error": None,
                "timestamp": datetime.utcnow().isoformat(),
                "mock": True
            }
        start = time.time()
        result = {
            "provider_id": provider_id,
            "name": config["name"],
            "status": "fail",
            "latency_ms": 0,
            "error": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            if config["type"] in ["external_api", "rss", "llm"]:
                if config["url"] == "internal":
                    # Check internal
                    if provider_id == "filesystem":
                        # Test filesystem
                        test_path = DB_PATH.parent / "workspace" / ".health_check"
                        try:
                            test_path.write_text("ok")
                            test_path.unlink()
                            result["status"] = "ok"
                        except Exception as e:
                            result["error"] = str(e)[:200]
                    elif provider_id == "database":
                        conn = sqlite3.connect(str(DB_PATH))
                        cur = conn.cursor()
                        cur.execute("SELECT 1")
                        conn.close()
                        result["status"] = "ok"
                else:
                    # External HTTP check
                    with httpx.Client(timeout=8, headers={"User-Agent": "AI-Brain-Health/1.0"}, follow_redirects=True) as client:
                        resp = client.get(config["url"])
                        latency = (time.time() - start) * 1000
                        result["latency_ms"] = round(latency, 1)
                        if resp.status_code == 200:
                            result["status"] = "ok"
                        else:
                            result["status"] = "degraded" if resp.status_code < 500 else "fail"
                            result["error"] = f"HTTP {resp.status_code}"
            else:
                result["status"] = "ok"
                result["latency_ms"] = round((time.time() - start) * 1000, 1)
                
        except Exception as e:
            result["latency_ms"] = round((time.time() - start) * 1000, 1)
            result["status"] = "fail"
            result["error"] = str(e)[:200]
        
        return result

    def _calculate_score(self, success_count: int, fail_count: int, avg_latency: float, consecutive_fails: int, experience: int) -> float:
        """Calcula score baseado em experiência"""
        total = success_count + fail_count
        if total == 0:
            success_rate = 0.5
        else:
            success_rate = success_count / total
        
        # Penaliza latência alta (quanto menor latência, melhor)
        latency_score = 1.0
        if avg_latency > 0:
            # Normaliza: 0-1000ms = 1.0 a 0.1
            latency_score = max(0.1, 1.0 - (avg_latency / 2000))
        
        # Penaliza fails consecutivos
        fail_penalty = max(0, 1.0 - (consecutive_fails * 0.3))
        
        # Bonus por experiência
        exp_bonus = min(0.3, experience / 100)
        
        score = (success_rate * 0.5 + latency_score * 0.3 + fail_penalty * 0.2) + exp_bonus
        return round(min(1.0, max(0, score)), 3)

    def _update_ranking(self, check_result: dict):
        """Atualiza ranking na BD"""
        try:
            ensure_provider_tables()
        except:
            pass
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        
        pid = check_result["provider_id"]
        cur.execute("SELECT * FROM provider_rankings WHERE provider_id=?", (pid,))
        row = cur.fetchone()
        
        if not row:
            conn.close()
            return
        
        # Get current values
        cur.execute("SELECT success_count, fail_count, avg_latency_ms, consecutive_fails, experience_points FROM provider_rankings WHERE provider_id=?", (pid,))
        data = cur.fetchone()
        success_count, fail_count, avg_latency, consecutive_fails, exp = data
        
        if check_result["status"] == "ok":
            success_count += 1
            consecutive_fails = 0
            exp += 2  # Ganha experiência por sucesso
            # Update avg latency (moving average)
            if avg_latency == 0:
                avg_latency = check_result["latency_ms"]
            else:
                avg_latency = (avg_latency * 0.8 + check_result["latency_ms"] * 0.2)
            last_success = datetime.utcnow().isoformat()
            last_fail = None
            status = "ok"
            alternative = None
        else:
            fail_count += 1
            consecutive_fails += 1
            exp = max(0, exp - 1)  # Perde experiência por falha
            last_success = None
            last_fail = datetime.utcnow().isoformat()
            status = "fail" if consecutive_fails >= 2 else "degraded"
            # Failover: escolhe alternativa se falhou muito
            config = PROVIDERS_CONFIG.get(pid, {})
            alternatives = config.get("alternatives", [])
            alternative = alternatives[0] if alternatives and consecutive_fails >= 3 else None
        
        score = self._calculate_score(success_count, fail_count, avg_latency, consecutive_fails, exp)
        
        cur.execute("""
        UPDATE provider_rankings SET
            success_count=?, fail_count=?, consecutive_fails=?, 
            avg_latency_ms=?, last_latency_ms=?, last_check=?,
            last_success=COALESCE(?, last_success),
            last_fail=COALESCE(?, last_fail),
            status=?, score=?, alternative_in_use=?,
            experience_points=?, updated_at=?
        WHERE provider_id=?
        """, (
            success_count, fail_count, consecutive_fails,
            round(avg_latency, 1), check_result["latency_ms"], datetime.utcnow().isoformat(),
            last_success if check_result["status"]=="ok" else None,
            last_fail if check_result["status"]!="ok" else None,
            status, score, alternative,
            exp, datetime.utcnow().isoformat(),
            pid
        ))
        
        # Insert history
        import uuid
        cur.execute("""
        INSERT INTO provider_health_history (id, provider_id, check_time, status, latency_ms, error, score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            pid,
            datetime.utcnow().isoformat(),
            check_result["status"],
            check_result["latency_ms"],
            check_result.get("error"),
            score
        ))
        
        conn.commit()
        
        # Update ranks
        cur.execute("SELECT provider_id, score FROM provider_rankings ORDER BY score DESC, success_count DESC")
        ranked = cur.fetchall()
        for rank, (provider_id, _) in enumerate(ranked, 1):
            cur.execute("UPDATE provider_rankings SET rank=? WHERE provider_id=?", (rank, provider_id))
        
        conn.commit()
        conn.close()

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = self.status.RUNNING if hasattr(self.status, 'RUNNING') else "RUNNING"
        
        objective = task_input.objective.lower()
        
        # Se pedido específico de provider
        if "ranking" in objective or "rank" in objective:
            return self._get_ranking(task_input)
        elif "health" in objective or "check" in objective or "verificar" in objective:
            return self._check_all_providers(task_input)
        else:
            # Default: check all
            return self._check_all_providers(task_input)

    def _check_all_providers(self, task_input: TaskInput) -> TaskOutput:
        results = []
        for pid, config in PROVIDERS_CONFIG.items():
            check = self._check_provider(pid, config)
            self._update_ranking(check)
            results.append(check)
        
        # Summary
        ok_count = len([r for r in results if r["status"] == "ok"])
        fail_count = len([r for r in results if r["status"] == "fail"])
        degraded = len([r for r in results if r["status"] == "degraded"])
        
        # Get rankings
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT provider_id, name, status, score, rank, success_count, fail_count, avg_latency_ms, alternative_in_use, experience_points FROM provider_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        summary = f"Verificação providers: {ok_count} OK, {degraded} degradados, {fail_count} falhados. "
        if fail_count > 0:
            failed = [r["provider_id"] for r in results if r["status"] == "fail"]
            summary += f"Falhas: {', '.join(failed)}. Failover ativado para alternativas. "
        
        # Top 3 ranking
        top3 = rankings[:3]
        summary += f"Top ranking: {', '.join([f'{r['provider_id']}({r['score']})' for r in top3])}"
        
        return TaskOutput(
            task_id=task_input.task_id,
            status="completed",
            summary=summary,
            artifacts=[
                {"type": "provider_health", "data": results},
                {"type": "provider_ranking", "data": rankings}
            ],
            evidence=[{"type": "health_check", "providers_checked": len(results), "ok": ok_count}],
            confidence="high" if ok_count >= len(results) * 0.7 else "medium",
            requires_review=False,
            next_recommendations=[
                f"Provider {r['provider_id']} com {r['consecutive_fails']} falhas consecutivas — considerar alternativa {r['alternative_in_use']}" 
                for r in rankings if r.get('consecutive_fails', 0) >= 2
            ] if 'consecutive_fails' in str(rankings) else []
        )

    def _get_ranking(self, task_input: TaskInput) -> TaskOutput:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM provider_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT * FROM provider_health_history ORDER BY check_time DESC LIMIT 20")
        history = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        # Calcula preferência
        by_category = {}
        for r in rankings:
            cat = r["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)
        
        summary = "Ranking providers por experiência:\n"
        for cat, providers in by_category.items():
            summary += f"\n{cat.upper()}: "
            for p in sorted(providers, key=lambda x: x["score"], reverse=True)[:2]:
                summary += f"{p['provider_id']} (score {p['score']}, exp {p['experience_points']}) > "
        
        return TaskOutput(
            task_id=task_input.task_id,
            status="completed",
            summary=summary,
            artifacts=[
                {"type": "ranking", "data": rankings},
                {"type": "history", "data": history},
                {"type": "by_category", "data": by_category}
            ],
            confidence="high",
            requires_review=False
        )
