"""
Teste completo de todas as funcionalidades do bot
Envia mensagens e aguarda respostas
"""
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv('assistente-ranny/.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID'))
TOPIC_CHAT = int(os.getenv('TOPIC_CHAT'))

async def enviar_e_aguardar(bot, texto, aguardar=5):
    """Envia mensagem e aguarda resposta"""
    print(f"\n📤 Enviando: {texto}")
    await bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_CHAT,
        text=texto
    )
    print(f"⏳ Aguardando {aguardar} segundos...")
    await asyncio.sleep(aguardar)

async def testar_todas_funcionalidades():
    """Testa todas as funcionalidades do bot"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    print("=" * 80)
    print("🧪 TESTE COMPLETO DE FUNCIONALIDADES")
    print("=" * 80)
    
    # Teste 1: Fechamento de caixa
    print("\n\n1️⃣ TESTANDO: Fechamento de caixa")
    await enviar_e_aguardar(bot, "fechei 3500", 8)
    
    # Teste 2: Criar lembrete
    print("\n\n2️⃣ TESTANDO: Criar lembrete")
    await enviar_e_aguardar(bot, "me lembra amanhã às 15h de conferir estoque", 8)
    
    # Teste 3: Listar lembretes
    print("\n\n3️⃣ TESTANDO: Listar lembretes")
    await enviar_e_aguardar(bot, "quais meus lembretes?", 8)
    
    # Teste 4: Buscar documento
    print("\n\n4️⃣ TESTANDO: Buscar documento")
    await enviar_e_aguardar(bot, "cadê a nota fiscal?", 8)
    
    # Teste 5: Conversa livre
    print("\n\n5️⃣ TESTANDO: Conversa livre")
    await enviar_e_aguardar(bot, "Como faço para organizar melhor os documentos?", 8)
    
    # Teste 6: Criar documento
    print("\n\n6️⃣ TESTANDO: Criar documento")
    await enviar_e_aguardar(bot, "cria um pdf com: LISTA DE COMPRAS\n- Queijo mussarela\n- Presunto\n- Tomate\n- Azeitonas", 10)
    
    # Teste 7: Ajuda
    print("\n\n7️⃣ TESTANDO: Comando de ajuda")
    await enviar_e_aguardar(bot, "/help", 8)
    
    print("\n\n" + "=" * 80)
    print("✅ TODOS OS TESTES ENVIADOS!")
    print("=" * 80)
    print("\n📱 Agora verifique o Telegram para ver as respostas do bot.")
    print("   O bot deve ter respondido a cada mensagem.")

if __name__ == "__main__":
    asyncio.run(testar_todas_funcionalidades())
