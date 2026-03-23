"""
📄 Sistema de Templates PDF
Assistente Ranny V3

Funcionalidades:
- Templates pré-definidos para documentos comuns
- Renderização com variáveis dinâmicas
- Integração com sistema de confirmação do bot
"""

import io
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Tenta importar reportlab
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib.colors import HexColor, black, grey
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("ReportLab não instalado - templates PDF desabilitados")


# ============ TEMPLATES PRÉ-DEFINIDOS ============

TEMPLATES_PDF_DISPONIVEIS = {
    'relatorio_entregas': {
        'descricao': 'Relatório de entregas para entregadores',
        'variaveis': ['periodo', 'entregador', 'total_entregas', 'valor_total', 'dias_trabalhados'],
        'categoria': 'pizzaria'
    },
    'recibo_pagamento': {
        'descricao': 'Recibo de pagamento',
        'variaveis': ['valor', 'valor_extenso', 'referente', 'pagador', 'recebedor', 'cpf_recebedor', 'data'],
        'categoria': 'financeiro'
    },
    'comprovante_entrega': {
        'descricao': 'Comprovante de entrega realizada',
        'variaveis': ['cliente', 'endereco', 'pedido', 'valor', 'entregador', 'data', 'hora'],
        'categoria': 'pizzaria'
    },
    'relatorio_semanal': {
        'descricao': 'Relatório semanal da pizzaria',
        'variaveis': ['periodo', 'total_pedidos', 'faturamento', 'entregas', 'destaques'],
        'categoria': 'pizzaria'
    },
    'contrato_simples': {
        'descricao': 'Contrato simples de prestação de serviços',
        'variaveis': ['contratante', 'cpf_contratante', 'contratado', 'cpf_contratado', 'servico', 'valor', 'data_inicio', 'data_fim'],
        'categoria': 'juridico'
    }
}


def listar_templates_pdf() -> Dict[str, Dict]:
    """Lista todos os templates PDF disponíveis
    
    Returns:
        Dict com templates e suas informações
    """
    return TEMPLATES_PDF_DISPONIVEIS


def obter_template_pdf(nome_template: str) -> Optional[Dict]:
    """Obtém informações de um template PDF específico
    
    Args:
        nome_template: Nome do template
    
    Returns:
        Dict com informações do template ou None se não existir
    """
    return TEMPLATES_PDF_DISPONIVEIS.get(nome_template)


def renderizar_template_pdf(nome_template: str, contexto: Dict[str, Any]) -> Optional[bytes]:
    """Renderiza um template PDF com variáveis
    
    Args:
        nome_template: Nome do template (ex: 'relatorio_entregas')
        contexto: Dict com variáveis para o template
    
    Returns:
        bytes do PDF renderizado ou None se falhar
    """
    if not HAS_REPORTLAB:
        logger.error("ReportLab não instalado")
        return None
    
    template_info = TEMPLATES_PDF_DISPONIVEIS.get(nome_template)
    if not template_info:
        logger.error(f"Template PDF não encontrado: {nome_template}")
        return None
    
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        styles = getSampleStyleSheet()
        elementos = []
        
        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'TituloCustom',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=HexColor('#2C3E50'),
            alignment=1  # Centralizado
        )
        
        subtitulo_style = ParagraphStyle(
            'SubtituloCustom',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#7F8C8D'),
            alignment=1,
            spaceAfter=30
        )
        
        corpo_style = ParagraphStyle(
            'CorpoCustom',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=12,
            textColor=HexColor('#333333')
        )
        
        # Renderiza baseado no tipo de template
        if nome_template == 'relatorio_entregas':
            elementos = _render_relatorio_entregas(contexto, styles, titulo_style, subtitulo_style, corpo_style)
        elif nome_template == 'recibo_pagamento':
            elementos = _render_recibo_pagamento(contexto, styles, titulo_style, subtitulo_style, corpo_style)
        elif nome_template == 'comprovante_entrega':
            elementos = _render_comprovante_entrega(contexto, styles, titulo_style, subtitulo_style, corpo_style)
        elif nome_template == 'relatorio_semanal':
            elementos = _render_relatorio_semanal(contexto, styles, titulo_style, subtitulo_style, corpo_style)
        elif nome_template == 'contrato_simples':
            elementos = _render_contrato_simples(contexto, styles, titulo_style, subtitulo_style, corpo_style)
        else:
            # Template genérico
            elementos = _render_generico(contexto, styles, titulo_style, subtitulo_style, corpo_style)
        
        # Gera o PDF
        doc.build(elementos)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Template PDF '{nome_template}' renderizado: {len(pdf_bytes)} bytes")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Erro ao renderizar template PDF: {e}")
        return None


def _render_relatorio_entregas(ctx: dict, styles, titulo_style, subtitulo_style, corpo_style) -> list:
    """Renderiza relatório de entregas"""
    elementos = []
    
    # Título
    elementos.append(Paragraph("RELATÓRIO DE ENTREGAS", titulo_style))
    
    # Período
    periodo = ctx.get('periodo', datetime.now().strftime('%d/%m/%Y'))
    elementos.append(Paragraph(f"Período: {periodo}", subtitulo_style))
    
    # Dados do entregador
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph(f"<b>Entregador:</b> {ctx.get('entregador', 'N/A')}", corpo_style))
    elementos.append(Paragraph(f"<b>Total de Entregas:</b> {ctx.get('total_entregas', 0)}", corpo_style))
    elementos.append(Paragraph(f"<b>Valor Total:</b> R$ {ctx.get('valor_total', '0,00')}", corpo_style))
    elementos.append(Paragraph(f"<b>Dias Trabalhados:</b> {ctx.get('dias_trabalhados', 0)}", corpo_style))
    
    # Rodapé
    elementos.append(Spacer(1, 40))
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=grey, alignment=1)
    elementos.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny", rodape_style))
    
    return elementos


def _render_recibo_pagamento(ctx: dict, styles, titulo_style, subtitulo_style, corpo_style) -> list:
    """Renderiza recibo de pagamento"""
    elementos = []
    
    # Título
    elementos.append(Paragraph("RECIBO DE PAGAMENTO", titulo_style))
    elementos.append(Spacer(1, 30))
    
    # Valor
    valor_style = ParagraphStyle('Valor', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=20)
    elementos.append(Paragraph(f"<b>VALOR: R$ {ctx.get('valor', '0,00')}</b>", valor_style))
    
    # Texto do recibo
    texto = f"""
    Recebi de <b>{ctx.get('pagador', 'N/A')}</b> a quantia de <b>R$ {ctx.get('valor', '0,00')}</b>
    ({ctx.get('valor_extenso', 'valor por extenso')}), referente a <b>{ctx.get('referente', 'serviços prestados')}</b>.
    """
    elementos.append(Paragraph(texto.replace('\n', '<br/>'), corpo_style))
    
    # Dados do recebedor
    elementos.append(Spacer(1, 30))
    elementos.append(Paragraph(f"<b>Recebedor:</b> {ctx.get('recebedor', 'N/A')}", corpo_style))
    elementos.append(Paragraph(f"<b>CPF:</b> {ctx.get('cpf_recebedor', 'N/A')}", corpo_style))
    elementos.append(Paragraph(f"<b>Data:</b> {ctx.get('data', datetime.now().strftime('%d/%m/%Y'))}", corpo_style))
    
    # Assinatura
    elementos.append(Spacer(1, 50))
    assinatura_style = ParagraphStyle('Assinatura', parent=styles['Normal'], fontSize=10, alignment=1)
    elementos.append(Paragraph("_" * 40, assinatura_style))
    elementos.append(Paragraph("Assinatura", assinatura_style))
    
    # Rodapé
    elementos.append(Spacer(1, 30))
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=grey, alignment=1)
    elementos.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny", rodape_style))
    
    return elementos


def _render_comprovante_entrega(ctx: dict, styles, titulo_style, subtitulo_style, corpo_style) -> list:
    """Renderiza comprovante de entrega"""
    elementos = []
    
    # Título
    elementos.append(Paragraph("COMPROVANTE DE ENTREGA", titulo_style))
    elementos.append(Spacer(1, 20))
    
    # Dados da entrega
    dados = [
        ['Cliente:', ctx.get('cliente', 'N/A')],
        ['Endereço:', ctx.get('endereco', 'N/A')],
        ['Pedido:', ctx.get('pedido', 'N/A')],
        ['Valor:', f"R$ {ctx.get('valor', '0,00')}"],
        ['Entregador:', ctx.get('entregador', 'N/A')],
        ['Data:', ctx.get('data', datetime.now().strftime('%d/%m/%Y'))],
        ['Hora:', ctx.get('hora', datetime.now().strftime('%H:%M'))],
    ]
    
    tabela = Table(dados, colWidths=[3*cm, 10*cm])
    tabela.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elementos.append(tabela)
    
    # Rodapé
    elementos.append(Spacer(1, 40))
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=grey, alignment=1)
    elementos.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny", rodape_style))
    
    return elementos


def _render_relatorio_semanal(ctx: dict, styles, titulo_style, subtitulo_style, corpo_style) -> list:
    """Renderiza relatório semanal"""
    elementos = []
    
    # Título
    elementos.append(Paragraph("RELATÓRIO SEMANAL", titulo_style))
    
    periodo = ctx.get('periodo', datetime.now().strftime('%d/%m/%Y'))
    elementos.append(Paragraph(f"Período: {periodo}", subtitulo_style))
    
    # Resumo
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("<b>RESUMO DA SEMANA</b>", corpo_style))
    elementos.append(Spacer(1, 10))
    
    dados = [
        ['Total de Pedidos:', str(ctx.get('total_pedidos', 0))],
        ['Faturamento:', f"R$ {ctx.get('faturamento', '0,00')}"],
        ['Entregas Realizadas:', str(ctx.get('entregas', 0))],
    ]
    
    tabela = Table(dados, colWidths=[5*cm, 5*cm])
    tabela.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elementos.append(tabela)
    
    # Destaques
    destaques = ctx.get('destaques', '')
    if destaques:
        elementos.append(Spacer(1, 20))
        elementos.append(Paragraph("<b>Destaques:</b>", corpo_style))
        elementos.append(Paragraph(destaques, corpo_style))
    
    # Rodapé
    elementos.append(Spacer(1, 40))
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=grey, alignment=1)
    elementos.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny", rodape_style))
    
    return elementos


def _render_contrato_simples(ctx: dict, styles, titulo_style, subtitulo_style, corpo_style) -> list:
    """Renderiza contrato simples"""
    elementos = []
    
    # Título
    elementos.append(Paragraph("CONTRATO DE PRESTAÇÃO DE SERVIÇOS", titulo_style))
    elementos.append(Spacer(1, 30))
    
    # Texto do contrato
    texto = f"""
    <b>CONTRATANTE:</b> {ctx.get('contratante', 'N/A')}, CPF: {ctx.get('cpf_contratante', 'N/A')}<br/><br/>
    
    <b>CONTRATADO:</b> {ctx.get('contratado', 'N/A')}, CPF: {ctx.get('cpf_contratado', 'N/A')}<br/><br/>
    
    <b>CLÁUSULA PRIMEIRA - DO OBJETO</b><br/>
    O presente contrato tem por objeto a prestação de serviços de {ctx.get('servico', 'serviços diversos')}.<br/><br/>
    
    <b>CLÁUSULA SEGUNDA - DO VALOR</b><br/>
    Pelos serviços prestados, o CONTRATANTE pagará ao CONTRATADO o valor de <b>R$ {ctx.get('valor', '0,00')}</b>.<br/><br/>
    
    <b>CLÁUSULA TERCEIRA - DO PRAZO</b><br/>
    O presente contrato terá vigência de {ctx.get('data_inicio', '___/___/______')} a {ctx.get('data_fim', '___/___/______')}.<br/><br/>
    
    <b>CLÁUSULA QUARTA - DAS DISPOSIÇÕES GERAIS</b><br/>
    As partes elegem o foro da Comarca de domicílio do CONTRATANTE para dirimir quaisquer dúvidas decorrentes do presente contrato.
    """
    
    elementos.append(Paragraph(texto.replace('\n', '<br/>'), corpo_style))
    
    # Assinaturas
    elementos.append(Spacer(1, 50))
    assinatura_style = ParagraphStyle('Assinatura', parent=styles['Normal'], fontSize=10, alignment=1)
    
    elementos.append(Paragraph("_" * 30 + "          " + "_" * 30, assinatura_style))
    elementos.append(Paragraph("CONTRATANTE          CONTRATADO", assinatura_style))
    
    # Rodapé
    elementos.append(Spacer(1, 30))
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=grey, alignment=1)
    elementos.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny", rodape_style))
    
    return elementos


def _render_generico(ctx: dict, styles, titulo_style, subtitulo_style, corpo_style) -> list:
    """Renderiza documento genérico"""
    elementos = []
    
    # Título
    elementos.append(Paragraph("DOCUMENTO", titulo_style))
    elementos.append(Spacer(1, 20))
    
    # Dados
    for chave, valor in ctx.items():
        elementos.append(Paragraph(f"<b>{chave.replace('_', ' ').title()}:</b> {valor}", corpo_style))
    
    # Rodapé
    elementos.append(Spacer(1, 40))
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=grey, alignment=1)
    elementos.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny", rodape_style))
    
    return elementos
