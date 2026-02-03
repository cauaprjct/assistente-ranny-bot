"""
🕐 Scheduler - Agendador de tarefas do Assistente Ranny

Usa APScheduler com AsyncIOScheduler para:
- Disparar lembretes no horário correto
- Enviar alertas de vencimentos
- Gerar resumos semanais automáticos

Requirements: 3.3, 8.1
"""

import logging
from datetime import datetime
from typing import Optional, Callable, Awaitable

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Timezone Brasil (São Paulo)
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

logger = logging.getLogger(__name__)

# Instância global do scheduler
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Retorna a instância do scheduler, criando se necessário"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(
            timezone=BRAZIL_TZ,
            job_defaults={
                'coalesce': True,  # Agrupa execuções perdidas
                'max_instances': 1,  # Evita execuções paralelas do mesmo job
                'misfire_grace_time': 60 * 5,  # 5 minutos de tolerância
            }
        )
        logger.info("📅 Scheduler criado com timezone America/Sao_Paulo")
    return _scheduler


def start_scheduler() -> None:
    """Inicia o scheduler se não estiver rodando"""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("✅ Scheduler iniciado")
    else:
        logger.info("⚠️ Scheduler já estava rodando")


def stop_scheduler() -> None:
    """Para o scheduler graciosamente"""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("🛑 Scheduler encerrado")
    _scheduler = None


def add_cron_job(
    func: Callable[[], Awaitable[None]],
    job_id: str,
    hour: int,
    minute: int = 0,
    day_of_week: str = '*',
    replace_existing: bool = True
) -> None:
    """
    Adiciona um job com trigger cron (horário fixo)
    
    Args:
        func: Função async a ser executada
        job_id: ID único do job
        hour: Hora de execução (0-23)
        minute: Minuto de execução (0-59)
        day_of_week: Dias da semana ('mon-fri', 'sun', '*' para todos)
        replace_existing: Se True, substitui job existente com mesmo ID
    """
    scheduler = get_scheduler()
    
    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        day_of_week=day_of_week,
        timezone=BRAZIL_TZ
    )
    
    scheduler.add_job(
        func,
        trigger=trigger,
        id=job_id,
        replace_existing=replace_existing
    )
    
    logger.info(f"📅 Job '{job_id}' agendado para {hour:02d}:{minute:02d} ({day_of_week})")


def add_interval_job(
    func: Callable[[], Awaitable[None]],
    job_id: str,
    minutes: int = 0,
    hours: int = 0,
    replace_existing: bool = True
) -> None:
    """
    Adiciona um job com trigger de intervalo
    
    Args:
        func: Função async a ser executada
        job_id: ID único do job
        minutes: Intervalo em minutos
        hours: Intervalo em horas
        replace_existing: Se True, substitui job existente com mesmo ID
    """
    scheduler = get_scheduler()
    
    trigger = IntervalTrigger(
        minutes=minutes,
        hours=hours,
        timezone=BRAZIL_TZ
    )
    
    scheduler.add_job(
        func,
        trigger=trigger,
        id=job_id,
        replace_existing=replace_existing
    )
    
    interval_str = f"{hours}h{minutes}m" if hours else f"{minutes}m"
    logger.info(f"📅 Job '{job_id}' agendado a cada {interval_str}")


def add_one_time_job(
    func: Callable[[], Awaitable[None]],
    job_id: str,
    run_date: datetime,
    replace_existing: bool = True
) -> None:
    """
    Adiciona um job para executar uma única vez
    
    Args:
        func: Função async a ser executada
        job_id: ID único do job
        run_date: Data/hora de execução
        replace_existing: Se True, substitui job existente com mesmo ID
    """
    scheduler = get_scheduler()
    
    # Garante que a data está no timezone correto
    if run_date.tzinfo is None:
        run_date = BRAZIL_TZ.localize(run_date)
    
    trigger = DateTrigger(run_date=run_date, timezone=BRAZIL_TZ)
    
    scheduler.add_job(
        func,
        trigger=trigger,
        id=job_id,
        replace_existing=replace_existing
    )
    
    logger.info(f"📅 Job '{job_id}' agendado para {run_date.strftime('%d/%m/%Y %H:%M')}")


def remove_job(job_id: str) -> bool:
    """
    Remove um job pelo ID
    
    Returns:
        True se removeu, False se não existia
    """
    scheduler = get_scheduler()
    try:
        scheduler.remove_job(job_id)
        logger.info(f"🗑️ Job '{job_id}' removido")
        return True
    except Exception:
        return False


def get_jobs() -> list:
    """Retorna lista de jobs agendados"""
    scheduler = get_scheduler()
    return scheduler.get_jobs()


def get_next_run_time(job_id: str) -> Optional[datetime]:
    """Retorna próxima execução de um job"""
    scheduler = get_scheduler()
    job = scheduler.get_job(job_id)
    if job:
        return job.next_run_time
    return None


def now_brazil() -> datetime:
    """Retorna datetime atual no timezone do Brasil"""
    return datetime.now(BRAZIL_TZ)
