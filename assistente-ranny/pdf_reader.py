"""
📄 Leitor de PDFs - Extração local de dados

Sistema próprio de extração que economiza chamadas ao Gemini:
- PDFs com texto: extrai direto com pdfplumber
- PDFs escaneados: converte para imagem e usa Gemini Vision
- Fallback: regex para extrair valor, vencimento, beneficiário

Requirements: 2.3
"""

import re
import logging
from datetime import datetime
from typing import Optional, Tuple
from io import BytesIO

logger = logging.getLogger(__name__)

# Tenta importar bibliotecas de PDF
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    logger.warning("pdfplumber não instalado - extração de texto limitada")

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF não instalado - conversão PDF→imagem desabilitada")


def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, bool]:
    """Extrai texto de PDF
    
    Returns:
        Tuple[str, bool]: (texto extraído, True se tem texto suficiente)
    """
    if not HAS_PDFPLUMBER:
        return "", False
    
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text_parts = []
            for page in pdf.pages[:5]:  # Limita a 5 páginas
                text = page.extract_text() or ""
                text_parts.append(text)
            
            full_text = "\n".join(text_parts).strip()
            
            # Considera que tem texto suficiente se > 50 caracteres
            has_text = len(full_text) > 50
            return full_text, has_text
            
    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF: {e}")
        return "", False


def pdf_to_image(pdf_bytes: bytes, page_num: int = 0, dpi: int = 150) -> Optional[bytes]:
    """Converte página do PDF em imagem PNG
    
    Args:
        pdf_bytes: Bytes do PDF
        page_num: Número da página (0-indexed)
        dpi: Resolução da imagem
    
    Returns:
        Bytes da imagem PNG ou None se falhar
    """
    if not HAS_PYMUPDF:
        return None
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if page_num >= len(doc):
            page_num = 0
        
        page = doc[page_num]
        
        # Renderiza com zoom baseado no DPI
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Converte para PNG
        img_bytes = pix.tobytes("png")
        
        doc.close()
        return img_bytes
        
    except Exception as e:
        logger.error(f"Erro ao converter PDF para imagem: {e}")
        return None


def extract_boleto_data(text: str) -> dict:
    """Extrai dados de boleto usando regex
    
    Sistema local que não depende de IA.
    Extrai: valor, vencimento, beneficiário, tipo de conta.
    """
    result = {}
    text_lower = text.lower()
    
    # === EXTRAI VALOR ===
    valor_patterns = [
        # Padrões específicos de boleto
        r'valor\s*(?:do\s*)?(?:documento|cobrado|total)[:\s]*R?\$?\s*([\d.,]+)',
        r'total\s*a\s*pagar[:\s]*R?\$?\s*([\d.,]+)',
        r'valor\s*cobrado[:\s]*R?\$?\s*([\d.,]+)',
        # Padrão genérico R$ XXX,XX
        r'R\$\s*([\d]{1,3}(?:\.[\d]{3})*,[\d]{2})',
        r'R\$\s*([\d]+,[\d]{2})',
        # Valor sem R$
        r'valor[:\s]+([\d]{1,3}(?:\.[\d]{3})*,[\d]{2})',
    ]
    
    for pattern in valor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            valor_str = match.group(1)
            # Normaliza: remove pontos de milhar, troca vírgula por ponto
            valor_str = valor_str.replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
                if 0.01 <= valor <= 1000000:  # Sanity check
                    result['valor'] = valor
                    break
            except ValueError:
                continue
    
    # === EXTRAI VENCIMENTO ===
    venc_patterns = [
        r'vencimento[:\s]*(\d{2}[/.-]\d{2}[/.-]\d{4})',
        r'vence(?:m)?\s*(?:em)?[:\s]*(\d{2}[/.-]\d{2}[/.-]\d{4})',
        r'data\s*(?:de\s*)?vencimento[:\s]*(\d{2}[/.-]\d{2}[/.-]\d{4})',
        r'pagar\s*até[:\s]*(\d{2}[/.-]\d{2}[/.-]\d{4})',
        r'válido\s*até[:\s]*(\d{2}[/.-]\d{2}[/.-]\d{4})',
    ]
    
    for pattern in venc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data_str = match.group(1)
            data_str = re.sub(r'[/.-]', '/', data_str)
            try:
                dt = datetime.strptime(data_str, '%d/%m/%Y')
                # Só aceita datas futuras ou até 1 ano no passado
                if dt.year >= datetime.now().year - 1:
                    result['vencimento'] = dt.strftime('%Y-%m-%d')
                    break
            except ValueError:
                continue
    
    # === EXTRAI BENEFICIÁRIO ===
    benef_patterns = [
        r'benefici[áa]rio[:\s]*([^\n\r]{5,60})',
        r'cedente[:\s]*([^\n\r]{5,60})',
        r'favorecido[:\s]*([^\n\r]{5,60})',
        r'empresa[:\s]*([^\n\r]{5,60})',
        r'razão\s*social[:\s]*([^\n\r]{5,60})',
    ]
    
    for pattern in benef_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            beneficiario = match.group(1).strip()
            # Remove caracteres indesejados
            beneficiario = re.sub(r'[\d]{2}\.[\d]{3}\.[\d]{3}', '', beneficiario)  # Remove CNPJ
            beneficiario = beneficiario.strip(' -:')
            if len(beneficiario) >= 3:
                result['beneficiario'] = beneficiario[:60]
                break
    
    # === DETECTA TIPO DE CONTA ===
    # Ordem importa: tipos mais específicos primeiro
    tipo_keywords = {
        'gas': ['gás', 'gas', 'naturgy', 'comgas', 'ceg', 'gás natural'],
        'luz': ['luz', 'energia', 'elétrica', 'eletrica', 'light', 'enel', 'cemig', 'cpfl', 'celpe', 'coelba', 'energisa'],
        'agua': ['água', 'agua', 'cedae', 'sabesp', 'saneamento', 'copasa', 'embasa', 'cagece'],
        'internet': ['internet', 'fibra', 'banda larga', 'wifi', 'wi-fi'],
        'telefone': ['telefone', 'celular', 'móvel', 'movel', 'linha telefônica', 'linha telefonica'],
        'aluguel': ['aluguel', 'locação', 'locacao', 'inquilino'],
        'condominio': ['condomínio', 'condominio', 'taxa condominial'],
        'cartao': ['cartão', 'cartao', 'fatura', 'crédito', 'credito'],
        'boleto': ['boleto', 'cobrança', 'cobranca'],
    }
    
    for tipo, keywords in tipo_keywords.items():
        if any(kw in text_lower for kw in keywords):
            result['tipo_conta'] = tipo
            break
    
    # Se não detectou tipo mas tem valor/vencimento, é boleto genérico
    if 'tipo_conta' not in result and ('valor' in result or 'vencimento' in result):
        result['tipo_conta'] = 'outro'
    
    # === EXTRAI CÓDIGO DE BARRAS / LINHA DIGITÁVEL ===
    # Linha digitável de boleto bancário: 47 dígitos (com ou sem formatação)
    # Formato: XXXXX.XXXXX XXXXX.XXXXXX XXXXX.XXXXXX X XXXXXXXXXXXXXX
    
    linha_digitavel = None
    
    # Padrão 1: Linha digitável formatada com pontos e espaços
    pattern_formatado = r'(\d{5})[.\s]?(\d{5})[.\s]+(\d{5})[.\s]?(\d{6})[.\s]+(\d{5})[.\s]?(\d{6})[.\s]+(\d)[.\s]+(\d{14})'
    match = re.search(pattern_formatado, text)
    if match:
        # Junta todos os grupos para formar a linha digitável completa
        linha_digitavel = ''.join(match.groups())
    
    # Padrão 2: Sequência de 47-48 dígitos (sem formatação)
    if not linha_digitavel:
        pattern_numerico = r'(?<!\d)(\d{47,48})(?!\d)'
        match = re.search(pattern_numerico, text)
        if match:
            linha_digitavel = match.group(1)
    
    # Padrão 3: Linha digitável com "Linha Digitável:" ou similar
    if not linha_digitavel:
        pattern_label = r'linha\s*digit[áa]vel[:\s]*([0-9.\s]{47,70})'
        match = re.search(pattern_label, text, re.IGNORECASE)
        if match:
            # Remove pontos e espaços
            linha_digitavel = re.sub(r'[.\s]', '', match.group(1))
    
    # Padrão 4: Código de barras de concessionárias (contas de luz, água, etc) - 48 dígitos
    if not linha_digitavel:
        pattern_concess = r'(\d{11,12})[.\s-]?(\d{11,12})[.\s-]?(\d{11,12})[.\s-]?(\d{11,12})'
        match = re.search(pattern_concess, text)
        if match:
            linha_digitavel = ''.join(match.groups())
    
    if linha_digitavel and len(linha_digitavel) >= 44:
        result['codigo_barras'] = linha_digitavel
        # Formata para exibição (mais legível)
        if len(linha_digitavel) == 47:
            # Boleto bancário: XXXXX.XXXXX XXXXX.XXXXXX XXXXX.XXXXXX X XXXXXXXXXXXXXX
            result['codigo_barras_formatado'] = f"{linha_digitavel[:5]}.{linha_digitavel[5:10]} {linha_digitavel[10:15]}.{linha_digitavel[15:21]} {linha_digitavel[21:26]}.{linha_digitavel[26:32]} {linha_digitavel[32]} {linha_digitavel[33:]}"
        elif len(linha_digitavel) == 48:
            # Concessionária: XXXXXXXXXXX-X XXXXXXXXXXX-X XXXXXXXXXXX-X XXXXXXXXXXX-X
            result['codigo_barras_formatado'] = f"{linha_digitavel[:11]}-{linha_digitavel[11]} {linha_digitavel[12:23]}-{linha_digitavel[23]} {linha_digitavel[24:35]}-{linha_digitavel[35]} {linha_digitavel[36:47]}-{linha_digitavel[47]}"
        else:
            result['codigo_barras_formatado'] = linha_digitavel
    
    # Marca tipo de documento
    if result:
        result['tipo_documento'] = 'boleto'
    
    return result


def extract_comprovante_data(text: str) -> dict:
    """Extrai dados de comprovante de pagamento"""
    result = {}
    text_lower = text.lower()
    
    # Detecta se é comprovante
    comprovante_keywords = ['comprovante', 'transferência', 'transferencia', 'pix', 'pagamento realizado', 'operação realizada']
    if not any(kw in text_lower for kw in comprovante_keywords):
        return {}
    
    result['tipo_documento'] = 'comprovante'
    
    # Extrai valor
    valor_patterns = [
        r'valor[:\s]*R?\$?\s*([\d.,]+)',
        r'R\$\s*([\d]{1,3}(?:\.[\d]{3})*,[\d]{2})',
    ]
    
    for pattern in valor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                result['valor'] = float(valor_str)
                break
            except ValueError:
                continue
    
    # Extrai data
    data_patterns = [
        r'data[:\s]*(\d{2}[/.-]\d{2}[/.-]\d{4})',
        r'realizado\s*em[:\s]*(\d{2}[/.-]\d{2}[/.-]\d{4})',
    ]
    
    for pattern in data_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data_str = re.sub(r'[/.-]', '/', match.group(1))
            try:
                dt = datetime.strptime(data_str, '%d/%m/%Y')
                result['data_pagamento'] = dt.strftime('%Y-%m-%d')
                break
            except ValueError:
                continue
    
    # Detecta tipo de pagamento
    if 'pix' in text_lower:
        result['tipo_pagamento'] = 'pix'
    elif 'ted' in text_lower or 'transferência' in text_lower:
        result['tipo_pagamento'] = 'transferencia'
    elif 'boleto' in text_lower:
        result['tipo_pagamento'] = 'boleto'
    
    # Extrai destinatário
    dest_patterns = [
        r'(?:para|destinat[áa]rio|favorecido)[:\s]*([^\n\r]{5,60})',
        r'nome[:\s]*([^\n\r]{5,60})',
    ]
    
    for pattern in dest_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['destinatario'] = match.group(1).strip()[:60]
            break
    
    return result


async def analyze_pdf(pdf_bytes: bytes, use_vision_callback=None) -> dict:
    """Analisa PDF e extrai dados
    
    Estratégia:
    1. Tenta extrair texto do PDF
    2. Se tem texto suficiente, usa regex local (economiza Gemini)
    3. Se não tem texto (PDF escaneado), converte para imagem e usa callback
    
    Args:
        pdf_bytes: Bytes do arquivo PDF
        use_vision_callback: Função async para analisar imagem com Gemini Vision
                            Assinatura: async def callback(image_bytes: bytes) -> dict
    
    Returns:
        dict com dados extraídos
    """
    # 1. Tenta extrair texto
    text, has_text = extract_text_from_pdf(pdf_bytes)
    
    if has_text:
        logger.info("📄 PDF com texto - usando extração local")
        
        # Tenta extrair como boleto
        result = extract_boleto_data(text)
        
        # Se não é boleto, tenta como comprovante
        if not result:
            result = extract_comprovante_data(text)
        
        # Adiciona texto bruto para classificação
        if result:
            result['texto_extraido'] = text[:500]
            result['metodo'] = 'local'
            return result
        
        # Se não conseguiu extrair dados estruturados, retorna texto
        return {
            'tipo_documento': 'outro',
            'descricao': text[:200],
            'texto_extraido': text[:500],
            'metodo': 'local'
        }
    
    # 2. PDF sem texto (escaneado) - converte para imagem
    logger.info("📄 PDF escaneado - convertendo para imagem")
    
    image_bytes = pdf_to_image(pdf_bytes)
    
    if image_bytes and use_vision_callback:
        try:
            result = await use_vision_callback(image_bytes)
            result['metodo'] = 'vision'
            return result
        except Exception as e:
            logger.error(f"Erro no Gemini Vision: {e}")
            # Fallback: retorna info básica
            return {
                'tipo_documento': 'outro',
                'descricao': 'PDF escaneado - não foi possível extrair dados',
                'error': str(e),
                'metodo': 'fallback'
            }
    
    # 3. Não conseguiu processar
    return {
        'tipo_documento': 'outro',
        'descricao': 'PDF não processável',
        'metodo': 'fallback'
    }


def is_pdf(file_bytes: bytes) -> bool:
    """Verifica se o arquivo é um PDF pelo magic number"""
    return file_bytes[:4] == b'%PDF'


def get_pdf_page_count(pdf_bytes: bytes) -> int:
    """Retorna número de páginas do PDF"""
    if not HAS_PDFPLUMBER:
        return 0
    
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            return len(pdf.pages)
    except:
        return 0
