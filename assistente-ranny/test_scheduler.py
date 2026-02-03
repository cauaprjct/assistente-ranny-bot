"""
Testes do módulo scheduler
"""
import pytest
import asyncio
from datetime import datetime, timedelta

from scheduler import (
    get_scheduler, 
    start_scheduler, 
    stop_scheduler, 
    BRAZIL_TZ, 
    now_brazil,
    add_cron_job,
    add_interval_job,
    add_one_time_job,
    remove_job,
    get_jobs,
    get_next_run_time
)


def test_brazil_timezone():
    """Verifica que o timezone está configurado corretamente"""
    assert str(BRAZIL_TZ) == 'America/Sao_Paulo'


def test_now_brazil():
    """Verifica que now_brazil retorna datetime com timezone"""
    now = now_brazil()
    assert now.tzinfo is not None
    assert str(now.tzinfo) == 'America/Sao_Paulo'


def test_scheduler_creation():
    """Verifica que o scheduler é criado corretamente"""
    scheduler = get_scheduler()
    assert scheduler is not None
    assert scheduler.timezone == BRAZIL_TZ


@pytest.fixture
def event_loop_for_scheduler():
    """Cria um event loop para testes do scheduler"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


def test_scheduler_start_stop(event_loop_for_scheduler):
    """Verifica que o scheduler inicia e para corretamente"""
    start_scheduler()
    scheduler = get_scheduler()
    assert scheduler.running is True
    
    stop_scheduler()
    # Após stop, o scheduler é resetado para None


def test_add_cron_job(event_loop_for_scheduler):
    """Verifica que jobs cron são adicionados corretamente"""
    start_scheduler()
    
    async def dummy_job():
        pass
    
    add_cron_job(dummy_job, 'test_cron', hour=9, minute=0)
    
    jobs = get_jobs()
    job_ids = [j.id for j in jobs]
    assert 'test_cron' in job_ids
    
    # Limpa
    remove_job('test_cron')
    stop_scheduler()


def test_add_interval_job(event_loop_for_scheduler):
    """Verifica que jobs de intervalo são adicionados corretamente"""
    start_scheduler()
    
    async def dummy_job():
        pass
    
    add_interval_job(dummy_job, 'test_interval', minutes=30)
    
    jobs = get_jobs()
    job_ids = [j.id for j in jobs]
    assert 'test_interval' in job_ids
    
    # Limpa
    remove_job('test_interval')
    stop_scheduler()


def test_remove_job(event_loop_for_scheduler):
    """Verifica que jobs são removidos corretamente"""
    start_scheduler()
    
    async def dummy_job():
        pass
    
    add_cron_job(dummy_job, 'test_remove', hour=10, minute=0)
    
    # Verifica que foi adicionado
    jobs = get_jobs()
    assert any(j.id == 'test_remove' for j in jobs)
    
    # Remove
    result = remove_job('test_remove')
    assert result is True
    
    # Verifica que foi removido
    jobs = get_jobs()
    assert not any(j.id == 'test_remove' for j in jobs)
    
    # Tenta remover novamente (não existe)
    result = remove_job('test_remove')
    assert result is False
    
    stop_scheduler()


def test_get_next_run_time(event_loop_for_scheduler):
    """Verifica que próxima execução é retornada corretamente"""
    start_scheduler()
    
    async def dummy_job():
        pass
    
    add_cron_job(dummy_job, 'test_next_run', hour=9, minute=0)
    
    next_run = get_next_run_time('test_next_run')
    assert next_run is not None
    assert next_run.tzinfo is not None
    
    # Job inexistente
    next_run = get_next_run_time('inexistente')
    assert next_run is None
    
    # Limpa
    remove_job('test_next_run')
    stop_scheduler()
