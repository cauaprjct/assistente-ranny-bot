"""
Integração com Gemini AI
"""
import google.generativeai as genai
import json
from datetime import datetime
from config import GEMINI_API_KEY, SYSTEM_PROMPT
import database_adapter as db
import logging
import pdf_reader

logger = logging.getLogger(__name__)

# Configura Gemini com a chave correta
genai.configure(api_key=GEMINI_API_KEY)

# Modelo Gemini 2.5 Flash (mais recente e eficiente)
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={
        'temperature': 0.7,
        'max_output_tokens': 2000,  # Respostas completas (aumentado de 500)
    }
)

# Histórico de conversa por usuário
conversation_history = {}

def get_context() -> str:
    """Monta contexto atual para a IA"""
    context_parts = []
    
    # Vencimentos próximos
    vencimentos = db.get_vencimentos_proximos(7)
    if vencimentos:
        context_parts.append("VENCIMENTOS PRÓXIMOS:")
        for v in vencimentos[:5]:
            context_parts.append(f"- {v['descricao']}: R$ {v['valor']:.2f} (vence em {v['dias_restantes']} dias)")
    
    # Último fechamento
    fechamentos = db.get_fechamentos(7)
    if fechamentos:
        ultimo = fechamentos[0]
        context_parts.append(f"\nÚLTIMO FECHAMENTO: R$ {ultimo['valor']:.2f} em {ultimo['data']}")
    
    # Funcionários ativos
    funcionarios = db.get_funcionarios()
    if funcionarios:
        context_parts.append(f"\nFUNCIONÁRIOS ATIVOS: {len(funcionarios)}")
        for f in funcionarios[:5]:
            context_parts.append(f"- {f['nome']} ({f['funcao']})")
    
    # Audiências próximas
    audiencias = db.get_audiencias_proximas(30)
    if audiencias:
        context_parts.append("\nAUDIÊNCIAS PRÓXIMAS:")
        for a in audiencias[:3]:
            context_parts.append(f"- {a['data']}: Processo {a['processo']}")
    
    # Problemas TI abertos
    problemas = db.get_problemas_ti('aberto')
    if problemas:
        context_parts.append(f"\nPROBLEMAS TI ABERTOS: {len(problemas)}")
    
    return "\n".join(context_parts) if context_parts else "Nenhum dado cadastrado ainda."


async def get_response(user_id: int, message: str, image_data: bytes = None) -> str:
    """Obtém resposta da IA"""
    
    # Inicializa histórico
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # Adiciona mensagem ao histórico
    conversation_history[user_id].append(f"Ranny: {message}")
    
    # Mantém últimas 10 mensagens
    if len(conversation_history[user_id]) > 10:
        conversation_history[user_id] = conversation_history[user_id][-10:]
    
    # Monta prompt
    context = get_context()
    system = SYSTEM_PROMPT.format(
        context=context,
        date=datetime.now().strftime("%d/%m/%Y %H:%M")
    )
    history = "\n".join(conversation_history[user_id])
    full_prompt = f"{system}\n\nHISTÓRICO DA CONVERSA:\n{history}\n\nAssistente:"
    
    try:
        if image_data:
            # Processa imagem junto com texto
            import PIL.Image
            import io
            image = PIL.Image.open(io.BytesIO(image_data))
            response = model.generate_content([full_prompt, image])
        else:
            response = model.generate_content(full_prompt)
        
        ai_response = response.text.strip()
        
        # Adiciona resposta ao histórico
        conversation_history[user_id].append(f"Assistente: {ai_response}")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Erro Gemini: {e}")
        return get_fallback_response(message)

def get_fallback_response(message: str) -> str:
    """Resposta de fallback quando IA falha"""
    msg_lower = message.lower()
    
    if any(word in msg_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
        return "Oi! Tô aqui pra te ajudar 😊 O que você precisa?"
    elif any(word in msg_lower for word in ['tudo bem', 'como vai', 'beleza']):
        return "Tudo ótimo! E você? Em que posso ajudar?"
    elif any(word in msg_lower for word in ['obrigad', 'valeu', 'thanks']):
        return "Por nada! Qualquer coisa, é só chamar 😊"
    elif 'fechamento' in msg_lower:
        return "Me fala o valor do fechamento de hoje que eu anoto! 📊"
    elif 'funcionario' in msg_lower or 'funcionária' in msg_lower:
        return "Quer cadastrar um funcionário novo ou ver informações de alguém? 👥"
    elif 'vencimento' in msg_lower or 'conta' in msg_lower:
        return "Me manda o boleto ou comprovante que eu guardo pra você! 💰"
    else:
        return "Oi! Estou com um probleminha técnico, mas já já volta ao normal. Me conta o que você precisa! 📝"


async def analyze_image(image_data: bytes, context: str = "") -> dict:
    """Analisa imagem com Gemini Vision
    
    Extrai dados estruturados de boletos, comprovantes e documentos.
    Para boletos, extrai: valor, vencimento, beneficiário, tipo.
    
    NOVO: Detecta e decodifica QR codes PIX automaticamente!
    
    Se Gemini falhar (limite, erro), usa fallback local.
    
    Requirements: 2.3
    """
    try:
        import PIL.Image
        import io
        import json
        import re
        
        # NOVO: Tenta detectar QR code PIX primeiro
        try:
            from qrcode_reader import processar_imagem_com_qrcode
            dados_qr = processar_imagem_com_qrcode(image_data)
            
            if dados_qr and dados_qr.get('tipo') == 'pix':
                logger.info("✅ QR Code PIX detectado e decodificado!")
                # Retorna dados do PIX com formato compatível
                return {
                    'tipo_documento': 'boleto',
                    'valor': dados_qr.get('valor'),
                    'beneficiario': dados_qr.get('beneficiario'),
                    'chave_pix': dados_qr.get('chave_pix'),
                    'tipo_chave': dados_qr.get('tipo_chave'),
                    'qrcode_pix': dados_qr.get('qrcode_completo'),
                    'cidade': dados_qr.get('cidade'),
                    'referencia': dados_qr.get('referencia'),
                    'descricao': f"PIX - {dados_qr.get('beneficiario', 'Pagamento')}",
                    'texto_formatado': dados_qr.get('texto_formatado'),
                    'metodo': 'qrcode_pix'
                }
        except ImportError:
            logger.debug("qrcode_reader não disponível, continuando com Gemini Vision")
        except Exception as e:
            logger.debug(f"Erro ao tentar ler QR code: {e}, continuando com Gemini Vision")
        
        image = PIL.Image.open(io.BytesIO(image_data))
        
        prompt = """Analise esta imagem e extraia as informações relevantes.

IMPORTANTE: Responda APENAS com JSON válido, sem texto adicional.

Se for um BOLETO ou CONTA, extraia OBRIGATORIAMENTE:
{
    "tipo_documento": "boleto",
    "valor": 123.45,
    "vencimento": "2025-01-20",
    "beneficiario": "Nome da Empresa",
    "tipo_conta": "luz|agua|internet|telefone|gas|aluguel|condominio|cartao|outro",
    "codigo_barras": "se visível",
    "descricao": "descrição breve do documento"
}

Se for um COMPROVANTE DE PAGAMENTO, extraia:
{
    "tipo_documento": "comprovante",
    "valor": 123.45,
    "data_pagamento": "2025-01-15",
    "destinatario": "Nome do destinatário",
    "tipo_pagamento": "pix|transferencia|boleto|debito|credito",
    "descricao": "descrição breve"
}

Se for um DOCUMENTO DE FUNCIONÁRIO, extraia:
{
    "tipo_documento": "funcionario",
    "nome_funcionario": "Nome",
    "tipo": "contrato|advertencia|aso|ferias|outro",
    "descricao": "descrição breve"
}

Se for OUTRO tipo de documento:
{
    "tipo_documento": "outro",
    "descricao": "descrição do que é o documento"
}

REGRAS:
- Valor SEMPRE como número decimal (ex: 150.00, não "R$ 150,00")
- Datas SEMPRE no formato YYYY-MM-DD
- Se não conseguir extrair algum campo, omita-o do JSON
- Responda APENAS o JSON, nada mais"""

        response = model.generate_content([prompt, image])
        
        # Limpa a resposta e tenta parsear como JSON
        response_text = response.text.strip()
        
        # Remove possíveis marcadores de código
        if response_text.startswith('```'):
            response_text = re.sub(r'^```(?:json)?\n?', '', response_text)
            response_text = re.sub(r'\n?```$', '', response_text)
        
        try:
            result = json.loads(response_text)
            
            # Normaliza o resultado para garantir campos esperados
            result = normalize_boleto_data(result)
            result['metodo'] = 'vision'
            
            return result
        except json.JSONDecodeError:
            # Tenta extrair dados manualmente do texto
            result = extract_boleto_from_text(response_text)
            result['metodo'] = 'vision_fallback'
            return result
            
    except Exception as e:
        logger.error(f"Erro Gemini Vision: {e}")
        # Fallback: retorna erro para tratamento externo
        return {
            'error': str(e),
            'tipo_documento': 'outro',
            'descricao': 'Não foi possível analisar a imagem',
            'metodo': 'fallback'
        }


async def analyze_file(file_data: bytes, file_name: str = "", context: str = "") -> dict:
    """Analisa arquivo (PDF ou imagem) e extrai dados
    
    Estratégia inteligente:
    1. Se é PDF com texto → extração local (economiza Gemini)
    2. Se é PDF escaneado → converte para imagem + Gemini Vision
    3. Se é imagem → Gemini Vision
    4. Se Gemini falhar → fallback local
    
    Args:
        file_data: Bytes do arquivo
        file_name: Nome do arquivo (para detectar tipo)
        context: Contexto adicional (legenda)
    
    Returns:
        dict com dados extraídos e campo 'metodo' indicando como foi processado
    """
    # Detecta se é PDF
    is_pdf = pdf_reader.is_pdf(file_data) or file_name.lower().endswith('.pdf')
    
    if is_pdf:
        logger.info(f"📄 Processando PDF: {file_name}")
        
        # Callback para usar Gemini Vision quando necessário
        async def vision_callback(image_bytes: bytes) -> dict:
            return await analyze_image(image_bytes, context)
        
        result = await pdf_reader.analyze_pdf(file_data, vision_callback)
        return result
    
    # É imagem - usa Gemini Vision
    logger.info(f"🖼️ Processando imagem: {file_name}")
    return await analyze_image(file_data, context)


def normalize_boleto_data(data: dict) -> dict:
    """Normaliza dados extraídos de boleto
    
    Garante que valor seja float e datas estejam no formato correto.
    """
    import re
    from datetime import datetime
    
    result = data.copy()
    
    # Normaliza valor
    if 'valor' in result:
        valor = result['valor']
        if isinstance(valor, str):
            # Remove R$, pontos de milhar, e converte vírgula para ponto
            valor = re.sub(r'[R$\s]', '', valor)
            valor = valor.replace('.', '').replace(',', '.')
            try:
                result['valor'] = float(valor)
            except ValueError:
                del result['valor']
        elif isinstance(valor, (int, float)):
            result['valor'] = float(valor)
    
    # Normaliza vencimento
    if 'vencimento' in result:
        venc = result['vencimento']
        if isinstance(venc, str):
            # Tenta diferentes formatos de data
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']
            for fmt in formatos:
                try:
                    dt = datetime.strptime(venc, fmt)
                    result['vencimento'] = dt.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
    
    # Normaliza data_pagamento
    if 'data_pagamento' in result:
        data_pag = result['data_pagamento']
        if isinstance(data_pag, str):
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']
            for fmt in formatos:
                try:
                    dt = datetime.strptime(data_pag, fmt)
                    result['data_pagamento'] = dt.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
    
    return result


def extract_boleto_from_text(text: str) -> dict:
    """Extrai dados de boleto de texto não-estruturado
    
    Fallback quando o JSON não é parseável.
    """
    import re
    from datetime import datetime
    
    result = {'raw_text': text}
    
    # Tenta extrair valor (R$ XXX,XX ou XXX.XX)
    valor_patterns = [
        r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2}))',  # R$ 1.234,56
        r'R\$\s*(\d+(?:,\d{2}))',                    # R$ 123,45
        r'valor[:\s]+R?\$?\s*(\d+(?:[.,]\d{2})?)',   # valor: 123.45
    ]
    
    for pattern in valor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            valor_str = match.group(1)
            valor_str = valor_str.replace('.', '').replace(',', '.')
            try:
                result['valor'] = float(valor_str)
                break
            except ValueError:
                continue
    
    # Tenta extrair data de vencimento
    venc_patterns = [
        r'vencimento[:\s]+(\d{2}[/.-]\d{2}[/.-]\d{4})',
        r'vence[:\s]+(\d{2}[/.-]\d{2}[/.-]\d{4})',
        r'(\d{2}[/.-]\d{2}[/.-]\d{4})',  # qualquer data
    ]
    
    for pattern in venc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data_str = match.group(1)
            # Normaliza separadores
            data_str = re.sub(r'[/.-]', '/', data_str)
            try:
                dt = datetime.strptime(data_str, '%d/%m/%Y')
                result['vencimento'] = dt.strftime('%Y-%m-%d')
                break
            except ValueError:
                continue
    
    # Tenta extrair beneficiário
    benef_patterns = [
        r'benefici[aá]rio[:\s]+([^\n]+)',
        r'empresa[:\s]+([^\n]+)',
        r'cedente[:\s]+([^\n]+)',
    ]
    
    for pattern in benef_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['beneficiario'] = match.group(1).strip()[:100]
            break
    
    # Detecta tipo de conta
    tipo_keywords = {
        'luz': ['luz', 'energia', 'light', 'enel', 'cemig', 'cpfl'],
        'agua': ['água', 'agua', 'cedae', 'sabesp', 'saneamento'],
        'internet': ['internet', 'fibra', 'banda larga', 'oi', 'vivo', 'claro', 'tim'],
        'telefone': ['telefone', 'celular', 'móvel'],
        'gas': ['gás', 'gas', 'naturgy', 'comgas'],
        'aluguel': ['aluguel', 'locação'],
        'condominio': ['condomínio', 'condominio'],
        'cartao': ['cartão', 'cartao', 'fatura', 'nubank', 'itau', 'bradesco'],
    }
    
    text_lower = text.lower()
    for tipo, keywords in tipo_keywords.items():
        if any(kw in text_lower for kw in keywords):
            result['tipo_conta'] = tipo
            break
    
    # Se encontrou valor ou vencimento, marca como boleto
    if 'valor' in result or 'vencimento' in result:
        result['tipo_documento'] = 'boleto'
    
    return result


async def classify_document(text: str) -> str:
    """Classifica tipo de documento baseado no texto"""
    prompt = f"""Classifique este documento em uma das categorias:
- financeiro (boletos, comprovantes, extratos, faturas)
- empresa (notas fiscais, DAS, DARF, guias)
- funcionarios (contratos, advertências, folhas, ASO)
- juridico (processos, intimações, petições)
- pessoal (documentos pessoais, CNH, RG)
- outros

Texto do documento:
{text[:500]}

Responda apenas com a categoria, sem explicação."""

    try:
        response = model.generate_content(prompt)
        categoria = response.text.strip().lower()
        
        categorias_validas = ['financeiro', 'empresa', 'funcionarios', 'juridico', 'pessoal', 'outros']
        if categoria in categorias_validas:
            return categoria
        return 'outros'
        
    except Exception as e:
        logger.error(f"Erro ao classificar: {e}")
        return 'outros'



async def extrair_dados_entregadores(texto: str) -> dict:
    """Extrai dados de entregadores do texto usando IA
    
    Args:
        texto: Descrição da semana de entregas
    
    Returns:
        Dicionário com estrutura:
        {
            "sucesso": True/False,
            "dados": {
                "periodo": "Semana 10/02 a 16/02",
                "dias": [
                    {"dia": "segunda", "entregadores": 3, "chegaram_horario": 0, "entregas": 20},
                    ...
                ]
            },
            "erro": "mensagem de erro" (se falhar)
        }
    """
    try:
        prompt = f"""Você é um assistente que extrai dados estruturados de texto.

CONTEXTO:
A Ranny descreve a semana de trabalho dos entregadores da pizzaria.

REGRAS DE NEGÓCIO:
- Segunda a quinta: R$ 1,00 por entregador escalado
- Sexta a domingo: R$ 10,00 por entregador escalado
- Sexta a domingo: R$ 10,00 adicional por cada entregador que chegar até 18:10h
- Sempre: R$ 12,00 por entrega realizada

IMPORTANTE:
- "chegaram_horario" deve ser 0 (zero) para segunda a quinta
- "chegaram_horario" só tem valor para sexta, sábado e domingo
- Se não mencionar quem chegou no horário, assume 0

TAREFA:
Extraia os dados do texto abaixo e retorne APENAS um JSON válido (sem markdown, sem explicações).

FORMATO DO JSON:
{{
  "periodo": "Semana DD/MM a DD/MM",
  "dias": [
    {{"dia": "segunda", "entregadores": 3, "chegaram_horario": 0, "entregas": 20}},
    {{"dia": "terca", "entregadores": 3, "chegaram_horario": 0, "entregas": 18}},
    {{"dia": "quarta", "entregadores": 3, "chegaram_horario": 0, "entregas": 22}},
    {{"dia": "quinta", "entregadores": 3, "chegaram_horario": 0, "entregas": 19}},
    {{"dia": "sexta", "entregadores": 4, "chegaram_horario": 3, "entregas": 30}},
    {{"dia": "sabado", "entregadores": 4, "chegaram_horario": 4, "entregas": 35}},
    {{"dia": "domingo", "entregadores": 4, "chegaram_horario": 3, "entregas": 28}}
  ]
}}

TEXTO DA RANNY:
{texto}

RETORNE APENAS O JSON (sem ```json, sem explicações):"""

        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2000,
            )
        )
        
        if not response or not response.text:
            return {
                "sucesso": False,
                "erro": "IA não retornou resposta"
            }
        
        # Limpa a resposta (remove markdown se houver)
        resposta_texto = response.text.strip()
        resposta_texto = resposta_texto.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        dados = json.loads(resposta_texto)
        
        # Valida estrutura básica
        if 'dias' not in dados or not isinstance(dados['dias'], list):
            return {
                "sucesso": False,
                "erro": "Estrutura JSON inválida"
            }
        
        # Valida cada dia
        for dia in dados['dias']:
            if not all(k in dia for k in ['dia', 'entregadores', 'chegaram_horario', 'entregas']):
                return {
                    "sucesso": False,
                    "erro": f"Dia {dia.get('dia', '?')} com dados incompletos"
                }
        
        # Gera período se não tiver
        if 'periodo' not in dados or not dados['periodo']:
            from datetime import datetime
            hoje = datetime.now()
            dados['periodo'] = f"Semana {hoje.strftime('%d/%m/%Y')}"
        
        logger.info(f"Dados de entregadores extraídos: {len(dados['dias'])} dias")
        
        return {
            "sucesso": True,
            "dados": dados
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao fazer parse do JSON: {e}")
        logger.error(f"Resposta da IA: {resposta_texto if 'resposta_texto' in locals() else 'N/A'}")
        return {
            "sucesso": False,
            "erro": f"Erro ao interpretar resposta da IA: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro ao extrair dados de entregadores: {e}")
        return {
            "sucesso": False,
            "erro": str(e)
        }
