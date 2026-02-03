"""
Teste rápido da nova funcionalidade de busca
"""
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv('assistente-ranny/.env')

async def testar():
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    
    # Pega o ID do usuário (Ranny)
    user_id = 7846363557  # ID do usuário Mn/Ranny
    
    # Envia mensagem de teste COMO SE FOSSE DO USUÁRIO
    # Nota: Não podemos enviar mensagens como outro usuário
    # Vamos apenas verificar se o bot está online
    
    me = await bot.get_me()
    print(f"✅ Bot online: @{me.username}")
    print(f"📝 Para testar, envie uma mensagem para o bot no Telegram")
    print(f"💬 Mensagem sugerida: 'quantos arquivos você tem?'")

if __name__ == '__main__':
    asyncio.run(testar())
