"""
Script SIMPLES para indexar arquivos do Telegram
Itera por IDs de mensagens e indexa documentos encontrados
"""

import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
import config
import database_adapter as db

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Mapeamento de tópicos (do relatorio_upload_backup.json)
TOPICOS = {
    'FINANCEIRO': 2,
    'EMPRESA': 3,
    'PESSOAL': 4,
    'JURIDICO': 5,
    'FUNCIONARIOS': 6,
    'MANUTENCAO': 7,
    'OUTROS': 8,
    'OPERACIONAL': 214,
    'MIDIA': 215,
    'CONTROLES': 216
}


async def indexar_mensagem(bot, chat_id, msg_id, topic_id, categoria):
    """Tenta indexar uma mensagem específica"""
    try:
        # Tenta pegar a mensagem
        # Nota: forward_message não funciona bem, vamos usar copy_message
        # que retorna a mensagem copiada
        
        # Primeiro, vamos tentar usar a API diretamente
        # Infelizmente, python-telegram-bot não tem getMessage
        # Vamos usar uma abordagem diferente: copiar para o mesmo chat e deletar
        
        try:
            # Copia a mensagem para o mesmo chat (temporariamente)
            copied = await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=chat_id,
                message_id=msg_id
            )
            
            # Deleta a cópia imediatamente
            await bot.delete_message(chat_id=chat_id, message_id=copied.message_id)
            
            # Se chegou aqui, a mensagem existe
            # Agora precisamos pegar os dados dela
            # Vamos usar forward para o próprio chat
            message = await bot.forward_message(
                chat_id=chat_id,
                from_chat_id=chat_id,
                message_id=msg_id
            )
            
            # Deleta o forward
            await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            
        except TelegramError as e:
            error_msg = str(e).lower()
            if "message not found" in error_msg or "message to copy not found" in error_msg:
                return None  # Mensagem não existe
            elif "message can't be copied" in error_msg or "message can't be forwarded" in error_msg:
                return None  # Mensagem não pode ser copiada
            else:
                raise
        
        # Verifica se tem documento ou foto
        if not hasattr(message, 'document') and not hasattr(message, 'photo'):
            return None
        
        if not message.document and not message.photo:
            return None
        
        # Extrai informações
        if message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name or f'documento_{msg_id}'
            mime_type = message.document.mime_type or 'application/octet-stream'
        elif message.photo:
            file_id = message.photo[-1].file_id
            caption = message.caption or f'foto_{msg_id}'
            file_name = f'{caption}.jpg' if not caption.endswith('.jpg') else caption
            mime_type = 'image/jpeg'
        else:
            return None
        
        # Verifica se já existe no banco
        existing = db.buscar_documentos(file_name)
        if existing:
            return 'duplicado'
        
        # Adiciona ao banco
        db.add_documento(
            tipo=mime_type,
            descricao=file_name,
            file_id=file_id,
            categoria=categoria,
            message_id=msg_id,
            topic_id=topic_id,
            dados_extraidos={
                'file_name': file_name,
                'categoria_original': categoria,
                'message_id': msg_id
            }
        )
        
        return 'indexado'
        
    except TelegramError as e:
        error_msg = str(e).lower()
        if "message not found" in error_msg or "message to copy not found" in error_msg:
            return None
        elif "message can't be copied" in error_msg or "message can't be forwarded" in error_msg:
            return None
        else:
            logger.debug(f"Erro Telegram msg {msg_id}: {e}")
            return None
    except Exception as e:
        logger.debug(f"Erro msg {msg_id}: {e}")
        return None


async def indexar_topico(bot, chat_id, topic_id, categoria, max_range=2000):
    """Indexa um tópico completo"""
    logger.info(f"\n📂 Indexando {categoria} (tópico {topic_id})...")
    
    indexados = 0
    duplicados = 0
    nao_encontrados = 0
    
    # Itera por possíveis IDs de mensagem
    # Começamos logo após o ID do tópico
    start_id = topic_id + 1
    end_id = start_id + max_range
    
    sem_sucesso_consecutivos = 0
    max_sem_sucesso = 100  # Para após 100 mensagens não encontradas consecutivas
    
    for msg_id in range(start_id, end_id):
        resultado = await indexar_mensagem(bot, chat_id, msg_id, topic_id, categoria)
        
        if resultado == 'indexado':
            indexados += 1
            sem_sucesso_consecutivos = 0
            if indexados % 10 == 0:
                logger.info(f"   📊 {categoria}: {indexados} indexados...")
        elif resultado == 'duplicado':
            duplicados += 1
            sem_sucesso_consecutivos = 0
        else:
            nao_encontrados += 1
            sem_sucesso_consecutivos += 1
        
        # Para se não encontrar muitas mensagens consecutivas
        if sem_sucesso_consecutivos >= max_sem_sucesso:
            logger.info(f"   ⏹️  Parando após {max_sem_sucesso} mensagens não encontradas")
            break
        
        # Aguarda um pouco para não sobrecarregar a API
        await asyncio.sleep(0.3)
    
    logger.info(f"✅ {categoria}: {indexados} indexados, {duplicados} duplicados")
    return indexados, duplicados


async def main():
    """Função principal"""
    
    logger.info("=" * 70)
    logger.info("🔍 INDEXADOR SIMPLES DE ARQUIVOS DO TELEGRAM")
    logger.info("=" * 70)
    logger.info("⚠️  Este processo pode demorar 10-20 minutos")
    logger.info("=" * 70)
    
    # Inicializa bot
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    chat_id = config.GROUP_ID
    
    logger.info(f"\n🤖 Bot inicializado")
    logger.info(f"💬 Chat ID: {chat_id}")
    
    # Indexa cada tópico
    total_indexados = 0
    total_duplicados = 0
    
    for categoria, topic_id in TOPICOS.items():
        try:
            indexados, duplicados = await indexar_topico(
                bot, chat_id, topic_id, categoria
            )
            total_indexados += indexados
            total_duplicados += duplicados
            
            # Aguarda entre tópicos
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Erro ao indexar {categoria}: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ INDEXAÇÃO CONCLUÍDA!")
    logger.info("=" * 70)
    logger.info(f"📊 Total indexado: {total_indexados} arquivos")
    logger.info(f"⏭️  Total duplicados: {total_duplicados} arquivos")
    logger.info(f"📁 Total geral: {total_indexados + total_duplicados} arquivos")
    logger.info("=" * 70)
    logger.info("\n🎉 Agora o bot pode buscar os arquivos antigos!")


if __name__ == '__main__':
    asyncio.run(main())
