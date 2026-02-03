"""
🤖 Bot Telegram Simplificado - Apenas para teste
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

load_dotenv()

# Logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Silencia logs de rede
for noisy in ['httpx', 'httpcore', 'telegram', 'telegram.ext']:
    logging.getLogger(noisy).setLevel(logging.ERROR)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler de mensagens"""
    
    logger.info(f"📨 UPDATE RECEBIDO!")
    logger.info(f"   Chat ID: {update.effective_chat.id if update.effective_chat else 'N/A'}")
    logger.info(f"   Chat Type: {update.effective_chat.type if update.effective_chat else 'N/A'}")
    logger.info(f"   User: {update.effective_user.first_name if update.effective_user else 'N/A'}")
    
    if not update.message:
        logger.info("   ⚠️ Update sem mensagem")
        return
    
    text = update.message.text or update.message.caption or ""
    topic_id = update.message.message_thread_id or "sem tópico"
    
    logger.info(f"   Tópico: {topic_id}")
    logger.info(f"   Texto: {text[:100] if text else '(sem texto)'}")
    
    # Responde
    await update.message.reply_text(f"✅ Recebi sua mensagem!\n\nTexto: {text[:50]}...")

async def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN não configurado!")
        return
    
    logger.info("=" * 40)
    logger.info("🤖 BOT SIMPLIFICADO - TESTE")
    logger.info("=" * 40)
    
    app = Application.builder().token(token).job_queue(None).build()
    
    # Handler para TODAS as mensagens
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.Document.ALL,
        handle_message
    ))
    
    logger.info("🤖 Iniciando polling...")
    
    async with app:
        await app.start()
        await app.updater.start_polling(
            drop_pending_updates=True,
            poll_interval=1.0,
            timeout=20
        )
        
        logger.info("✅ Bot online! Manda uma mensagem no grupo pra testar...")
        logger.info("   Pressione Ctrl+C para parar")
        
        # Aguarda indefinidamente
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        
        await app.updater.stop()
        await app.stop()

if __name__ == '__main__':
    asyncio.run(main())
