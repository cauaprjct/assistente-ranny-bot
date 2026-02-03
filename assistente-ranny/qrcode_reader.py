"""
📱 Leitor de QR Code PIX - Assistente Ranny V3

Funcionalidades:
- Detectar QR codes em imagens
- Decodificar QR codes PIX
- Extrair informações do PIX (chave, valor, beneficiário)
- Formatar dados para apresentação
"""

import logging
import re
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Importa bibliotecas de QR Code
try:
    from pyzbar import pyzbar
    from pyzbar.pyzbar import ZBarSymbol
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False
    logger.warning("pyzbar não instalado - leitura de QR code desabilitada")

try:
    import PIL.Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("Pillow não instalado - processamento de imagem desabilitado")


def detectar_qrcode(image_data: bytes) -> Optional[str]:
    """Detecta e decodifica QR code de uma imagem
    
    Args:
        image_data: bytes da imagem
    
    Returns:
        String do QR code decodificado ou None se não encontrar
    """
    if not HAS_PYZBAR or not HAS_PIL:
        logger.error("Bibliotecas necessárias não instaladas (pyzbar, Pillow)")
        return None
    
    try:
        # Abre a imagem
        image = PIL.Image.open(io.BytesIO(image_data))
        
        # Converte para RGB se necessário
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Detecta QR codes
        qrcodes = pyzbar.decode(image, symbols=[ZBarSymbol.QRCODE])
        
        if not qrcodes:
            logger.info("Nenhum QR code encontrado na imagem")
            return None
        
        # Pega o primeiro QR code encontrado
        qrcode = qrcodes[0]
        qrcode_data = qrcode.data.decode('utf-8')
        
        logger.info(f"QR code detectado: {len(qrcode_data)} caracteres")
        return qrcode_data
        
    except Exception as e:
        logger.error(f"Erro ao detectar QR code: {e}")
        return None


def decodificar_pix(qrcode_data: str) -> Optional[Dict]:
    """Decodifica dados de um QR code PIX (BR Code)
    
    O PIX usa o padrão EMV QR Code (BR Code) que tem formato específico.
    
    Args:
        qrcode_data: String do QR code
    
    Returns:
        Dict com dados do PIX ou None se não for PIX válido
    """
    if not qrcode_data:
        return None
    
    try:
        # Verifica se é um PIX válido (começa com "00020126" ou "00020101")
        if not (qrcode_data.startswith('00020126') or qrcode_data.startswith('00020101')):
            logger.info("QR code não é um PIX válido")
            return None
        
        resultado = {
            'tipo': 'pix',
            'qrcode_completo': qrcode_data,
            'tamanho': len(qrcode_data)
        }
        
        # Extrai informações do PIX usando regex
        # O formato PIX é: ID(2 dígitos) + Tamanho(2 dígitos) + Valor
        
        # Merchant Account Information (tag 26)
        # Contém a chave PIX
        match_chave = re.search(r'26(\d{2})0014br\.gov\.bcb\.pix01(\d{2})(.+?)(?=\d{2}\d{2}|$)', qrcode_data)
        if match_chave:
            tamanho_chave = int(match_chave.group(2))
            chave = match_chave.group(3)[:tamanho_chave]
            resultado['chave_pix'] = chave
            
            # Identifica tipo de chave
            if '@' in chave:
                resultado['tipo_chave'] = 'email'
            elif re.match(r'^\+?\d{10,}$', chave):
                resultado['tipo_chave'] = 'telefone'
            elif re.match(r'^\d{11}$', chave):
                resultado['tipo_chave'] = 'cpf'
            elif re.match(r'^\d{14}$', chave):
                resultado['tipo_chave'] = 'cnpj'
            elif re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', chave.lower()):
                resultado['tipo_chave'] = 'aleatoria'
            else:
                resultado['tipo_chave'] = 'desconhecida'
        
        # Merchant Name (tag 59)
        match_nome = re.search(r'59(\d{2})(.+?)(?=\d{2}\d{2}|$)', qrcode_data)
        if match_nome:
            tamanho_nome = int(match_nome.group(1))
            nome = match_nome.group(2)[:tamanho_nome]
            resultado['beneficiario'] = nome
        
        # Merchant City (tag 60)
        match_cidade = re.search(r'60(\d{2})(.+?)(?=\d{2}\d{2}|$)', qrcode_data)
        if match_cidade:
            tamanho_cidade = int(match_cidade.group(1))
            cidade = match_cidade.group(2)[:tamanho_cidade]
            resultado['cidade'] = cidade
        
        # Transaction Amount (tag 54) - Valor
        match_valor = re.search(r'54(\d{2})(.+?)(?=\d{2}\d{2}|$)', qrcode_data)
        if match_valor:
            tamanho_valor = int(match_valor.group(1))
            valor_str = match_valor.group(2)[:tamanho_valor]
            try:
                resultado['valor'] = float(valor_str)
            except ValueError:
                logger.warning(f"Valor inválido no PIX: {valor_str}")
        
        # Additional Data Field (tag 62) - Informações adicionais
        match_info = re.search(r'62(\d{2})(.+?)(?=\d{2}\d{2}|$)', qrcode_data)
        if match_info:
            tamanho_info = int(match_info.group(1))
            info_adicional = match_info.group(2)[:tamanho_info]
            
            # Dentro do campo 62, pode ter:
            # 05 = Reference Label (identificador da transação)
            match_ref = re.search(r'05(\d{2})(.+?)(?=\d{2}\d{2}|$)', info_adicional)
            if match_ref:
                tamanho_ref = int(match_ref.group(1))
                referencia = match_ref.group(2)[:tamanho_ref]
                resultado['referencia'] = referencia
        
        logger.info(f"PIX decodificado: {resultado.get('beneficiario', 'N/A')}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao decodificar PIX: {e}")
        return None


def formatar_pix_para_texto(dados_pix: Dict) -> str:
    """Formata dados do PIX para apresentação em texto
    
    Args:
        dados_pix: Dict com dados do PIX
    
    Returns:
        String formatada para apresentação
    """
    if not dados_pix:
        return "❌ Dados do PIX inválidos"
    
    linhas = []
    linhas.append("📱 **QR CODE PIX DETECTADO**")
    linhas.append("")
    
    # Beneficiário
    if 'beneficiario' in dados_pix:
        linhas.append(f"👤 **Beneficiário:** {dados_pix['beneficiario']}")
    
    # Chave PIX
    if 'chave_pix' in dados_pix:
        tipo_chave = dados_pix.get('tipo_chave', 'desconhecida')
        emoji_chave = {
            'email': '📧',
            'telefone': '📱',
            'cpf': '🆔',
            'cnpj': '🏢',
            'aleatoria': '🔑',
            'desconhecida': '❓'
        }.get(tipo_chave, '🔑')
        
        chave = dados_pix['chave_pix']
        # Mascara CPF/CNPJ para privacidade
        if tipo_chave == 'cpf' and len(chave) == 11:
            chave = f"{chave[:3]}.***.**{chave[-2:]}"
        elif tipo_chave == 'cnpj' and len(chave) == 14:
            chave = f"{chave[:2]}.***.***/****-{chave[-2:]}"
        
        linhas.append(f"{emoji_chave} **Chave PIX ({tipo_chave}):** {chave}")
    
    # Valor
    if 'valor' in dados_pix:
        valor = dados_pix['valor']
        linhas.append(f"💰 **Valor:** R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    else:
        linhas.append("💰 **Valor:** A definir no pagamento")
    
    # Cidade
    if 'cidade' in dados_pix:
        linhas.append(f"📍 **Cidade:** {dados_pix['cidade']}")
    
    # Referência
    if 'referencia' in dados_pix:
        linhas.append(f"🔖 **Referência:** {dados_pix['referencia']}")
    
    linhas.append("")
    linhas.append("ℹ️ **Informação Técnica:**")
    linhas.append(f"• Tamanho do QR Code: {dados_pix.get('tamanho', 0)} caracteres")
    
    # QR Code completo (truncado para não poluir)
    if 'qrcode_completo' in dados_pix:
        qr_truncado = dados_pix['qrcode_completo'][:50] + "..." if len(dados_pix['qrcode_completo']) > 50 else dados_pix['qrcode_completo']
        linhas.append(f"• Código: `{qr_truncado}`")
    
    linhas.append("")
    linhas.append("✅ **Este QR Code pode ser usado para pagamento via PIX**")
    
    return "\n".join(linhas)


def processar_imagem_com_qrcode(image_data: bytes) -> Optional[Dict]:
    """Processa uma imagem, detecta QR code e extrai dados do PIX
    
    Função principal que combina detecção e decodificação.
    
    Args:
        image_data: bytes da imagem
    
    Returns:
        Dict com dados processados ou None se não encontrar QR code
    """
    try:
        # Detecta QR code
        qrcode_data = detectar_qrcode(image_data)
        
        if not qrcode_data:
            return None
        
        # Tenta decodificar como PIX
        dados_pix = decodificar_pix(qrcode_data)
        
        if dados_pix:
            # É um PIX válido
            dados_pix['texto_formatado'] = formatar_pix_para_texto(dados_pix)
            return dados_pix
        else:
            # É um QR code mas não é PIX
            return {
                'tipo': 'qrcode_generico',
                'conteudo': qrcode_data,
                'tamanho': len(qrcode_data),
                'texto_formatado': f"📱 **QR CODE DETECTADO**\n\nConteúdo: {qrcode_data[:100]}{'...' if len(qrcode_data) > 100 else ''}"
            }
        
    except Exception as e:
        logger.error(f"Erro ao processar imagem com QR code: {e}")
        return None


def extrair_codigo_barras_de_texto(texto: str) -> Optional[str]:
    """Extrai código de barras de texto (47-48 dígitos)
    
    Args:
        texto: Texto contendo possível código de barras
    
    Returns:
        Código de barras ou None se não encontrar
    """
    try:
        # Remove espaços e caracteres especiais
        texto_limpo = re.sub(r'[^\d]', '', texto)
        
        # Procura sequências de 47 ou 48 dígitos
        match = re.search(r'\d{47,48}', texto_limpo)
        
        if match:
            codigo = match.group(0)
            logger.info(f"Código de barras encontrado: {len(codigo)} dígitos")
            return codigo
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao extrair código de barras: {e}")
        return None


def formatar_codigo_barras(codigo: str) -> str:
    """Formata código de barras para apresentação
    
    Args:
        codigo: Código de barras (47-48 dígitos)
    
    Returns:
        String formatada
    """
    if not codigo:
        return ""
    
    # Formata em blocos para facilitar leitura
    # Padrão comum: XXXXX.XXXXX XXXXX.XXXXXX XXXXX.XXXXXX X XXXXXXXXXXXXXXXX
    if len(codigo) == 47:
        return f"{codigo[:5]}.{codigo[5:10]} {codigo[10:15]}.{codigo[15:21]} {codigo[21:26]}.{codigo[26:32]} {codigo[32]} {codigo[33:]}"
    elif len(codigo) == 48:
        return f"{codigo[:11]} {codigo[11:12]} {codigo[12:23]} {codigo[23:24]} {codigo[24:]}"
    else:
        # Formato genérico: blocos de 5
        blocos = [codigo[i:i+5] for i in range(0, len(codigo), 5)]
        return " ".join(blocos)


# ============ FUNÇÃO DE TESTE ============

def testar_qrcode_reader():
    """Testa o leitor de QR code"""
    print("=" * 60)
    print("🧪 TESTE DO LEITOR DE QR CODE PIX")
    print("=" * 60)
    print()
    
    # Verifica bibliotecas
    print("1️⃣  Verificando bibliotecas...")
    if HAS_PYZBAR:
        print("   ✅ pyzbar instalado")
    else:
        print("   ❌ pyzbar NÃO instalado")
        print("   💡 Instale com: pip install pyzbar")
    
    if HAS_PIL:
        print("   ✅ Pillow instalado")
    else:
        print("   ❌ Pillow NÃO instalado")
    
    print()
    
    # Teste de decodificação PIX (exemplo)
    print("2️⃣  Testando decodificação PIX...")
    
    # PIX de exemplo (formato simplificado)
    pix_exemplo = "00020126580014br.gov.bcb.pix0136123e4567-e12b-12d1-a456-426655440000520400005303986540510.005802BR5913Fulano de Tal6008BRASILIA62070503***63041D3D"
    
    dados = decodificar_pix(pix_exemplo)
    if dados:
        print("   ✅ PIX decodificado com sucesso!")
        print(f"   Beneficiário: {dados.get('beneficiario', 'N/A')}")
        print(f"   Valor: R$ {dados.get('valor', 0):.2f}")
    else:
        print("   ⚠️  Não foi possível decodificar o PIX de exemplo")
    
    print()
    
    # Teste de formatação
    print("3️⃣  Testando formatação de código de barras...")
    codigo_teste = "34191234567890123456789012345678901234567"
    formatado = formatar_codigo_barras(codigo_teste)
    print(f"   Original: {codigo_teste}")
    print(f"   Formatado: {formatado}")
    
    print()
    print("=" * 60)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 60)


if __name__ == "__main__":
    testar_qrcode_reader()
