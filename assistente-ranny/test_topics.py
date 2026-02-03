"""
Testa se os IDs dos tópicos estão corretos
Manda uma mensagem em cada tópico do grupo

Este é um script de teste manual - execute diretamente com:
    python test_topics.py

Não é executado automaticamente pelo pytest.
"""
import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
import pytest

load_dotenv()

TOPICS = {
    'Chat': int(os.getenv('TOPIC_CHAT', '47')),
    'Financeiro': int(os.getenv('TOPIC_FINANCEIRO', '2')),
    'Empresa': int(os.getenv('TOPIC_EMPRESA', '3')),
    'Jurídico': int(os.getenv('TOPIC_JURIDICO', '5')),
    'Pessoal': int(os.getenv('TOPIC_PESSOAL', '4')),
    'Funcionários': int(os.getenv('TOPIC_FUNCIONARIOS', '6')),
    'Manutenção': int(os.getenv('TOPIC_MANUTENCAO', '7')),
    'Outros': int(os.getenv('TOPIC_OUTROS', '8')),
}

@pytest.mark.skip(reason="Teste manual - envia mensagens reais no Telegram")
@pytest.mark.asyncio
async def test_topics_telegram():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    group_id = int(os.getenv('GROUP_ID'))
    
    bot = Bot(token)
    
    print("\n🧪 Testando tópicos...\n")
    
    for nome, topic_id in TOPICS.items():
        try:
            await bot.send_message(
                chat_id=group_id,
                text=f"✅ Teste: {nome}",
                message_thread_id=topic_id
            )
            print(f"✅ {nome} (ID: {topic_id}) - OK")
        except Exception as e:
            print(f"❌ {nome} (ID: {topic_id}) - ERRO: {e}")
        
        await asyncio.sleep(0.5)  # Evita flood
    
    await bot.close()
    print("\n✅ Teste concluído! Verifique o grupo no Telegram.")

if __name__ == '__main__':
    asyncio.run(test_topics_telegram())
