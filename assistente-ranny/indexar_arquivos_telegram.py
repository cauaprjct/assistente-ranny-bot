"""
Script para indexar arquivos já enviados para o Telegram
Lê as mensagens dos tópicos e adiciona ao banco de dados
"""

import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

import database_adapter as db
import config

load_dotenv()

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def indexar_topico(bot: Bot, topic_id: int, categoria: str):
    """Indexa mensagens de um tópico específico"""
    
    logger.info(f"📂 Indexando tópico: {categoria} (ID: {topic_id})")
    
    try:
        # Busca mensagens do tópico
        # Nota: A API do Telegram não permite buscar por tópico diretamente
        # Vamos usar uma abordagem diferente: iterar pelas mensagens
        
        indexados = 0
        erros = 0
        
        # Tenta buscar as últimas 1000 mensagens
        # Começando de uma mensagem recente e indo para trás
        for offset in range(0, 1000, 100):
            try:
                # Aqui precisaríamos usar get_chat_history ou similar
                # Mas a API pública do Telegram não expõe isso facilmente
                # Vamos usar uma abordagem alternativa
                pass
                
            except Exception as e:
                logger.error(f"Erro ao buscar mensagens: {e}")
                erros += 1
                break
        
        logger.info(f"✅ Tópico {categoria}: {indexados} indexados, {erros} erros")
        return indexados, erros
        
    except Exception as e:
        logger.error(f"❌ Erro ao indexar tópico {categoria}: {e}")
        return 0, 1


async def indexar_mensagem_especifica(bot: Bot, message_id: int, topic_id: int, categoria: str):
    """Indexa uma mensagem específica se tiver documento"""
    
    try:
        # Busca a mensagem
        message = await bot.forward_message(
            chat_id=config.GROUP_ID,
            from_chat_id=config.GROUP_ID,
            message_id=message_id
        )
        
        # Verifica se tem documento
        if message.document:
            doc = message.document
            
            # Adiciona ao banco
            db.add_documento(
                tipo=doc.mime_type or 'application/octet-stream',
                descricao=doc.file_name or 'Documento',
                file_id=doc.file_id,
                categoria=categoria,
                message_id=message_id,
                topic_id=topic_id,
                dados_extraidos={'file_name': doc.file_name, 'file_size': doc.file_size}
            )
            
            logger.info(f"✅ Indexado: {doc.file_name}")
            return True
            
        elif message.photo:
            photo = message.photo[-1]
            caption = message.caption or 'Imagem'
            
            db.add_documento(
                tipo='image/jpeg',
                descricao=caption,
                file_id=photo.file_id,
                categoria=categoria,
                message_id=message_id,
                topic_id=topic_id,
                dados_extraidos={'caption': caption}
            )
            
            logger.info(f"✅ Indexado: {caption}")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao indexar mensagem {message_id}: {e}")
        return False


async def indexar_range_mensagens(bot: Bot, start_id: int, end_id: int, topic_id: int, categoria: str):
    """Indexa um range de IDs de mensagens"""
    
    logger.info(f"📂 Indexando mensagens {start_id} a {end_id} do tópico {categoria}")
    
    indexados = 0
    erros = 0
    
    for msg_id in range(start_id, end_id + 1):
        try:
            if await indexar_mensagem_especifica(bot, msg_id, topic_id, categoria):
                indexados += 1
            
            # Aguarda um pouco para não sobrecarregar a API
            await asyncio.sleep(0.1)
            
        except Exception as e:
            erros += 1
            if erros > 10:
                logger.warning(f"Muitos erros consecutivos, parando...")
                break
    
    logger.info(f"✅ Range {start_id}-{end_id}: {indexados} indexados, {erros} erros")
    return indexados, erros


async def main():
    """Função principal"""
    
    logger.info("=" * 60)
    logger.info("🔍 INDEXADOR DE ARQUIVOS DO TELEGRAM")
    logger.info("=" * 60)
    
    # Cria bot
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    
    logger.info(f"✅ Bot conectado")
    logger.info(f"📁 Grupo: {config.GROUP_ID}")
    
    # Mapeamento de tópicos
    topicos = {
        'financeiro': config.TOPICS.get('financeiro'),
        'empresa': config.TOPICS.get('empresa'),
        'juridico': config.TOPICS.get('juridico'),
        'pessoal': config.TOPICS.get('pessoal'),
        'funcionarios': config.TOPICS.get('funcionarios'),
        'manutencao': config.TOPICS.get('manutencao'),
        'outros': config.TOPICS.get('outros'),
        'operacional': config.TOPICS.get('operacional'),
        'midia': config.TOPICS.get('midia'),
        'controles': config.TOPICS.get('controles'),
    }
    
    logger.info(f"\n📋 Tópicos a indexar: {len(topicos)}")
    
    # ABORDAGEM MANUAL: Você precisa fornecer os ranges de IDs
    # Exemplo: mensagens do tópico Funcionários estão entre ID 1000 e 1100
    
    logger.info("\n" + "=" * 60)
    logger.info("⚠️  ATENÇÃO: Este script precisa dos IDs das mensagens!")
    logger.info("=" * 60)
    logger.info("\nPara indexar os arquivos, você precisa:")
    logger.info("1. Abrir o Telegram Web")
    logger.info("2. Ir em cada tópico")
    logger.info("3. Clicar com botão direito em uma mensagem")
    logger.info("4. Copiar o link da mensagem")
    logger.info("5. O ID está no final do link")
    logger.info("\nExemplo de link:")
    logger.info("https://t.me/c/3536252896/12345")
    logger.info("                            ^^^^^")
    logger.info("                            ID da mensagem")
    logger.info("\n" + "=" * 60)
    
    # Exemplo de uso (você precisa ajustar os IDs):
    # await indexar_range_mensagens(bot, 1000, 1100, topicos['funcionarios'], 'funcionarios')
    
    logger.info("\n✅ Script pronto para uso!")
    logger.info("📝 Edite o script e adicione os ranges de IDs para cada tópico")


if __name__ == '__main__':
    asyncio.run(main())
