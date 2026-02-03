"""
🔔 Jobs - Tarefas agendadas do Assistente Ranny

Jobs automáticos:
- check_lembretes: Dispara lembretes no horário correto (a cada minuto)
- check_vencimentos: Alerta sobre vencimentos próximos (8h diário)
- resumo_semanal: Envia resumo financeiro (domingo 20h)
- keep_alive: Mantém o bot acordado no Railway (a cada 10 minutos)

Requirements: 3.3, 8.1
"""

import logging
from datetime import datetime
from typing import Optional, Callable, Awaitable
import httpx

import database_adapter as db
from config import GROUP_ID, TOPICS, BASE_URL

logger = logging.getLogger(__name__)

# Referência ao bot do Telegram (será configurada pelo bot.py)
_telegram_bot = None


def set_telegram_bot(bot) -> None:
    """Configura a referência ao bot do Telegram
    
    Deve ser chamado pelo bot.py após criar a Application
    """
    global _telegram_bot
    _telegram_bot = bot
    logger.info("📱 Bot do Telegram configurado para jobs")


def get_telegram_bot():
    """Retorna a referência ao bot do Telegram"""
    return _telegram_bot


async def check_lembretes() -> int:
    """Job de lembretes - verifica e dispara lembretes pendentes
    
    Busca lembretes do dia com hora <= agora, envia no Tópico_Chat
    e marca como disparado. Para lembretes recorrentes, cria o próximo.
    
    Requirements: 3.3
    
    Returns:
        Número de lembretes disparados
    """
    bot = get_telegram_bot()
    if not bot:
        logger.warning("⚠️ Bot não configurado, pulando check_lembretes")
        return 0
    
    # Busca lembretes que devem ser disparados
    lembretes = db.get_lembretes_para_disparar()
    
    if not lembretes:
        return 0
    
    disparados = 0
    
    for lembrete in lembretes:
        try:
            # Monta mensagem do lembrete
            descricao = lembrete['descricao']
            hora = lembrete.get('hora', '09:00')
            
            mensagem = f"🔔 Lembrete!\n\n{descricao}"
            
            if lembrete.get('recorrente'):
                recorrencia = {
                    'diario': 'diário',
                    'semanal': 'semanal',
                    'mensal': 'mensal'
                }.get(lembrete['recorrente'], lembrete['recorrente'])
                mensagem += f"\n\n🔄 Lembrete {recorrencia}"
            
            # Envia no Tópico_Chat
            await bot.send_message(
                chat_id=GROUP_ID,
                text=mensagem,
                message_thread_id=TOPICS['chat']
            )
            
            # Marca como disparado
            db.marcar_lembrete_disparado(lembrete['id'])
            
            # Se for recorrente, cria o próximo
            if lembrete.get('recorrente'):
                novo = db.criar_proximo_lembrete_recorrente(lembrete)
                if novo:
                    logger.info(f"🔄 Próximo lembrete recorrente criado: {novo['data']}")
            
            disparados += 1
            logger.info(f"✅ Lembrete disparado: {descricao[:30]}...")
            
        except Exception as e:
            logger.error(f"❌ Erro ao disparar lembrete {lembrete['id']}: {e}")
    
    if disparados > 0:
        logger.info(f"🔔 {disparados} lembrete(s) disparado(s)")
    
    return disparados


async def check_vencimentos() -> int:
    """Job de vencimentos - alerta sobre contas a vencer
    
    Busca vencimentos não pagos e alerta quando dias_restantes em [7, 3, 1].
    
    Requirements: 8.1, 8.2, 8.3
    
    Returns:
        Número de alertas enviados
    """
    bot = get_telegram_bot()
    if not bot:
        logger.warning("⚠️ Bot não configurado, pulando check_vencimentos")
        return 0
    
    # Busca vencimentos dos próximos 7 dias
    vencimentos = db.get_vencimentos_proximos(7)
    
    if not vencimentos:
        return 0
    
    alertas = 0
    
    # Filtra apenas os que devem gerar alerta (7, 3, 1 dias)
    dias_alerta = [7, 3, 1]
    
    for venc in vencimentos:
        dias = venc.get('dias_restantes', 999)
        
        if dias not in dias_alerta:
            continue
        
        try:
            # Monta mensagem de alerta
            descricao = venc['descricao']
            valor = venc.get('valor', 0)
            
            if dias == 1:
                urgencia = "⚠️ AMANHÃ!"
            elif dias == 3:
                urgencia = "📅 Em 3 dias"
            else:
                urgencia = "📆 Em 7 dias"
            
            mensagem = f"🔔 Vencimento próximo!\n\n"
            mensagem += f"{urgencia}\n"
            mensagem += f"📌 {descricao}\n"
            
            if valor:
                mensagem += f"💰 R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Envia no Tópico_Chat
            await bot.send_message(
                chat_id=GROUP_ID,
                text=mensagem,
                message_thread_id=TOPICS['chat']
            )
            
            alertas += 1
            logger.info(f"✅ Alerta de vencimento enviado: {descricao[:30]}...")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar alerta de vencimento: {e}")
    
    if alertas > 0:
        logger.info(f"🔔 {alertas} alerta(s) de vencimento enviado(s)")
    
    return alertas


async def resumo_semanal() -> bool:
    """Job de resumo semanal - envia relatório financeiro com gráficos
    
    Gera relatório interativo dos fechamentos da semana e envia no Tópico_Chat.
    Executado todo domingo às 20h.
    
    - Busca fechamentos dos últimos 7 dias
    - Busca vencimentos para gráfico de gastos
    - Gera token temporário (TTL 24h)
    - Envia link para página de relatório
    
    Requirements: 5.4
    Property 12: Token tem TTL de 24h
    
    Returns:
        True se enviou com sucesso
    """
    bot = get_telegram_bot()
    if not bot:
        logger.warning("⚠️ Bot não configurado, pulando resumo_semanal")
        return False
    
    try:
        # Busca fechamentos da semana
        fechamentos = db.get_fechamentos(7)
        vencimentos = db.get_vencimentos_periodo(7)
        
        if not fechamentos and not vencimentos:
            mensagem = "📊 Resumo da Semana\n\n"
            mensagem += "Nenhum fechamento registrado esta semana.\n"
            mensagem += "Lembra de me contar o fechamento todo dia! 😊"
            
            await bot.send_message(
                chat_id=GROUP_ID,
                text=mensagem,
                message_thread_id=TOPICS['chat']
            )
            logger.info("✅ Resumo semanal enviado (sem dados)")
            return True
        
        # Calcula estatísticas
        total = sum(f['valor'] for f in fechamentos) if fechamentos else 0
        media = total / len(fechamentos) if fechamentos else 0
        
        # Prepara dados para o relatório
        dados_relatorio = {
            'fechamentos': fechamentos,
            'vencimentos': vencimentos,
            'periodo': 'Última semana',
            'periodo_dias': 7
        }
        
        # Cria token temporário no banco (TTL 24h)
        token = db.criar_relatorio_temp('semanal', dados_relatorio)
        
        if not token:
            # Fallback: envia resumo em texto se não conseguir criar token
            mensagem = "📊 Resumo da Semana\n\n"
            mensagem += f"📈 Total: R$ {total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.')
            mensagem += f"📊 Média: R$ {media:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.')
            mensagem += f"📅 Dias registrados: {len(fechamentos)}\n"
            
            if fechamentos:
                melhor = max(fechamentos, key=lambda x: x['valor'])
                pior = min(fechamentos, key=lambda x: x['valor'])
                mensagem += f"\n🏆 Melhor dia: R$ {melhor['valor']:,.2f} ({melhor['data']})\n".replace(',', 'X').replace('.', ',').replace('X', '.')
                mensagem += f"📉 Menor dia: R$ {pior['valor']:,.2f} ({pior['data']})".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            await bot.send_message(
                chat_id=GROUP_ID,
                text=mensagem,
                message_thread_id=TOPICS['chat']
            )
            logger.info("✅ Resumo semanal enviado (texto, sem link)")
            return True
        
        # Monta URL do relatório
        # Usa BASE_URL do config (Railway ou localhost)
        relatorio_url = f"{BASE_URL}/relatorio/{token}"
        
        # Monta mensagem com link
        mensagem = "📊 Resumo da Semana\n\n"
        
        if fechamentos:
            mensagem += f"📈 Total: R$ {total:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.')
            mensagem += f"📊 Média diária: R$ {media:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.')
            mensagem += f"📅 {len(fechamentos)} dias registrados\n"
            
            # Melhor e pior dia
            melhor = max(fechamentos, key=lambda x: x['valor'])
            pior = min(fechamentos, key=lambda x: x['valor'])
            
            mensagem += f"\n🏆 Melhor: R$ {melhor['valor']:,.2f} ({melhor['data']})\n".replace(',', 'X').replace('.', ',').replace('X', '.')
            mensagem += f"📉 Menor: R$ {pior['valor']:,.2f} ({pior['data']})\n".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        mensagem += f"\n🔗 Veja os gráficos completos:\n{relatorio_url}\n"
        mensagem += f"\n⏰ O link expira em 24 horas!"
        
        # Envia no Tópico_Chat
        await bot.send_message(
            chat_id=GROUP_ID,
            text=mensagem,
            message_thread_id=TOPICS['chat']
        )
        
        logger.info("✅ Resumo semanal enviado com link de relatório")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar resumo semanal: {e}")
        return False


async def keep_alive() -> bool:
    """Job de keep-alive - mantém o bot acordado no Railway
    
    Faz uma requisição HTTP ao próprio health check a cada 10 minutos
    para evitar que o Railway coloque o serviço em sleep por inatividade.
    
    Isso é especialmente útil no plano gratuito do Railway que tem
    limite de horas de execução por mês.
    
    Returns:
        True se a requisição foi bem-sucedida
    """
    try:
        # Faz requisição ao health check
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                logger.debug("💓 Keep-alive: bot está acordado")
                return True
            else:
                logger.warning(f"⚠️ Keep-alive retornou status {response.status_code}")
                return False
                
    except httpx.TimeoutException:
        logger.warning("⏱️ Keep-alive: timeout na requisição")
        return False
    except Exception as e:
        logger.error(f"❌ Erro no keep-alive: {e}")
        return False


# Job sync_onedrive removido - usar monitor local em vez de integração Azure OneDrive
