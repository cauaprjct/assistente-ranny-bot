"""
Teste simples: Verifica se o bot lista os 11 tópicos corretamente
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv('assistente-ranny/.env')

async def testar_bot():
    """Envia mensagem de teste para o bot"""
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    group_id = int(os.getenv('GROUP_ID', '-1003536252896'))
    topic_chat = 47
    
    bot = Bot(token=token)
    
    print("🧪 TESTE: Verificando resposta do bot sobre tópicos\n")
    
    # Envia mensagem de teste
    mensagem_teste = "quantos arquivos você tem?"
    
    print(f"📤 Enviando: '{mensagem_teste}'")
    
    await bot.send_message(
        chat_id=group_id,
        text=mensagem_teste,
        message_thread_id=topic_chat
    )
    
    print("✅ Mensagem enviada!")
    print("\n⏳ Aguarde alguns segundos e verifique a resposta do bot no Telegram...")
    print("\n📋 O bot deve listar os 11 tópicos:")
    print("   1. Chat")
    print("   2. Financeiro")
    print("   3. Empresa")
    print("   4. Jurídico")
    print("   5. Pessoal")
    print("   6. Funcionários")
    print("   7. Manutenção")
    print("   8. Outros")
    print("   9. Operacional")
    print("   10. Mídia")
    print("   11. Controles")
    print("\n✅ Total: ~300 arquivos em 11 tópicos")

if __name__ == '__main__':
    asyncio.run(testar_bot())
