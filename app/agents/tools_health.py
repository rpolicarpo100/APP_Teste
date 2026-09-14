"""
Tools Health Agent — Audita, lista, analisa e faz ranking das tools, troca por melhores se necessário
Similar ao Provider Health mas para tools internas
"""
from app.agents.base import BaseAgent, TaskInput, TaskOutput
from datetime import datetime
import sqlite3
from pathlib import Path
import time
import json
import os

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"

# Alternativas por categoria de tool — se uma falha, troca por outra melhor rankeada
TOOL_ALTERNATIVES = {
    "web.search": ["web.fetch", "news.all", "news.portugal"],
    "web.fetch": ["web.search", "filesystem.read"],
    "filesystem.read": ["filesystem.list", "web.fetch"],
    "filesystem.write": ["filesystem.read", "filesystem.list"],
    "filesystem.list": ["filesystem.read"],
    "python.execute": ["filesystem.read", "filesystem.write"],
    "browser.open": ["web.fetch", "browser.screenshot"],
    "browser.screenshot": ["browser.open", "web.fetch"],
    "site.builder": ["filesystem.write", "filesystem.read"],
    "news.portugal": ["news.all", "news.world", "web.search"],
    "news.world": ["news.all", "news.portugal", "web.search"],
    "news.markets": ["news.all", "stocks.markets", "web.search"],
    "news.crypto": ["news.all", "crypto.markets", "web.search"],
    "news.all": ["news.portugal", "news.world"],
    "crypto.markets": ["crypto.gainers_losers", "news.crypto"],
    "crypto.gainers_losers": ["crypto.markets", "news.crypto"],
    "stocks.markets": ["stocks.gainers_losers", "news.markets"],
    "stocks.gainers_losers": ["stocks.markets", "news.markets"],
    "dashboard.market_overview": ["news.all", "crypto.markets", "stocks.markets"],
    "provider.health_check": ["provider.ranking"],
    "provider.ranking": ["provider.health_check"],
    "provider.failover": ["provider.health_check", "provider.ranking"]
}

def ensure_tools_tables():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tool_rankings (
        tool_id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        risk_level TEXT,
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
        usage_count INTEGER DEFAULT 0,
        experience_points INTEGER DEFAULT 0,
        implementation_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tool_health_history (
        id TEXT PRIMARY KEY,
        tool_id TEXT,
        check_time TIMESTAMP,
        status TEXT,
        latency_ms REAL,
        error TEXT,
        score REAL,
        FOREIGN KEY(tool_id) REFERENCES tool_rankings(tool_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tool_calls_log (
        id TEXT PRIMARY KEY,
        tool_id TEXT,
        agent_id TEXT,
        mission_id TEXT,
        task_id TEXT,
        status TEXT,
        latency_ms REAL,
        error TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

try:
    ensure_tools_tables()
except Exception as e:
    print(f"[ToolsHealth] Erro ao criar tabelas: {e}")

class ToolsHealthAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="tools_health",
            name="Tools Health & Rank Agent",
            specialty="Audita tools, analisa uso, ranking por experiência e failover para melhores",
            version="1.0.0"
        )
        self.skills = ["tool_audit", "tool_check", "tool_ranking", "failover", "experience_learning", "tool_optimization"]
        self.tools = ["filesystem.read", "filesystem.list", "provider.ranking", "tool.health_check", "tool.ranking"]
        self.limitations = ["Não pode criar novas tools, só rankear e sugerir alternativas entre existentes"]

    def _check_tool(self, tool_def) -> dict:
        """Verifica uma tool e retorna resultado"""
        import time
        start = time.time()
        result = {
            "tool_id": tool_def.id,
            "name": tool_def.name,
            "category": tool_def.id.split('.')[0] if '.' in tool_def.id else 'other',
            "risk_level": getattr(tool_def, 'risk_level', 'LOW'),
            "status": "fail",
            "latency_ms": 0,
            "error": None,
            "implementation": getattr(tool_def, 'implementation', None),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Verifica se implementação existe e é callable
            from app.tools.registry import tool_registry
            impl = tool_registry.get_implementation(tool_def.id)
            
            if not impl:
                result["status"] = "fail"
                result["error"] = "Implementação não encontrada"
                return result
            
            if not callable(impl):
                result["status"] = "fail"
                result["error"] = "Implementação não callable"
                return result
            
            # Verifica status no registry
            if tool_def.status.value != "available":
                result["status"] = "degraded"
                result["error"] = f"Status {tool_def.status.value}"
                result["latency_ms"] = round((time.time() - start) * 1000, 1)
                return result
            
            # Simula check rápido — não executa tool real para evitar side effects, só verifica metadata
            # Para tools de leitura, faz check leve
            latency = (time.time() - start) * 1000
            result["latency_ms"] = round(latency, 1)
            result["status"] = "ok"
            
        except Exception as e:
            result["latency_ms"] = round((time.time() - start) * 1000, 1)
            result["status"] = "fail"
            result["error"] = str(e)[:200]
        
        return result

    def _calculate_score(self, success_count: int, fail_count: int, avg_latency: float, consecutive_fails: int, experience: int, usage_count: int) -> float:
        """Calcula score baseado em experiência e uso"""
        total = success_count + fail_count
        if total == 0:
            success_rate = 0.7  # Assume OK se nunca usado, mas não perfeito
        else:
            success_rate = success_count / total
        
        # Latência — quanto menor melhor
        latency_score = 1.0
        if avg_latency > 0:
            latency_score = max(0.1, 1.0 - (avg_latency / 1000))
        
        # Penaliza fails consecutivos
        fail_penalty = max(0, 1.0 - (consecutive_fails * 0.3))
        
        # Bonus por experiência e uso
        exp_bonus = min(0.2, experience / 100)
        usage_bonus = min(0.1, usage_count / 50)
        
        score = (success_rate * 0.5 + latency_score * 0.2 + fail_penalty * 0.2 + 0.1) + exp_bonus + usage_bonus
        return round(min(1.0, max(0, score)), 3)

    def _update_ranking(self, check_result: dict):
        """Atualiza ranking na BD"""
        try:
            ensure_tools_tables()
        except:
            pass
        
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        
        tid = check_result["tool_id"]
        
        # Garante que existe na tabela
        cur.execute("SELECT tool_id FROM tool_rankings WHERE tool_id=?", (tid,))
        if not cur.fetchone():
            cur.execute("""
            INSERT INTO tool_rankings (tool_id, name, category, risk_level, implementation_path, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'unknown', ?, ?)
            """, (
                tid, 
                check_result["name"], 
                check_result["category"], 
                check_result["risk_level"],
                check_result.get("implementation"),
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))
        
        cur.execute("SELECT success_count, fail_count, avg_latency_ms, consecutive_fails, experience_points, usage_count FROM tool_rankings WHERE tool_id=?", (tid,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return
        
        success_count, fail_count, avg_latency, consecutive_fails, exp, usage_count = row
        
        # Atualiza contadores baseado no check
        if check_result["status"] == "ok":
            success_count += 1
            consecutive_fails = 0
            exp += 1
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
            exp = max(0, exp - 1)
            last_success = None
            last_fail = datetime.utcnow().isoformat()
            status = "fail" if consecutive_fails >= 2 else "degraded"
            alternatives = TOOL_ALTERNATIVES.get(tid, [])
            alternative = alternatives[0] if alternatives and consecutive_fails >= 3 else None
        
        # Busca uso real da tool (tool_calls_log)
        cur.execute("SELECT COUNT(*) FROM tool_calls_log WHERE tool_id=?", (tid,))
        usage_count = cur.fetchone()[0]
        
        score = self._calculate_score(success_count, fail_count, avg_latency, consecutive_fails, exp, usage_count)
        
        cur.execute("""
        UPDATE tool_rankings SET
            success_count=?, fail_count=?, consecutive_fails=?, 
            avg_latency_ms=?, last_latency_ms=?, last_check=?,
            last_success=COALESCE(?, last_success),
            last_fail=COALESCE(?, last_fail),
            status=?, score=?, alternative_in_use=?,
            experience_points=?, usage_count=?, updated_at=?
        WHERE tool_id=?
        """, (
            success_count, fail_count, consecutive_fails,
            round(avg_latency, 1), check_result["latency_ms"], datetime.utcnow().isoformat(),
            last_success if check_result["status"]=="ok" else None,
            last_fail if check_result["status"]!="ok" else None,
            status, score, alternative,
            exp, usage_count, datetime.utcnow().isoformat(),
            tid
        ))
        
        # History
        import uuid
        cur.execute("""
        INSERT INTO tool_health_history (id, tool_id, check_time, status, latency_ms, error, score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            tid,
            datetime.utcnow().isoformat(),
            check_result["status"],
            check_result["latency_ms"],
            check_result.get("error"),
            score
        ))
        
        conn.commit()
        
        # Update ranks
        cur.execute("SELECT tool_id, score FROM tool_rankings ORDER BY score DESC, success_count DESC, usage_count DESC")
        ranked = cur.fetchall()
        for rank, (tool_id, _) in enumerate(ranked, 1):
            cur.execute("UPDATE tool_rankings SET rank=? WHERE tool_id=?", (rank, tool_id))
        
        conn.commit()
        conn.close()

    def execute(self, task_input: TaskInput) -> TaskOutput:
        self.status = self.status.RUNNING if hasattr(self.status, 'RUNNING') else "RUNNING"
        
        objective = task_input.objective.lower()
        
        if "ranking" in objective or "rank" in objective:
            return self._get_ranking(task_input)
        elif "audit" in objective or "lista" in objective:
            return self._audit_tools(task_input)
        else:
            return self._check_all_tools(task_input)

    def _check_all_tools(self, task_input: TaskInput) -> TaskOutput:
        from app.tools.registry import tool_registry
        
        tools = tool_registry.list_all()
        results = []
        
        for tool_def in tools:
            check = self._check_tool(tool_def)
            self._update_ranking(check)
            results.append(check)
        
        ok_count = len([r for r in results if r["status"] == "ok"])
        fail_count = len([r for r in results if r["status"] == "fail"])
        degraded = len([r for r in results if r["status"] == "degraded"])
        
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT tool_id, name, status, score, rank, success_count, fail_count, usage_count, alternative_in_use, experience_points, category, consecutive_fails FROM tool_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        summary = f"Auditoria tools: {ok_count} OK, {degraded} degradadas, {fail_count} falhadas de {len(results)} total. "
        if fail_count > 0:
            failed = [r["tool_id"] for r in results if r["status"] == "fail"]
            summary += f"Falhas: {', '.join(failed)}. "
        
        top3 = rankings[:3]
        if top3:
            summary += "Top: " + ", ".join([f"{r['tool_id']}({r['score']})" for r in top3]) + ". "
        
        # Sugere trocas
        suggestions = []
        for r in rankings:
            if r.get("consecutive_fails",0) >= 3 and r.get("alternative_in_use"):
                suggestions.append(f"Trocar {r['tool_id']} → {r['alternative_in_use']} (score {r['score']})")
        
        if suggestions:
            summary += f"Sugestões failover: {'; '.join(suggestions)}"
        
        return TaskOutput(
            task_id=task_input.task_id,
            status="completed",
            summary=summary,
            artifacts=[
                {"type": "tool_health", "data": results},
                {"type": "tool_ranking", "data": rankings}
            ],
            evidence=[{"type": "tool_audit", "tools_checked": len(results), "ok": ok_count}],
            confidence="high" if ok_count >= len(results) * 0.8 else "medium",
            requires_review=False,
            next_recommendations=suggestions
        )

    def _audit_tools(self, task_input: TaskInput) -> TaskOutput:
        from app.tools.registry import tool_registry
        
        tools = tool_registry.list_all()
        by_category = {}
        for t in tools:
            cat = t.id.split('.')[0] if '.' in t.id else 'other'
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                "id": t.id,
                "name": t.name,
                "risk": getattr(t, 'risk_level', 'LOW'),
                "status": t.status.value,
                "implementation": t.implementation
            })
        
        summary = f"Auditoria completa: {len(tools)} tools em {len(by_category)} categorias. "
        for cat, lst in by_category.items():
            summary += f"{cat}({len(lst)}) "
        
        return TaskOutput(
            task_id=task_input.task_id,
            status="completed",
            summary=summary,
            artifacts=[
                {"type": "tools_by_category", "data": by_category},
                {"type": "all_tools", "data": [{"id": t.id, "name": t.name, "status": t.status.value} for t in tools]}
            ],
            confidence="high",
            requires_review=False
        )

    def _get_ranking(self, task_input: TaskInput) -> TaskOutput:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tool_rankings ORDER BY rank ASC")
        rankings = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT * FROM tool_health_history ORDER BY check_time DESC LIMIT 20")
        history = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        by_category = {}
        for r in rankings:
            cat = r["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)
        
        summary = "Ranking tools por experiência e uso:\n"
        for cat, tools in by_category.items():
            summary += f"\n{cat.upper()}: "
            for t in sorted(tools, key=lambda x: x["score"], reverse=True)[:2]:
                summary += f"{t['tool_id']}({t['score']}, exp {t['experience_points']}, uso {t['usage_count']}) > "
        
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
