"""
Scheduler tool — APScheduler wrapper
Local AI Brain §17
"""
from app.tools.registry import register_tool
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import uuid

# Singleton scheduler para MVP
_scheduler = None

def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
    return _scheduler

@register_tool(
    id="scheduler.create",
    name="Scheduler Create",
    description="Cria tarefa agendada com cron expression",
    risk_level="MEDIUM",
    requires_approval=False,
    input_schema={"type": "object", "properties": {"name": {"type": "string"}, "cron": {"type": "string"}, "agent": {"type": "string"}, "payload": {"type": "object"}}, "required": ["name", "cron"]},
    output_schema={"type": "object", "properties": {"id": {"type": "string"}}}
)
def scheduler_create(name: str, cron: str, agent: str = "automation", payload: dict = None) -> dict:
    try:
        scheduler = get_scheduler()
        job_id = str(uuid.uuid4())
        # Para MVP, apenas regista — execução real seria via callback
        # Cron parsing validation
        CronTrigger.from_crontab(cron)
        scheduler.add_job(
            lambda: print(f"[Scheduler] Executing {name} agent={agent} payload={payload} at {datetime.utcnow()}"),
            CronTrigger.from_crontab(cron),
            id=job_id,
            name=name,
            replace_existing=True
        )
        return {"id": job_id, "name": name, "cron": cron, "agent": agent, "payload": payload or {}, "created": True}
    except Exception as e:
        return {"error": str(e), "created": False}

@register_tool(
    id="scheduler.list",
    name="Scheduler List",
    description="Lista tarefas agendadas",
    risk_level="LOW",
    requires_approval=False,
    input_schema={"type": "object", "properties": {}},
    output_schema={"type": "object", "properties": {"jobs": {"type": "array"}}}
)
def scheduler_list() -> dict:
    try:
        scheduler = get_scheduler()
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({"id": job.id, "name": job.name, "next_run": str(job.next_run_time)})
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        return {"error": str(e), "jobs": []}

def provider_health_check_job():
    """Job que verifica saúde dos providers e atualiza ranking"""
    try:
        from app.agents.provider_health import ProviderHealthAgent
        from app.agents.base import TaskInput
        import uuid
        print(f"[ProviderHealthScheduler] Verificando providers em {datetime.utcnow().isoformat()}")
        agent = ProviderHealthAgent()
        task = TaskInput(
            task_id=str(uuid.uuid4()),
            mission_id=str(uuid.uuid4()),
            agent_id="provider_health",
            objective="verificar saúde de todos os providers - job agendado"
        )
        output = agent.execute(task)
        print(f"[ProviderHealthScheduler] Resultado: {output.summary}")
    except Exception as e:
        print(f"[ProviderHealthScheduler] Erro: {e}")

def start_provider_health_scheduler():
    """Inicia scheduler que verifica providers a cada 5 minutos"""
    try:
        scheduler = get_scheduler()
        # Remove job existente se houver
        try:
            scheduler.remove_job("provider_health_check")
        except:
            pass
        
        # Adiciona job a cada 5 minutos
        scheduler.add_job(
            provider_health_check_job,
            'interval',
            minutes=5,
            id="provider_health_check",
            name="Provider Health Check - verifica providers a cada 5 min",
            replace_existing=True,
            next_run_time=None  # Não executa imediatamente, espera 5 min para evitar crash no Render
        )
        
        # Também adiciona job a cada hora para recalcular ranking
        try:
            scheduler.remove_job("provider_ranking_recalc")
        except:
            pass
        
        def recalc_ranking_job():
            try:
                import sqlite3
                from pathlib import Path
                DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "brain.db"
                conn = sqlite3.connect(str(DB_PATH))
                cur = conn.cursor()
                cur.execute("SELECT provider_id, score FROM provider_rankings ORDER BY score DESC, success_count DESC")
                ranked = cur.fetchall()
                for rank, (provider_id, _) in enumerate(ranked, 1):
                    cur.execute("UPDATE provider_rankings SET rank=? WHERE provider_id=?", (rank, provider_id))
                conn.commit()
                conn.close()
                print(f"[ProviderRankingScheduler] Ranking recalculado em {datetime.utcnow().isoformat()}")
            except Exception as e:
                print(f"[ProviderRankingScheduler] Erro: {e}")
        
        scheduler.add_job(
            recalc_ranking_job,
            'interval',
            hours=1,
            id="provider_ranking_recalc",
            name="Recalcula ranking providers a cada hora",
            replace_existing=True
        )
        
        print(f"[Scheduler] Provider Health jobs agendados: check a cada 5 min, ranking a cada 1h")
        return True
    except Exception as e:
        print(f"[Scheduler] Erro ao iniciar provider health scheduler: {e}")
        return False
