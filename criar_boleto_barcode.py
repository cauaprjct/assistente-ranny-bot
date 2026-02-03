"""Cria um PDF de boleto com código de barras para teste"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Cria PDF
c = canvas.Canvas("boleto_gas_teste.pdf", pagesize=A4)
width, height = A4

# Título
c.setFont("Helvetica-Bold", 16)
c.drawString(200, height - 50, "BOLETO BANCÁRIO")

# Dados do boleto
c.setFont("Helvetica", 12)
c.drawString(50, height - 100, "Beneficiário: NATURGY GÁS NATURAL")
c.drawString(50, height - 130, "CNPJ: 33.938.119/0001-69")
c.drawString(50, height - 160, "Valor: R$ 78,50")
c.drawString(50, height - 190, "Vencimento: 28/01/2026")
c.drawString(50, height - 220, "Nosso Número: 987654321")
c.drawString(50, height - 250, "Descrição: Conta de Gás - Janeiro/2026")

# Código de barras / Linha digitável
c.setFont("Helvetica-Bold", 10)
c.drawString(50, height - 300, "Linha Digitável:")
c.setFont("Courier", 10)
c.drawString(50, height - 320, "23793.38128 60000.000003 00000.000400 1 92340000007850")

c.save()
print("✅ Boleto de teste criado: boleto_gas_teste.pdf")
