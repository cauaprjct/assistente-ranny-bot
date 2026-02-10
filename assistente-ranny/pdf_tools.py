"""
📄 Ferramentas de PDF - Criação e Edição
Assistente Ranny V3

Funcionalidades:
- Criar PDF a partir de texto
- Mesclar múltiplos PDFs
- Extrair páginas específicas
- Comprimir PDF
- Adicionar marca d'água
- Converter imagens em PDF
"""

import io
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Importa bibliotecas de PDF
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF não instalado - algumas funções de PDF desabilitadas")

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("ReportLab não instalado - criação de PDF desabilitada")

# Importa bibliotecas do Office
try:
    from docx import Document
    from docx.shared import Inches, Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    logger.warning("python-docx não instalado - criação de DOCX desabilitada")

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_XLSX = True
except ImportError:
    HAS_XLSX = False
    logger.warning("openpyxl não instalado - criação de XLSX desabilitada")


def criar_pdf_texto(texto: str, titulo: str = None) -> Optional[bytes]:
    """Cria um PDF a partir de texto
    
    Args:
        texto: Conteúdo do PDF
        titulo: Título opcional do documento
    
    Returns:
        bytes do PDF ou None se falhar
    """
    if not HAS_REPORTLAB:
        logger.error("ReportLab não instalado")
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
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para título
        titulo_style = ParagraphStyle(
            'TituloCustom',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=HexColor('#2C3E50'),
            alignment=1  # Centralizado
        )
        
        # Estilo para corpo do texto
        corpo_style = ParagraphStyle(
            'CorpoCustom',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=12,
            textColor=HexColor('#333333')
        )
        
        # Estilo para rodapé
        rodape_style = ParagraphStyle(
            'RodapeCustom',
            parent=styles['Normal'],
            fontSize=8,
            textColor=HexColor('#888888'),
            alignment=1
        )
        
        elementos = []
        
        # Título
        if titulo:
            elementos.append(Paragraph(titulo, titulo_style))
            elementos.append(Spacer(1, 20))
        
        # Processa o texto - divide em parágrafos
        paragrafos = texto.split('\n')
        for p in paragrafos:
            p = p.strip()
            if p:
                # Escapa caracteres especiais do HTML
                p = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                elementos.append(Paragraph(p, corpo_style))
            else:
                elementos.append(Spacer(1, 10))
        
        # Rodapé com data
        elementos.append(Spacer(1, 30))
        data_atual = datetime.now().strftime('%d/%m/%Y às %H:%M')
        elementos.append(Paragraph(f"Gerado em {data_atual} • Assistente Ranny", rodape_style))
        
        # Gera o PDF
        doc.build(elementos)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"PDF criado com sucesso: {len(pdf_bytes)} bytes")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Erro ao criar PDF: {e}")
        return None


def mesclar_pdfs(pdfs: List[bytes]) -> Optional[bytes]:
    """Mescla múltiplos PDFs em um único arquivo
    
    Args:
        pdfs: Lista de bytes de PDFs
    
    Returns:
        bytes do PDF mesclado ou None se falhar
    """
    if not HAS_PYMUPDF:
        logger.error("PyMuPDF não instalado")
        return None
    
    if len(pdfs) < 2:
        logger.error("Precisa de pelo menos 2 PDFs para mesclar")
        return None
    
    try:
        # Cria documento de saída
        pdf_saida = fitz.open()
        
        for i, pdf_bytes in enumerate(pdfs):
            try:
                pdf_entrada = fitz.open(stream=pdf_bytes, filetype="pdf")
                pdf_saida.insert_pdf(pdf_entrada)
                pdf_entrada.close()
                logger.info(f"PDF {i+1} adicionado ({len(pdf_bytes)} bytes)")
            except Exception as e:
                logger.error(f"Erro ao processar PDF {i+1}: {e}")
                continue
        
        if pdf_saida.page_count == 0:
            logger.error("Nenhuma página foi adicionada")
            return None
        
        # Salva em bytes
        output = io.BytesIO()
        pdf_saida.save(output)
        pdf_saida.close()
        
        result = output.getvalue()
        output.close()
        
        logger.info(f"PDFs mesclados: {len(result)} bytes, {pdf_saida.page_count} páginas")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao mesclar PDFs: {e}")
        return None


def extrair_paginas(pdf_bytes: bytes, paginas: List[int]) -> Optional[bytes]:
    """Extrai páginas específicas de um PDF
    
    Args:
        pdf_bytes: bytes do PDF original
        paginas: Lista de números de página (1-indexed)
    
    Returns:
        bytes do PDF com as páginas extraídas ou None se falhar
    """
    if not HAS_PYMUPDF:
        logger.error("PyMuPDF não instalado")
        return None
    
    try:
        pdf_entrada = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_paginas = pdf_entrada.page_count
        
        # Valida páginas
        paginas_validas = []
        for p in paginas:
            if 1 <= p <= total_paginas:
                paginas_validas.append(p - 1)  # Converte para 0-indexed
            else:
                logger.warning(f"Página {p} inválida (total: {total_paginas})")
        
        if not paginas_validas:
            logger.error("Nenhuma página válida especificada")
            pdf_entrada.close()
            return None
        
        # Cria novo PDF com as páginas selecionadas
        pdf_saida = fitz.open()
        
        for page_num in paginas_validas:
            pdf_saida.insert_pdf(pdf_entrada, from_page=page_num, to_page=page_num)
        
        pdf_entrada.close()
        
        # Salva em bytes
        output = io.BytesIO()
        pdf_saida.save(output)
        pdf_saida.close()
        
        result = output.getvalue()
        output.close()
        
        logger.info(f"Páginas extraídas: {paginas_validas}, {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao extrair páginas: {e}")
        return None


def comprimir_pdf(pdf_bytes: bytes, qualidade: str = "media") -> Optional[Tuple[bytes, dict]]:
    """Comprime um PDF reduzindo seu tamanho
    
    Args:
        pdf_bytes: bytes do PDF original
        qualidade: 'baixa', 'media' ou 'alta'
    
    Returns:
        Tuple (bytes do PDF comprimido, dict com info) ou None se falhar
    """
    if not HAS_PYMUPDF:
        logger.error("PyMuPDF não instalado")
        return None
    
    try:
        tamanho_original = len(pdf_bytes)
        
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Configurações de compressão baseadas na qualidade
        if qualidade == "baixa":
            # Máxima compressão, menor qualidade
            garbage = 4
            deflate = True
            clean = True
        elif qualidade == "alta":
            # Mínima compressão, maior qualidade
            garbage = 1
            deflate = True
            clean = False
        else:  # media
            garbage = 3
            deflate = True
            clean = True
        
        # Salva com compressão
        output = io.BytesIO()
        pdf.save(
            output,
            garbage=garbage,
            deflate=deflate,
            clean=clean,
            linear=True  # Otimiza para web
        )
        pdf.close()
        
        result = output.getvalue()
        output.close()
        
        tamanho_final = len(result)
        reducao = ((tamanho_original - tamanho_final) / tamanho_original) * 100
        
        info = {
            'tamanho_original': tamanho_original,
            'tamanho_final': tamanho_final,
            'reducao_percentual': round(reducao, 1),
            'qualidade': qualidade
        }
        
        logger.info(f"PDF comprimido: {tamanho_original} -> {tamanho_final} bytes ({reducao:.1f}% redução)")
        return result, info
        
    except Exception as e:
        logger.error(f"Erro ao comprimir PDF: {e}")
        return None


def adicionar_marca_dagua(pdf_bytes: bytes, texto: str, opacidade: float = 0.3) -> Optional[bytes]:
    """Adiciona marca d'água em todas as páginas do PDF
    
    Args:
        pdf_bytes: bytes do PDF original
        texto: Texto da marca d'água
        opacidade: Opacidade da marca (0.0 a 1.0)
    
    Returns:
        bytes do PDF com marca d'água ou None se falhar
    """
    if not HAS_PYMUPDF:
        logger.error("PyMuPDF não instalado")
        return None
    
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page in pdf:
            # Obtém dimensões da página
            rect = page.rect
            
            # Configura a marca d'água
            # Posiciona no centro da página, rotacionada
            center_x = rect.width / 2
            center_y = rect.height / 2
            
            # Adiciona texto como marca d'água
            page.insert_text(
                (center_x - len(texto) * 5, center_y),  # Posição aproximada
                texto,
                fontsize=50,
                fontname="helv",
                color=(0.5, 0.5, 0.5),  # Cinza
                rotate=45,  # Rotação diagonal
                overlay=True
            )
        
        # Salva em bytes
        output = io.BytesIO()
        pdf.save(output)
        pdf.close()
        
        result = output.getvalue()
        output.close()
        
        logger.info(f"Marca d'água adicionada: '{texto}'")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao adicionar marca d'água: {e}")
        return None


def imagens_para_pdf(imagens: List[bytes]) -> Optional[bytes]:
    """Converte uma ou mais imagens em PDF
    
    Args:
        imagens: Lista de bytes de imagens (PNG, JPG, etc)
    
    Returns:
        bytes do PDF ou None se falhar
    """
    if not HAS_PYMUPDF:
        logger.error("PyMuPDF não instalado")
        return None
    
    try:
        pdf = fitz.open()
        
        for i, img_bytes in enumerate(imagens):
            try:
                # Abre a imagem
                img = fitz.open(stream=img_bytes, filetype="png")
                
                # Converte para PDF
                pdf_bytes_temp = img.convert_to_pdf()
                img.close()
                
                # Abre o PDF temporário e insere no documento principal
                img_pdf = fitz.open(stream=pdf_bytes_temp, filetype="pdf")
                pdf.insert_pdf(img_pdf)
                img_pdf.close()
                
                logger.info(f"Imagem {i+1} adicionada ao PDF")
                
            except Exception as e:
                logger.error(f"Erro ao processar imagem {i+1}: {e}")
                continue
        
        if pdf.page_count == 0:
            logger.error("Nenhuma imagem foi convertida")
            return None
        
        # Salva em bytes
        output = io.BytesIO()
        pdf.save(output)
        pdf.close()
        
        result = output.getvalue()
        output.close()
        
        logger.info(f"Imagens convertidas para PDF: {len(result)} bytes, {pdf.page_count} páginas")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao converter imagens para PDF: {e}")
        return None


def get_pdf_info(pdf_bytes: bytes) -> Optional[dict]:
    """Obtém informações sobre um PDF
    
    Args:
        pdf_bytes: bytes do PDF
    
    Returns:
        dict com informações ou None se falhar
    """
    if not HAS_PYMUPDF:
        logger.error("PyMuPDF não instalado")
        return None
    
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        info = {
            'paginas': pdf.page_count,
            'tamanho_bytes': len(pdf_bytes),
            'tamanho_formatado': _formatar_tamanho(len(pdf_bytes)),
            'titulo': pdf.metadata.get('title', ''),
            'autor': pdf.metadata.get('author', ''),
            'criado': pdf.metadata.get('creationDate', ''),
            'modificado': pdf.metadata.get('modDate', ''),
            'criptografado': pdf.is_encrypted,
        }
        
        # Obtém dimensões da primeira página
        if pdf.page_count > 0:
            page = pdf[0]
            rect = page.rect
            info['largura_mm'] = round(rect.width * 25.4 / 72, 1)
            info['altura_mm'] = round(rect.height * 25.4 / 72, 1)
        
        pdf.close()
        return info
        
    except Exception as e:
        logger.error(f"Erro ao obter info do PDF: {e}")
        return None


def _formatar_tamanho(bytes_size: int) -> str:
    """Formata tamanho em bytes para formato legível"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"


def criar_relatorio_pdf(titulo: str, dados: dict, tipo: str = "financeiro") -> Optional[bytes]:
    """Cria um relatório formatado em PDF
    
    Args:
        titulo: Título do relatório
        dados: Dados do relatório
        tipo: Tipo de relatório ('financeiro', 'vencimentos', etc)
    
    Returns:
        bytes do PDF ou None se falhar
    """
    if not HAS_REPORTLAB:
        logger.error("ReportLab não instalado")
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
        
        # Cabeçalho
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            textColor=HexColor('#1a5276'),
            alignment=1
        )
        elementos.append(Paragraph(titulo, titulo_style))
        
        # Data do relatório
        data_style = ParagraphStyle(
            'Data',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            alignment=1
        )
        data_atual = datetime.now().strftime('%d/%m/%Y às %H:%M')
        elementos.append(Paragraph(f"Gerado em {data_atual}", data_style))
        elementos.append(Spacer(1, 30))
        
        if tipo == "financeiro":
            elementos.extend(_criar_secao_financeiro(dados, styles))
        elif tipo == "vencimentos":
            elementos.extend(_criar_secao_vencimentos(dados, styles))
        else:
            # Genérico - lista os dados
            for chave, valor in dados.items():
                elementos.append(Paragraph(f"<b>{chave}:</b> {valor}", styles['Normal']))
                elementos.append(Spacer(1, 5))
        
        # Rodapé
        elementos.append(Spacer(1, 40))
        rodape_style = ParagraphStyle(
            'Rodape',
            parent=styles['Normal'],
            fontSize=8,
            textColor=HexColor('#999999'),
            alignment=1
        )
        elementos.append(Paragraph("Relatório gerado automaticamente pelo Assistente Ranny", rodape_style))
        
        doc.build(elementos)
        
        result = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Relatório PDF criado: {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao criar relatório PDF: {e}")
        return None


def _criar_secao_financeiro(dados: dict, styles) -> list:
    """Cria seção de relatório financeiro"""
    elementos = []
    
    # Resumo
    if 'resumo' in dados:
        subtitulo = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceAfter=10
        )
        elementos.append(Paragraph("📊 Resumo", subtitulo))
        
        resumo = dados['resumo']
        texto_resumo = f"""
        <b>Total:</b> R$ {resumo.get('total', 0):,.2f}<br/>
        <b>Média diária:</b> R$ {resumo.get('media', 0):,.2f}<br/>
        <b>Período:</b> {resumo.get('periodo', 'N/A')}
        """
        elementos.append(Paragraph(texto_resumo, styles['Normal']))
        elementos.append(Spacer(1, 20))
    
    # Tabela de fechamentos
    if 'fechamentos' in dados and dados['fechamentos']:
        elementos.append(Paragraph("💰 Fechamentos", styles['Heading2']))
        elementos.append(Spacer(1, 10))
        
        # Cabeçalho da tabela
        table_data = [['Data', 'Valor']]
        
        for f in dados['fechamentos'][:30]:  # Limita a 30 registros
            data = f.get('data', '')[:10] if f.get('data') else ''
            valor = f"R$ {f.get('valor', 0):,.2f}"
            table_data.append([data, valor])
        
        table = Table(table_data, colWidths=[8*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f8f9fa')]),
        ]))
        elementos.append(table)
    
    return elementos


def _criar_secao_vencimentos(dados: dict, styles) -> list:
    """Cria seção de relatório de vencimentos"""
    elementos = []
    
    if 'vencimentos' in dados and dados['vencimentos']:
        # Tabela de vencimentos
        table_data = [['Descrição', 'Vencimento', 'Valor', 'Status']]
        
        for v in dados['vencimentos']:
            desc = v.get('descricao', '')[:30]
            venc = v.get('vencimento', '')[:10] if v.get('vencimento') else ''
            valor = f"R$ {v.get('valor', 0):,.2f}" if v.get('valor') else '-'
            status = '✅ Pago' if v.get('pago') else '⏳ Pendente'
            table_data.append([desc, venc, valor, status])
        
        table = Table(table_data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#fdf2f2')]),
        ]))
        elementos.append(table)
    
    return elementos


# ============ FUNÇÕES PARA DOCX (Word) ============

def criar_docx_texto(texto: str, titulo: str = None) -> Optional[bytes]:
    """Cria um documento Word (DOCX) a partir de texto
    
    Args:
        texto: Conteúdo do documento
        titulo: Título opcional do documento
    
    Returns:
        bytes do DOCX ou None se falhar
    """
    if not HAS_DOCX:
        logger.error("python-docx não instalado")
        return None
    
    try:
        doc = Document()
        
        # Adiciona título se fornecido
        if titulo:
            heading = doc.add_heading(titulo, level=1)
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph()  # Espaço após título
        
        # Processa o texto - divide em parágrafos
        paragrafos = texto.split('\n')
        for p in paragrafos:
            p = p.strip()
            if p:
                # Verifica se é um item de lista (começa com • ou -)
                if p.startswith('•') or p.startswith('-'):
                    item_texto = p.lstrip('•-').strip()
                    doc.add_paragraph(item_texto, style='List Bullet')
                else:
                    doc.add_paragraph(p)
            else:
                doc.add_paragraph()  # Linha em branco
        
        # Adiciona rodapé com data
        doc.add_paragraph()
        rodape = doc.add_paragraph()
        rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = rodape.add_run(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny")
        run.font.size = Pt(8)
        run.font.italic = True
        
        # Salva em bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        
        result = buffer.getvalue()
        buffer.close()
        
        logger.info(f"DOCX criado com sucesso: {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao criar DOCX: {e}")
        return None


def criar_docx_tabela(dados: list, cabecalho: list = None, titulo: str = None) -> Optional[bytes]:
    """Cria um documento Word com uma tabela
    
    Args:
        dados: Lista de listas com os dados da tabela
        cabecalho: Lista com os títulos das colunas (opcional)
        titulo: Título do documento (opcional)
    
    Returns:
        bytes do DOCX ou None se falhar
    """
    if not HAS_DOCX:
        logger.error("python-docx não instalado")
        return None
    
    try:
        doc = Document()
        
        # Adiciona título se fornecido
        if titulo:
            heading = doc.add_heading(titulo, level=1)
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph()
        
        # Determina número de colunas
        if cabecalho:
            num_cols = len(cabecalho)
        elif dados:
            num_cols = len(dados[0]) if isinstance(dados[0], (list, tuple)) else 1
        else:
            logger.error("Dados vazios para criar tabela")
            return None
        
        # Cria tabela
        num_rows = len(dados) + (1 if cabecalho else 0)
        table = doc.add_table(rows=num_rows, cols=num_cols)
        table.style = 'Table Grid'
        
        # Adiciona cabeçalho
        row_idx = 0
        if cabecalho:
            for col_idx, header in enumerate(cabecalho):
                cell = table.rows[0].cells[col_idx]
                cell.text = str(header)
                # Negrito no cabeçalho
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
            row_idx = 1
        
        # Adiciona dados
        for data_row in dados:
            if isinstance(data_row, (list, tuple)):
                for col_idx, value in enumerate(data_row):
                    if col_idx < num_cols:
                        table.rows[row_idx].cells[col_idx].text = str(value)
            else:
                table.rows[row_idx].cells[0].text = str(data_row)
            row_idx += 1
        
        # Rodapé
        doc.add_paragraph()
        rodape = doc.add_paragraph()
        rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = rodape.add_run(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Assistente Ranny")
        run.font.size = Pt(8)
        run.font.italic = True
        
        # Salva em bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        
        result = buffer.getvalue()
        buffer.close()
        
        logger.info(f"DOCX com tabela criado: {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao criar DOCX com tabela: {e}")
        return None


# ============ FUNÇÕES PARA XLSX (Excel) ============

def criar_xlsx_texto(texto: str, titulo: str = None) -> Optional[bytes]:
    """Cria uma planilha Excel (XLSX) a partir de texto
    
    O texto é dividido em linhas e cada linha vira uma célula na coluna A.
    Se houver separadores (vírgula, ponto-e-vírgula, tab), divide em colunas.
    
    Args:
        texto: Conteúdo da planilha
        titulo: Título opcional (vai na primeira linha)
    
    Returns:
        bytes do XLSX ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Dados"
        
        # Estilos
        header_font = Font(bold=True, size=14, color="FFFFFF")
        header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center")
        
        row_num = 1
        
        # Adiciona título se fornecido
        if titulo:
            ws.cell(row=row_num, column=1, value=titulo)
            ws.cell(row=row_num, column=1).font = header_font
            ws.cell(row=row_num, column=1).fill = header_fill
            ws.cell(row=row_num, column=1).alignment = header_align
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
            row_num += 2  # Pula uma linha após o título
        
        # Processa o texto
        linhas = texto.split('\n')
        for linha in linhas:
            linha = linha.strip()
            if linha:
                # Remove bullet points
                if linha.startswith('•') or linha.startswith('-'):
                    linha = linha.lstrip('•-').strip()
                
                # Tenta detectar separador
                if '\t' in linha:
                    valores = linha.split('\t')
                elif ';' in linha:
                    valores = linha.split(';')
                elif ',' in linha and linha.count(',') >= 2:
                    valores = linha.split(',')
                else:
                    valores = [linha]
                
                for col_num, valor in enumerate(valores, 1):
                    ws.cell(row=row_num, column=col_num, value=valor.strip())
                
                row_num += 1
        
        # Ajusta largura das colunas
        for col in range(1, ws.max_column + 1):
            max_length = 0
            column_letter = get_column_letter(col)
            for row in range(1, ws.max_row + 1):
                cell = ws.cell(row=row, column=col)
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
        
        # Salva em bytes
        buffer = io.BytesIO()
        wb.save(buffer)
        
        result = buffer.getvalue()
        buffer.close()
        
        logger.info(f"XLSX criado com sucesso: {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao criar XLSX: {e}")
        return None


def criar_xlsx_tabela(dados: list, cabecalho: list = None, titulo: str = None) -> Optional[bytes]:
    """Cria uma planilha Excel com dados tabulares
    
    Args:
        dados: Lista de listas com os dados
        cabecalho: Lista com os títulos das colunas (opcional)
        titulo: Título da planilha (opcional)
    
    Returns:
        bytes do XLSX ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = titulo[:31] if titulo else "Dados"  # Excel limita a 31 caracteres
        
        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center")
        
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        row_num = 1
        
        # Adiciona cabeçalho
        if cabecalho:
            for col_num, header in enumerate(cabecalho, 1):
                cell = ws.cell(row=row_num, column=col_num, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_align
                cell.border = thin_border
            row_num += 1
        
        # Adiciona dados
        alt_fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
        
        for idx, data_row in enumerate(dados):
            if isinstance(data_row, (list, tuple)):
                for col_num, value in enumerate(data_row, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    cell.border = thin_border
                    if idx % 2 == 1:  # Linhas alternadas
                        cell.fill = alt_fill
            else:
                cell = ws.cell(row=row_num, column=1, value=data_row)
                cell.border = thin_border
                if idx % 2 == 1:
                    cell.fill = alt_fill
            row_num += 1
        
        # Ajusta largura das colunas
        for col in range(1, ws.max_column + 1):
            max_length = 0
            column_letter = get_column_letter(col)
            for row in range(1, ws.max_row + 1):
                cell = ws.cell(row=row, column=col)
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
        
        # Salva em bytes
        buffer = io.BytesIO()
        wb.save(buffer)
        
        result = buffer.getvalue()
        buffer.close()
        
        logger.info(f"XLSX com tabela criado: {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao criar XLSX com tabela: {e}")
        return None


def criar_xlsx_lista(itens: list, titulo: str = None, cabecalho: str = "Item") -> Optional[bytes]:
    """Cria uma planilha Excel simples com uma lista de itens
    
    Args:
        itens: Lista de itens
        titulo: Título da planilha (opcional)
        cabecalho: Título da coluna (padrão: "Item")
    
    Returns:
        bytes do XLSX ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        # Converte para formato de tabela
        dados = [[item] for item in itens]
        return criar_xlsx_tabela(dados, cabecalho=[cabecalho], titulo=titulo)
        
    except Exception as e:
        logger.error(f"Erro ao criar XLSX de lista: {e}")
        return None


# ============ FUNÇÕES DE LEITURA ============

def ler_docx(docx_bytes: bytes) -> Optional[dict]:
    """Lê um documento Word e retorna seu conteúdo estruturado
    
    Args:
        docx_bytes: bytes do arquivo DOCX
    
    Returns:
        dict com 'texto', 'paragrafos', 'tabelas' ou None se falhar
    """
    if not HAS_DOCX:
        logger.error("python-docx não instalado")
        return None
    
    try:
        doc = Document(io.BytesIO(docx_bytes))
        
        # Extrai parágrafos
        paragrafos = []
        texto_completo = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragrafos.append({
                    'texto': para.text,
                    'estilo': para.style.name if para.style else 'Normal'
                })
                texto_completo.append(para.text)
        
        # Extrai tabelas
        tabelas = []
        for table in doc.tables:
            dados_tabela = []
            for row in table.rows:
                linha = [cell.text for cell in row.cells]
                dados_tabela.append(linha)
            tabelas.append(dados_tabela)
        
        return {
            'texto': '\n'.join(texto_completo),
            'paragrafos': paragrafos,
            'tabelas': tabelas,
            'num_paragrafos': len(paragrafos),
            'num_tabelas': len(tabelas)
        }
        
    except Exception as e:
        logger.error(f"Erro ao ler DOCX: {e}")
        return None


def ler_xlsx(xlsx_bytes: bytes) -> Optional[dict]:
    """Lê uma planilha Excel e retorna seu conteúdo estruturado
    
    Args:
        xlsx_bytes: bytes do arquivo XLSX
    
    Returns:
        dict com 'planilhas', 'texto' ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = load_workbook(io.BytesIO(xlsx_bytes), read_only=True)
        
        planilhas = {}
        texto_completo = []
        
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            dados = []
            for row in sheet.iter_rows(values_only=True):
                linha = [str(cell) if cell is not None else '' for cell in row]
                if any(linha):  # Ignora linhas vazias
                    dados.append(linha)
                    texto_completo.append(' | '.join(linha))
            planilhas[sheet_name] = dados
        
        wb.close()
        
        return {
            'planilhas': planilhas,
            'texto': '\n'.join(texto_completo),
            'nomes_planilhas': list(planilhas.keys()),
            'num_planilhas': len(planilhas)
        }
        
    except Exception as e:
        logger.error(f"Erro ao ler XLSX: {e}")
        return None


# ============ FUNÇÕES DE EDIÇÃO DOCX ============

def editar_docx_adicionar_texto(docx_bytes: bytes, texto: str, posicao: str = 'fim') -> Optional[bytes]:
    """Adiciona texto a um documento Word existente
    
    Args:
        docx_bytes: bytes do arquivo DOCX original
        texto: texto a adicionar
        posicao: 'inicio' ou 'fim' (padrão: 'fim')
    
    Returns:
        bytes do DOCX modificado ou None se falhar
    """
    if not HAS_DOCX:
        logger.error("python-docx não instalado")
        return None
    
    try:
        doc = Document(io.BytesIO(docx_bytes))
        
        # Processa o texto (converte listas com " - " em parágrafos)
        linhas = texto.replace(' - ', '\n• ').split('\n')
        
        if posicao == 'inicio':
            # Adiciona no início (antes do primeiro parágrafo)
            for i, linha in enumerate(reversed(linhas)):
                if linha.strip():
                    para = doc.paragraphs[0].insert_paragraph_before(linha.strip())
        else:
            # Adiciona no fim
            for linha in linhas:
                if linha.strip():
                    doc.add_paragraph(linha.strip())
        
        # Salva em bytes
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Erro ao editar DOCX (adicionar texto): {e}")
        return None


def editar_docx_substituir(docx_bytes: bytes, texto_antigo: str, texto_novo: str) -> Optional[Tuple[bytes, int]]:
    """Substitui texto em um documento Word
    
    Args:
        docx_bytes: bytes do arquivo DOCX original
        texto_antigo: texto a ser substituído
        texto_novo: novo texto
    
    Returns:
        Tuple (bytes do DOCX modificado, número de substituições) ou None se falhar
    """
    if not HAS_DOCX:
        logger.error("python-docx não instalado")
        return None
    
    try:
        doc = Document(io.BytesIO(docx_bytes))
        substituicoes = 0
        
        # Substitui em parágrafos
        for para in doc.paragraphs:
            if texto_antigo in para.text:
                # Conta substituições
                substituicoes += para.text.count(texto_antigo)
                # Faz a substituição mantendo a formatação básica
                for run in para.runs:
                    if texto_antigo in run.text:
                        run.text = run.text.replace(texto_antigo, texto_novo)
        
        # Substitui em tabelas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if texto_antigo in cell.text:
                        substituicoes += cell.text.count(texto_antigo)
                        for para in cell.paragraphs:
                            for run in para.runs:
                                if texto_antigo in run.text:
                                    run.text = run.text.replace(texto_antigo, texto_novo)
        
        # Salva em bytes
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue(), substituicoes
        
    except Exception as e:
        logger.error(f"Erro ao editar DOCX (substituir): {e}")
        return None


def editar_docx_remover_paragrafo(docx_bytes: bytes, texto_busca: str) -> Optional[Tuple[bytes, int]]:
    """Remove parágrafos que contêm determinado texto
    
    Args:
        docx_bytes: bytes do arquivo DOCX original
        texto_busca: texto a buscar (parágrafos contendo serão removidos)
    
    Returns:
        Tuple (bytes do DOCX modificado, número de remoções) ou None se falhar
    """
    if not HAS_DOCX:
        logger.error("python-docx não instalado")
        return None
    
    try:
        doc = Document(io.BytesIO(docx_bytes))
        removidos = 0
        
        # Identifica parágrafos a remover
        for para in doc.paragraphs:
            if texto_busca.lower() in para.text.lower():
                # Remove o parágrafo
                p = para._element
                p.getparent().remove(p)
                removidos += 1
        
        # Salva em bytes
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue(), removidos
        
    except Exception as e:
        logger.error(f"Erro ao editar DOCX (remover): {e}")
        return None


# ============ FUNÇÕES DE EDIÇÃO XLSX ============

def editar_xlsx_adicionar_linha(xlsx_bytes: bytes, dados: list, planilha: str = None) -> Optional[bytes]:
    """Adiciona uma linha a uma planilha Excel
    
    Args:
        xlsx_bytes: bytes do arquivo XLSX original
        dados: lista com os valores da nova linha
        planilha: nome da planilha (usa a primeira se não especificado)
    
    Returns:
        bytes do XLSX modificado ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = load_workbook(io.BytesIO(xlsx_bytes))
        
        # Seleciona a planilha
        if planilha and planilha in wb.sheetnames:
            ws = wb[planilha]
        else:
            ws = wb.active
        
        # Adiciona a linha no final
        ws.append(dados)
        
        # Salva em bytes
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Erro ao editar XLSX (adicionar linha): {e}")
        return None


def editar_xlsx_adicionar_linhas(xlsx_bytes: bytes, linhas: list, planilha: str = None) -> Optional[bytes]:
    """Adiciona múltiplas linhas a uma planilha Excel
    
    Args:
        xlsx_bytes: bytes do arquivo XLSX original
        linhas: lista de listas com os valores das novas linhas
        planilha: nome da planilha (usa a primeira se não especificado)
    
    Returns:
        bytes do XLSX modificado ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = load_workbook(io.BytesIO(xlsx_bytes))
        
        # Seleciona a planilha
        if planilha and planilha in wb.sheetnames:
            ws = wb[planilha]
        else:
            ws = wb.active
        
        # Adiciona as linhas
        for linha in linhas:
            ws.append(linha)
        
        # Salva em bytes
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Erro ao editar XLSX (adicionar linhas): {e}")
        return None


def editar_xlsx_substituir(xlsx_bytes: bytes, texto_antigo: str, texto_novo: str, planilha: str = None) -> Optional[Tuple[bytes, int]]:
    """Substitui texto em uma planilha Excel
    
    Args:
        xlsx_bytes: bytes do arquivo XLSX original
        texto_antigo: texto a ser substituído
        texto_novo: novo texto
        planilha: nome da planilha (todas se não especificado)
    
    Returns:
        Tuple (bytes do XLSX modificado, número de substituições) ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = load_workbook(io.BytesIO(xlsx_bytes))
        substituicoes = 0
        
        # Define quais planilhas processar
        if planilha and planilha in wb.sheetnames:
            sheets = [wb[planilha]]
        else:
            sheets = wb.worksheets
        
        # Processa cada planilha
        for ws in sheets:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str) and texto_antigo in cell.value:
                        substituicoes += cell.value.count(texto_antigo)
                        cell.value = cell.value.replace(texto_antigo, texto_novo)
        
        # Salva em bytes
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue(), substituicoes
        
    except Exception as e:
        logger.error(f"Erro ao editar XLSX (substituir): {e}")
        return None


def editar_xlsx_remover_linha(xlsx_bytes: bytes, numero_linha: int, planilha: str = None) -> Optional[bytes]:
    """Remove uma linha específica de uma planilha Excel
    
    Args:
        xlsx_bytes: bytes do arquivo XLSX original
        numero_linha: número da linha a remover (1-indexed)
        planilha: nome da planilha (usa a primeira se não especificado)
    
    Returns:
        bytes do XLSX modificado ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = load_workbook(io.BytesIO(xlsx_bytes))
        
        # Seleciona a planilha
        if planilha and planilha in wb.sheetnames:
            ws = wb[planilha]
        else:
            ws = wb.active
        
        # Remove a linha
        ws.delete_rows(numero_linha)
        
        # Salva em bytes
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Erro ao editar XLSX (remover linha): {e}")
        return None


def editar_xlsx_atualizar_celula(xlsx_bytes: bytes, linha: int, coluna: int, valor, planilha: str = None) -> Optional[bytes]:
    """Atualiza o valor de uma célula específica
    
    Args:
        xlsx_bytes: bytes do arquivo XLSX original
        linha: número da linha (1-indexed)
        coluna: número da coluna (1-indexed) ou letra (A, B, C...)
        valor: novo valor da célula
        planilha: nome da planilha (usa a primeira se não especificado)
    
    Returns:
        bytes do XLSX modificado ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = load_workbook(io.BytesIO(xlsx_bytes))
        
        # Seleciona a planilha
        if planilha and planilha in wb.sheetnames:
            ws = wb[planilha]
        else:
            ws = wb.active
        
        # Converte coluna letra para número se necessário
        if isinstance(coluna, str):
            from openpyxl.utils import column_index_from_string
            coluna = column_index_from_string(coluna)
        
        # Atualiza a célula
        ws.cell(row=linha, column=coluna, value=valor)
        
        # Salva em bytes
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Erro ao editar XLSX (atualizar célula): {e}")
        return None


def criar_xlsx_entregadores(dados: dict, custo_semana: float = 1.0, custo_fds: float = 10.0, 
                           bonus_horario: float = 10.0, custo_entrega: float = 12.0) -> Optional[bytes]:
    """Cria planilha Excel formatada para controle de entregadores
    
    Args:
        dados: Dicionário com estrutura:
            {
                "periodo": "Semana 10/02 a 16/02",
                "dias": [
                    {"dia": "segunda", "entregadores": 3, "chegaram_horario": 0, "entregas": 20},
                    ...
                ]
            }
        custo_semana: Custo por entregador seg-qui (padrão: 1.0)
        custo_fds: Custo por entregador sex-dom (padrão: 10.0)
        bonus_horario: Bônus por chegar até 18:10 no FDS (padrão: 10.0)
        custo_entrega: Custo por entrega (padrão: 12.0)
    
    Returns:
        bytes do XLSX ou None se falhar
    """
    if not HAS_XLSX:
        logger.error("openpyxl não instalado")
        return None
    
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Entregadores"
        
        # Estilos
        title_font = Font(bold=True, size=14, color="FFFFFF")
        title_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        title_align = Alignment(horizontal="center", vertical="center")
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        data_align = Alignment(horizontal="center", vertical="center")
        currency_align = Alignment(horizontal="right", vertical="center")
        
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        thick_border = Border(
            left=Side(style='medium'),
            right=Side(style='medium'),
            top=Side(style='medium'),
            bottom=Side(style='medium')
        )
        
        # Linha 1: Título
        ws.merge_cells('A1:H1')
        title_cell = ws['A1']
        title_cell.value = f"📊 CONTROLE DE ENTREGADORES - {dados.get('periodo', 'Semana')}"
        title_cell.font = title_font
        title_cell.fill = title_fill
        title_cell.alignment = title_align
        title_cell.border = thick_border
        ws.row_dimensions[1].height = 30
        
        # Linha 2: Vazia (espaçamento)
        ws.row_dimensions[2].height = 5
        
        # Linha 3: Cabeçalhos
        headers = [
            "Dia",
            "Entregadores",
            "Chegaram\n18:10",
            "Entregas",
            "Custo\nEntregadores",
            "Bônus\nHorário",
            "Custo\nEntregas",
            "TOTAL"
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border
        
        ws.row_dimensions[3].height = 35
        
        # Dados dos dias
        dias_data = dados.get('dias', [])
        row_num = 4
        
        # Mapeamento de dias para identificar fim de semana
        dias_fds = {'sexta', 'sabado', 'sábado', 'domingo'}
        
        alt_fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
        fds_fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
        
        for idx, dia_info in enumerate(dias_data):
            dia = dia_info.get('dia', '').lower()
            entregadores = dia_info.get('entregadores', 0)
            chegaram_horario = dia_info.get('chegaram_horario', 0)
            entregas = dia_info.get('entregas', 0)
            
            # Determina se é fim de semana
            is_fds = any(d in dia for d in dias_fds)
            
            # Coluna A: Dia
            cell = ws.cell(row=row_num, column=1, value=dia.capitalize())
            cell.alignment = data_align
            cell.border = thin_border
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            # Coluna B: Entregadores
            cell = ws.cell(row=row_num, column=2, value=entregadores)
            cell.alignment = data_align
            cell.border = thin_border
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            # Coluna C: Chegaram 18:10
            cell = ws.cell(row=row_num, column=3, value=chegaram_horario if is_fds else '-')
            cell.alignment = data_align
            cell.border = thin_border
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            # Coluna D: Entregas
            cell = ws.cell(row=row_num, column=4, value=entregas)
            cell.alignment = data_align
            cell.border = thin_border
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            # Coluna E: Custo Entregadores (fórmula)
            if is_fds:
                formula = f"=B{row_num}*{custo_fds}"
            else:
                formula = f"=B{row_num}*{custo_semana}"
            
            cell = ws.cell(row=row_num, column=5, value=formula)
            cell.number_format = 'R$ #,##0.00'
            cell.alignment = currency_align
            cell.border = thin_border
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            # Coluna F: Bônus Horário (fórmula)
            if is_fds:
                formula = f"=C{row_num}*{bonus_horario}"
            else:
                formula = "=0"
            
            cell = ws.cell(row=row_num, column=6, value=formula)
            cell.number_format = 'R$ #,##0.00'
            cell.alignment = currency_align
            cell.border = thin_border
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            # Coluna G: Custo Entregas (fórmula)
            formula = f"=D{row_num}*{custo_entrega}"
            cell = ws.cell(row=row_num, column=7, value=formula)
            cell.number_format = 'R$ #,##0.00'
            cell.alignment = currency_align
            cell.border = thin_border
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            # Coluna H: TOTAL (fórmula)
            formula = f"=E{row_num}+F{row_num}+G{row_num}"
            cell = ws.cell(row=row_num, column=8, value=formula)
            cell.number_format = 'R$ #,##0.00'
            cell.alignment = currency_align
            cell.border = thin_border
            cell.font = Font(bold=True)
            if is_fds:
                cell.fill = fds_fill
            elif idx % 2 == 1:
                cell.fill = alt_fill
            
            row_num += 1
        
        # Linha de TOTAL
        total_row = row_num
        total_fill = PatternFill(start_color="27AE60", end_color="27AE60", fill_type="solid")
        total_font = Font(bold=True, color="FFFFFF", size=12)
        
        # Coluna A: "TOTAL"
        cell = ws.cell(row=total_row, column=1, value="TOTAL")
        cell.font = total_font
        cell.fill = total_fill
        cell.alignment = data_align
        cell.border = thick_border
        
        # Colunas B, C, D: Somas
        for col in [2, 3, 4]:
            formula = f"=SUM({get_column_letter(col)}4:{get_column_letter(col)}{total_row-1})"
            cell = ws.cell(row=total_row, column=col, value=formula)
            cell.font = total_font
            cell.fill = total_fill
            cell.alignment = data_align
            cell.border = thick_border
        
        # Colunas E, F, G, H: Somas com formato moeda
        for col in [5, 6, 7, 8]:
            formula = f"=SUM({get_column_letter(col)}4:{get_column_letter(col)}{total_row-1})"
            cell = ws.cell(row=total_row, column=col, value=formula)
            cell.number_format = 'R$ #,##0.00'
            cell.font = total_font
            cell.fill = total_fill
            cell.alignment = currency_align
            cell.border = thick_border
        
        ws.row_dimensions[total_row].height = 25
        
        # Ajusta largura das colunas
        column_widths = {
            'A': 12,  # Dia
            'B': 12,  # Entregadores
            'C': 12,  # Chegaram 18:10
            'D': 10,  # Entregas
            'E': 15,  # Custo Entregadores
            'F': 15,  # Bônus Horário
            'G': 15,  # Custo Entregas
            'H': 18   # TOTAL
        }
        
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width
        
        # Salva em bytes
        buffer = io.BytesIO()
        wb.save(buffer)
        
        result = buffer.getvalue()
        buffer.close()
        
        logger.info(f"XLSX de entregadores criado: {len(result)} bytes")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao criar XLSX de entregadores: {e}")
        return None
