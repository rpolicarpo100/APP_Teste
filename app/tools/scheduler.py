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
