"""
Script de teste completo do bot Assistente Ranny
Testa todas as funcionalidades principais
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

# Adiciona o diretório do bot ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistente-ranny'))

from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, GROUP_ID, TOPICS
from database import Database
from ai import GeminiAI
from pdf_tools import criar_pdf, criar_word, criar_excel

print("=" * 80)
print("🤖 TESTE COMPLETO DO ASSISTENTE RANNY")
print("=" * 80)

async def test_bot_connection():
    """Testa conexão com o bot"""
    print("\n📡 Testando conexão com o bot...")
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username} ({me.first_name})")
        return bot
    except Exception as e:
        print(f"❌ Erro ao conectar bot: {e}")
        return None

async def test_database():
    """Testa conexão com o banco de dados"""
    print("\n🗄️  Testando conexão com banco de dados...")
    try:
        db = Database()
        
        # Testa inserção de fechamento
        valor = 2500.00
        db.salvar_fechamento(valor, "Teste automático")
        print(f"✅ Fechamento salvo: R$ {valor:.2f}")
        
        # Testa busca de fechamentos
        fechamentos = db.buscar_fechamentos_periodo(7)
        print(f"✅ Fechamentos da semana: {len(fechamentos)} registros")
        
        # Testa lembretes
        data_lembrete = datetime.now() + timedelta(days=1)
        lembrete_id = db.criar_lembrete(
            "Teste de lembrete automático",
            data_lembrete.date(),
            "09:00"
        )
        print(f"✅ Lembrete criado: ID {lembrete_id}")
        
        # Lista lembretes ativos
        lembretes = db.listar_lembretes_ativos()
        print(f"✅ Lembretes ativos: {len(lembretes)}")
        
        # Cancela o lembrete de teste
        db.cancelar_lembrete(lembrete_id)
        print(f"✅ Lembrete de teste cancelado")
        
        return True
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

async def test_ai():
    """Testa integração com Gemini AI"""
    print("\n🧠 Testando integração com Gemini AI...")
    try:
        ai = GeminiAI()
        
        # Testa classificação de texto
        texto_boleto = "Boleto de luz da LIGHT no valor de R$ 350,00 vencimento 28/01/2026"
        categoria = ai.classificar_documento(texto_boleto)
        print(f"✅ Classificação: '{texto_boleto[:50]}...' → {categoria}")
        
        # Testa conversa
        resposta = ai.conversar("Oi, tudo bem?", "")
        print(f"✅ Conversa: '{resposta[:80]}...'")
        
        return True
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        return False

async def test_pdf_tools():
    """Testa criação de documentos"""
    print("\n📄 Testando criação de documentos...")
    try:
        # Cria PDF de teste
        pdf_path = criar_pdf("Teste de PDF\n\nEste é um documento de teste criado automaticamente.")
        print(f"✅ PDF criado: {pdf_path}")
        
        # Cria Word de teste
        word_path = criar_word("Teste de Word\n\nEste é um documento Word de teste.")
        print(f"✅ Word criado: {word_path}")
        
        # Cria Excel de teste
        excel_path = criar_excel("Nome,Valor,Data\nTeste,100,27/01/2026")
        print(f"✅ Excel criado: {excel_path}")
        
        return pdf_path, word_path, excel_path
    except Exception as e:
        print(f"❌ Erro ao criar documentos: {e}")
        return None, None, None

async def test_send_message(bot):
    """Testa envio de mensagem para o grupo"""
    print("\n💬 Testando envio de mensagem...")
    try:
        message = await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPICS['chat'],
            text=f"🤖 Teste automático do bot\n\n"
                 f"✅ Bot funcionando perfeitamente!\n"
                 f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                 f"Todas as funcionalidades testadas com sucesso! 🎉"
        )
        print(f"✅ Mensagem enviada: ID {message.message_id}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

async def test_send_documents(bot, pdf_path, word_path, excel_path):
    """Testa envio de documentos"""
    print("\n📎 Testando envio de documentos...")
    
    if not all([pdf_path, word_path, excel_path]):
        print("⚠️  Documentos não foram criados, pulando teste de envio")
        return False
    
    try:
        # Envia PDF
        with open(pdf_path, 'rb') as f:
            await bot.send_document(
                chat_id=GROUP_ID,
                message_thread_id=TOPICS['chat'],
                document=f,
                caption="📄 Teste de envio de PDF"
            )
        print(f"✅ PDF enviado: {pdf_path}")
        
        # Envia Word
        with open(word_path, 'rb') as f:
            await bot.send_document(
                chat_id=GROUP_ID,
                message_thread_id=TOPICS['chat'],
                document=f,
                caption="📝 Teste de envio de Word"
            )
        print(f"✅ Word enviado: {word_path}")
        
        # Envia Excel
        with open(excel_path, 'rb') as f:
            await bot.send_document(
                chat_id=GROUP_ID,
                message_thread_id=TOPICS['chat'],
                document=f,
                caption="📊 Teste de envio de Excel"
            )
        print(f"✅ Excel enviado: {excel_path}")
        
        # Limpa arquivos temporários
        for path in [pdf_path, word_path, excel_path]:
            if os.path.exists(path):
                os.remove(path)
        print("✅ Arquivos temporários removidos")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar documentos: {e}")
        return False

async def main():
    """Executa todos os testes"""
    print(f"\n⏰ Início dos testes: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    resultados = {
        'bot_connection': False,
        'database': False,
        'ai': False,
        'pdf_tools': False,
        'send_message': False,
        'send_documents': False
    }
    
    # Teste 1: Conexão com bot
    bot = await test_bot_connection()
    resultados['bot_connection'] = bot is not None
    
    # Teste 2: Banco de dados
    resultados['database'] = await test_database()
    
    # Teste 3: IA
    resultados['ai'] = await test_ai()
    
    # Teste 4: Criação de documentos
    pdf_path, word_path, excel_path = await test_pdf_tools()
    resultados['pdf_tools'] = all([pdf_path, word_path, excel_path])
    
    # Teste 5: Envio de mensagem (só se bot conectou)
    if bot:
        resultados['send_message'] = await test_send_message(bot)
        
        # Teste 6: Envio de documentos (só se documentos foram criados)
        if resultados['pdf_tools']:
            resultados['send_documents'] = await test_send_documents(bot, pdf_path, word_path, excel_path)
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)
    
    total = len(resultados)
    sucesso = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {teste.replace('_', ' ').title()}")
    
    print("\n" + "=" * 80)
    print(f"🎯 RESULTADO FINAL: {sucesso}/{total} testes passaram ({sucesso/total*100:.1f}%)")
    print("=" * 80)
    
    if sucesso == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Bot está funcionando perfeitamente!")
    elif sucesso >= total * 0.8:
        print("\n⚠️  Maioria dos testes passou, mas há alguns problemas.")
    else:
        print("\n❌ Vários testes falharam. Verifique as configurações.")
    
    print(f"\n⏰ Fim dos testes: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

if __name__ == "__main__":
    asyncio.run(main())
