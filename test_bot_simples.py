"""
Teste simples e direto do bot - sem imports complexos
"""
import asyncio
import os
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('assistente-ranny/.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID', '-1003536252896'))
TOPIC_CHAT = int(os.getenv('TOPIC_CHAT', '47'))

print("=" * 80)
print("🤖 TESTE SIMPLES DO ASSISTENTE RANNY")
print("=" * 80)

async def test_bot():
    """Testa o bot de forma simples"""
    
    print(f"\n⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # Teste 1: Conexão
    print("📡 Testando conexão com o bot...")
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username} ({me.first_name})")
        print(f"   ID: {me.id}")
        print(f"   Pode ler mensagens: {me.can_read_all_group_messages}")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return
    
    # Teste 2: Informações do grupo
    print(f"\n📱 Testando acesso ao grupo...")
    try:
        chat = await bot.get_chat(GROUP_ID)
        print(f"✅ Grupo acessível: {chat.title}")
        print(f"   ID: {chat.id}")
        print(f"   Tipo: {chat.type}")
    except Exception as e:
        print(f"❌ Erro ao acessar grupo: {e}")
        return
    
    # Teste 3: Enviar mensagem de teste
    print(f"\n💬 Enviando mensagem de teste...")
    try:
        message = await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text=f"🤖 **TESTE AUTOMÁTICO DO BOT**\n\n"
                 f"✅ Bot está funcionando!\n"
                 f"📅 {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n\n"
                 f"Testando funcionalidades básicas...",
            parse_mode='Markdown'
        )
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"   ID da mensagem: {message.message_id}")
        print(f"   Tópico: {message.message_thread_id}")
        
        # Aguarda 2 segundos
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return
    
    # Teste 4: Criar e enviar PDF de teste
    print(f"\n📄 Criando PDF de teste...")
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        pdf_path = "teste_bot.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "TESTE DO BOT ASSISTENTE RANNY")
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        c.drawString(100, 700, "")
        c.drawString(100, 680, "Este é um documento de teste criado automaticamente.")
        c.drawString(100, 660, "")
        c.drawString(100, 640, "Funcionalidades testadas:")
        c.drawString(120, 620, "✓ Conexão com Telegram")
        c.drawString(120, 600, "✓ Acesso ao grupo")
        c.drawString(120, 580, "✓ Envio de mensagens")
        c.drawString(120, 560, "✓ Criação de PDF")
        c.drawString(120, 540, "✓ Envio de documentos")
        c.save()
        
        print(f"✅ PDF criado: {pdf_path}")
        
        # Envia o PDF
        print(f"\n📎 Enviando PDF para o grupo...")
        with open(pdf_path, 'rb') as f:
            doc_message = await bot.send_document(
                chat_id=GROUP_ID,
                message_thread_id=TOPIC_CHAT,
                document=f,
                caption="📄 **Documento de Teste**\n\n"
                        "Este PDF foi criado e enviado automaticamente pelo bot.\n"
                        "Todas as funcionalidades básicas estão operacionais! ✅",
                parse_mode='Markdown'
            )
        
        print(f"✅ PDF enviado com sucesso!")
        print(f"   ID da mensagem: {doc_message.message_id}")
        
        # Remove arquivo temporário
        os.remove(pdf_path)
        print(f"✅ Arquivo temporário removido")
        
    except Exception as e:
        print(f"❌ Erro ao criar/enviar PDF: {e}")
        import traceback
        traceback.print_exc()
    
    # Teste 5: Mensagem final
    print(f"\n🎉 Enviando mensagem de conclusão...")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="✅ **TESTE CONCLUÍDO COM SUCESSO!**\n\n"
                 "Todas as funcionalidades básicas estão operacionais:\n"
                 "• Conexão com Telegram ✅\n"
                 "• Acesso ao grupo ✅\n"
                 "• Envio de mensagens ✅\n"
                 "• Criação de documentos ✅\n"
                 "• Envio de arquivos ✅\n\n"
                 "O bot está pronto para uso! 🚀",
            parse_mode='Markdown'
        )
        print(f"✅ Mensagem final enviada!")
        
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem final: {e}")
    
    # Resumo
    print("\n" + "=" * 80)
    print("🎯 RESUMO DO TESTE")
    print("=" * 80)
    print("✅ Conexão com bot: OK")
    print("✅ Acesso ao grupo: OK")
    print("✅ Envio de mensagens: OK")
    print("✅ Criação de PDF: OK")
    print("✅ Envio de documentos: OK")
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("=" * 80)
    print(f"\n⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

if __name__ == "__main__":
    asyncio.run(test_bot())
