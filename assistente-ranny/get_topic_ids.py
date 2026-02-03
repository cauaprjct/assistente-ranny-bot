"""
Script para descobrir os IDs dos tópicos do grupo Telegram
Rode uma vez e copie os IDs para o .env
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

async def get_topics():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    group_id = os.getenv('GROUP_ID')
    
    if not token or not group_id:
        print("❌ Configure TELEGRAM_BOT_TOKEN e GROUP_ID no .env")
        return
    
    bot = Bot(token)
    
    print(f"\n📋 Buscando tópicos do grupo {group_id}...\n")
    print("=" * 50)
    
    try:
        # Pega informações do chat
        chat = await bot.get_chat(int(group_id))
        print(f"Grupo: {chat.title}")
        print(f"ID: {chat.id}")
        print(f"Tipo: {chat.type}")
        print("=" * 50)
        
        # Tenta listar tópicos (se for supergrupo com tópicos)
        if hasattr(chat, 'is_forum') and chat.is_forum:
            print("\n✅ Grupo tem tópicos habilitados!")
            print("\n⚠️  O Telegram não tem API para listar tópicos.")
            print("Você precisa enviar uma mensagem em cada tópico")
            print("e o bot vai mostrar o ID.\n")
            print("Alternativa: Olhe as mensagens do grupo e pegue")
            print("o message_thread_id de cada tópico.\n")
        else:
            print("\n⚠️  Este grupo não tem tópicos habilitados.")
            print("Ative em: Configurações do grupo > Tópicos")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    await bot.close()

if __name__ == '__main__':
    asyncio.run(get_topics())
