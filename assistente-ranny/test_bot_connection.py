"""
Teste de conexão do bot - verifica se consegue receber updates
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application

load_dotenv()

async def test_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN não configurado!")
        return
    
    print(f"🔑 Token: {token[:20]}...{token[-10:]}")
    
    try:
        bot = Bot(token)
        
        # Testa conexão básica
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username} ({me.first_name})")
        print(f"   ID: {me.id}")
        print(f"   Can join groups: {me.can_join_groups}")
        print(f"   Can read all group messages: {me.can_read_all_group_messages}")
        
        # Verifica updates pendentes
        updates = await bot.get_updates(limit=5, timeout=5)
        print(f"\n📨 Updates pendentes: {len(updates)}")
        
        for update in updates:
            print(f"   - Update {update.update_id}: {type(update.message).__name__ if update.message else 'N/A'}")
            if update.message:
                chat = update.message.chat
                print(f"     Chat: {chat.title or chat.first_name} (ID: {chat.id}, Type: {chat.type})")
                if update.message.text:
                    print(f"     Texto: {update.message.text[:50]}...")
        
        # Testa envio de mensagem para o grupo
        group_id = int(os.getenv('GROUP_ID', '-1003536252896'))
        topic_chat = int(os.getenv('TOPIC_CHAT', '47'))
        
        print(f"\n📤 Testando envio para grupo {group_id}, tópico {topic_chat}...")
        
        try:
            msg = await bot.send_message(
                chat_id=group_id,
                text="🧪 Teste de conexão do bot - se você vê isso, o bot está funcionando!",
                message_thread_id=topic_chat
            )
            print(f"✅ Mensagem enviada com sucesso! ID: {msg.message_id}")
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    asyncio.run(test_bot())
