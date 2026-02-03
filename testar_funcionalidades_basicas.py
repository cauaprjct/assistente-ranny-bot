"""
Teste das funcionalidades básicas do bot
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv('assistente-ranny/.env')

async def testar_funcionalidades():
    """Testa funcionalidades básicas do bot"""
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    group_id = int(os.getenv('GROUP_ID', '-1003536252896'))
    topic_chat = 47
    
    bot = Bot(token=token)
    
    print("🧪 TESTE DE FUNCIONALIDADES BÁSICAS\n")
    print("=" * 60)
    
    testes = [
        {
            'nome': 'Fechamento de Caixa',
            'mensagem': 'fechei 2500',
            'esperado': 'Registrar fechamento de R$ 2.500,00'
        },
        {
            'nome': 'Lembrete',
            'mensagem': 'me lembra amanhã às 14h de testar o sistema',
            'esperado': 'Criar lembrete para amanhã às 14:00'
        },
        {
            'nome': 'Busca de Documentos',
            'mensagem': 'cadê os contratos?',
            'esperado': 'Listar tópicos ou buscar documentos'
        },
        {
            'nome': 'Conversa com IA',
            'mensagem': 'como você está hoje?',
            'esperado': 'Resposta natural da IA'
        }
    ]
    
    for i, teste in enumerate(testes, 1):
        print(f"\n📋 TESTE {i}/{len(testes)}: {teste['nome']}")
        print(f"   Mensagem: '{teste['mensagem']}'")
        print(f"   Esperado: {teste['esperado']}")
        
        try:
            await bot.send_message(
                chat_id=group_id,
                text=teste['mensagem'],
                message_thread_id=topic_chat
            )
            print(f"   ✅ Mensagem enviada!")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Aguarda 2 segundos entre testes
        if i < len(testes):
            await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("\n✅ Todos os testes enviados!")
    print("\n📱 Verifique as respostas do bot no Telegram (Tópico Chat)")
    print("\n💡 O bot deve responder a cada mensagem em alguns segundos")

if __name__ == '__main__':
    asyncio.run(testar_funcionalidades())
