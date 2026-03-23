"""
🔍 Descobrir ID do Tópico
Envia uma mensagem de teste e mostra o ID do tópico
"""

import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


async def descobrir_topicos():
    """Busca atualizações recentes e mostra IDs dos tópicos"""
    bot = Bot(token=BOT_TOKEN)
    
    print("=" * 60)
    print("🔍 DESCOBRINDO IDs DOS TÓPICOS")
    print("=" * 60)
    print()
    print("Buscando mensagens recentes...")
    print()
    
    # Buscar atualizações
    updates = await bot.get_updates(limit=100)
    
    topicos_encontrados = {}
    
    for update in updates:
        if update.message:
            msg = update.message
            
            # Verificar se é do grupo correto
            if str(msg.chat.id) == str(CHAT_ID):
                # Verificar se tem tópico
                if msg.message_thread_id:
                    topico_id = msg.message_thread_id
                    
                    # Tentar pegar o nome do tópico (se disponível)
                    if msg.reply_to_message and msg.reply_to_message.forum_topic_created:
                        nome = msg.reply_to_message.forum_topic_created.name
                    else:
                        nome = "Desconhecido"
                    
                    topicos_encontrados[topico_id] = {
                        'nome': nome,
                        'ultima_msg': msg.text[:50] if msg.text else '[arquivo]'
                    }
    
    if topicos_encontrados:
        print("✅ Tópicos encontrados:")
        print()
        for topico_id, info in topicos_encontrados.items():
            print(f"   ID: {topico_id}")
            print(f"   Nome: {info['nome']}")
            print(f"   Última msg: {info['ultima_msg']}")
            print()
    else:
        print("⚠️ Nenhum tópico encontrado nas últimas mensagens.")
        print()
        print("💡 Dica:")
        print("   1. Envie uma mensagem no tópico novo")
        print("   2. Execute este script novamente")
    
    print("=" * 60)
    print()
    print("📋 MÉTODO ALTERNATIVO:")
    print()
    print("1. Envie uma mensagem no tópico novo")
    print("2. Acesse: https://api.telegram.org/bot" + BOT_TOKEN + "/getUpdates")
    print("3. Procure por 'message_thread_id' na resposta")
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(descobrir_topicos())
    input("\nPressione Enter para fechar...")
