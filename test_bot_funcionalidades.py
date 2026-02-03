"""
Teste das funcionalidades avançadas do bot
Simula interações reais com o bot
"""
import asyncio
import os
from datetime import datetime, timedelta
from telegram import Bot
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

# Carrega variáveis de ambiente
load_dotenv('assistente-ranny/.env')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID', '-1003536252896'))
TOPIC_CHAT = int(os.getenv('TOPIC_CHAT', '47'))

print("=" * 80)
print("🧪 TESTE DE FUNCIONALIDADES AVANÇADAS")
print("=" * 80)

def criar_boleto_teste():
    """Cria um PDF simulando um boleto"""
    pdf_path = "boleto_teste.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "BOLETO DE TESTE - LIGHT")
    
    # Informações do boleto
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Beneficiário: LIGHT SERVIÇOS DE ELETRICIDADE S.A.")
    c.drawString(100, 700, "Valor: R$ 350,00")
    c.drawString(100, 680, f"Vencimento: {(datetime.now() + timedelta(days=5)).strftime('%d/%m/%Y')}")
    c.drawString(100, 660, "")
    c.drawString(100, 640, "Código de barras:")
    c.setFont("Courier", 10)
    c.drawString(100, 620, "23793381286000000000300000000400192340000035000")
    
    c.save()
    return pdf_path

def criar_comprovante_teste():
    """Cria um PDF simulando um comprovante de pagamento"""
    pdf_path = "comprovante_teste.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "COMPROVANTE DE PAGAMENTO")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawString(100, 700, "Tipo: PIX")
    c.drawString(100, 680, "Valor: R$ 1.500,00")
    c.drawString(100, 660, "Destinatário: Fornecedor XYZ LTDA")
    c.drawString(100, 640, "Status: APROVADO")
    
    c.save()
    return pdf_path

def criar_contrato_teste():
    """Cria um PDF simulando um contrato"""
    pdf_path = "contrato_teste.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS")
    
    c.setFont("Helvetica", 11)
    y = 720
    linhas = [
        "",
        "CONTRATANTE: GRN PIZZAS LTDA",
        "CNPJ: 38.825.791/0001-61",
        "",
        "CONTRATADO: Empresa de Manutenção ABC",
        "CNPJ: 12.345.678/0001-90",
        "",
        f"Data: {datetime.now().strftime('%d/%m/%Y')}",
        "",
        "OBJETO: Manutenção preventiva e corretiva de equipamentos",
        "",
        "VALOR: R$ 2.000,00 mensais",
        "",
        "VIGÊNCIA: 12 meses",
    ]
    
    for linha in linhas:
        c.drawString(100, y, linha)
        y -= 20
    
    c.save()
    return pdf_path

async def test_funcionalidades():
    """Testa funcionalidades avançadas"""
    
    print(f"\n⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Teste 1: Simular fechamento de caixa
    print("💰 Teste 1: Fechamento de caixa")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="fechei 2500"
        )
        print("✅ Mensagem de fechamento enviada")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Criar lembrete
    print("\n📝 Teste 2: Criar lembrete")
    try:
        amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m')
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text=f"me lembra amanhã às 14h de ligar pro contador"
        )
        print("✅ Mensagem de lembrete enviada")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Enviar boleto (deve classificar como Financeiro)
    print("\n💳 Teste 3: Enviar boleto (classificação automática)")
    try:
        boleto_path = criar_boleto_teste()
        with open(boleto_path, 'rb') as f:
            await bot.send_document(
                chat_id=GROUP_ID,
                message_thread_id=TOPIC_CHAT,
                document=f,
                caption="Boleto da luz que chegou hoje"
            )
        print("✅ Boleto enviado para classificação")
        os.remove(boleto_path)
        await asyncio.sleep(5)  # Aguarda processamento da IA
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 4: Enviar comprovante (deve classificar como Financeiro)
    print("\n🧾 Teste 4: Enviar comprovante (classificação automática)")
    try:
        comprovante_path = criar_comprovante_teste()
        with open(comprovante_path, 'rb') as f:
            await bot.send_document(
                chat_id=GROUP_ID,
                message_thread_id=TOPIC_CHAT,
                document=f,
                caption="Comprovante de pagamento ao fornecedor"
            )
        print("✅ Comprovante enviado para classificação")
        os.remove(comprovante_path)
        await asyncio.sleep(5)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 5: Enviar contrato (deve classificar como Jurídico)
    print("\n📄 Teste 5: Enviar contrato (classificação automática)")
    try:
        contrato_path = criar_contrato_teste()
        with open(contrato_path, 'rb') as f:
            await bot.send_document(
                chat_id=GROUP_ID,
                message_thread_id=TOPIC_CHAT,
                document=f,
                caption="Contrato de manutenção para assinar"
            )
        print("✅ Contrato enviado para classificação")
        os.remove(contrato_path)
        await asyncio.sleep(5)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 6: Buscar documento
    print("\n🔍 Teste 6: Buscar documento")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="cadê o contrato?"
        )
        print("✅ Mensagem de busca enviada")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 7: Listar lembretes
    print("\n📋 Teste 7: Listar lembretes")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="quais meus lembretes?"
        )
        print("✅ Mensagem para listar lembretes enviada")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 8: Conversa livre
    print("\n💬 Teste 8: Conversa livre com IA")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="Oi! Como você está?"
        )
        print("✅ Mensagem de conversa enviada")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 9: Criar documento
    print("\n📝 Teste 9: Criar documento")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="cria um pdf com: Lista de Tarefas\n1. Conferir estoque\n2. Pagar fornecedores\n3. Revisar contratos"
        )
        print("✅ Solicitação de criação de PDF enviada")
        await asyncio.sleep(5)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 10: Solicitar relatório
    print("\n📊 Teste 10: Solicitar relatório")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="mostra gráfico da semana"
        )
        print("✅ Solicitação de relatório enviada")
        await asyncio.sleep(3)
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Mensagem final
    print("\n✅ Teste 11: Mensagem de conclusão")
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=TOPIC_CHAT,
            text="🧪 **TESTE DE FUNCIONALIDADES CONCLUÍDO**\n\n"
                 "Funcionalidades testadas:\n"
                 "✅ Fechamento de caixa\n"
                 "✅ Criação de lembretes\n"
                 "✅ Classificação automática de documentos\n"
                 "✅ Busca de documentos\n"
                 "✅ Listagem de lembretes\n"
                 "✅ Conversa com IA\n"
                 "✅ Criação de documentos\n"
                 "✅ Relatórios\n\n"
                 "Aguarde alguns segundos para ver as respostas do bot! 🤖",
            parse_mode='Markdown'
        )
        print("✅ Mensagem final enviada")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Resumo
    print("\n" + "=" * 80)
    print("🎯 RESUMO DO TESTE DE FUNCIONALIDADES")
    print("=" * 80)
    print("✅ Fechamento de caixa: Enviado")
    print("✅ Lembretes: Enviado")
    print("✅ Classificação de boleto: Enviado")
    print("✅ Classificação de comprovante: Enviado")
    print("✅ Classificação de contrato: Enviado")
    print("✅ Busca de documentos: Enviado")
    print("✅ Listar lembretes: Enviado")
    print("✅ Conversa com IA: Enviado")
    print("✅ Criar documento: Enviado")
    print("✅ Relatório: Enviado")
    print("\n📱 Agora verifique o Telegram para ver as respostas do bot!")
    print("   O bot deve processar cada mensagem e responder adequadamente.")
    print("=" * 80)
    print(f"\n⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

if __name__ == "__main__":
    asyncio.run(test_funcionalidades())
