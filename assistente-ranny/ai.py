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



async def extrair_dados_entregadores(texto: str, tipo_periodo: str = 'semanal') -> dict:
    """Extrai dados de entregadores do texto usando IA
    
    Args:
        texto: Descrição da semana/mês de entregas
        tipo_periodo: 'semanal' ou 'mensal' (padrão: 'semanal')
    
    Returns:
        Dicionário com estrutura:
        {
            "sucesso": True/False,
            "dados": {
                "periodo": "Semana 10/02 a 16/02" ou "Janeiro/2026",
                "dias": [
                    {
                        "dia": "segunda" (semanal) ou "01/02" (mensal), 
                        "entregadores": ["João", "Pedro", "Maria"], 
                        "chegaram_horario": 0, 
                        "entregas": 20
                    },
                    ...
                ]
            },
            "erro": "mensagem de erro" (se falhar)
        }
    """
    try:
        # Detecta mês mencionado no texto (para período mensal)
        meses_map = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3,
            'abril': 4, 'maio': 5, 'junho': 6,
            'julho': 7, 'agosto': 8, 'setembro': 9,
            'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
        
        mes_detectado = None
        texto_lower = texto.lower()
        for nome_mes, num_mes in meses_map.items():
            if nome_mes in texto_lower:
                mes_detectado = num_mes
                break
        
        # Se é mensal e não detectou mês, usa mês atual
        if tipo_periodo == 'mensal' and mes_detectado is None:
            from datetime import datetime
            mes_detectado = datetime.now().month
        
        # Cria prompt baseado no tipo de período
        if tipo_periodo == 'mensal':
            # PROMPT MENSAL - usa datas (DD/MM)
            from datetime import datetime
            import calendar
            
            ano_atual = datetime.now().year
            mes_nome = list(meses_map.keys())[mes_detectado - 1].capitalize()
            num_dias = calendar.monthrange(ano_atual, mes_detectado)[1]
            
            prompt = f"""Você é um assistente que extrai dados estruturados de texto.

CONTEXTO:
A Ranny descreve o mês de trabalho dos entregadores da pizzaria.

REGRAS DE NEGÓCIO:
- Segunda a quinta: R$ 1,00 por entregador escalado
- Sexta a domingo: R$ 10,00 por entregador escalado
- Sexta a domingo: R$ 10,00 adicional por cada entregador que chegar até 18:10h
- Sempre: R$ 12,00 por entrega realizada

IMPORTANTE:
- Use formato DD/MM para as datas (exemplo: "01/{mes_detectado:02d}", "02/{mes_detectado:02d}", etc.)
- O mês tem {num_dias} dias
- "chegaram_horario" deve ser 0 (zero) para segunda a quinta
- "chegaram_horario" só tem valor para sexta, sábado e domingo
- Se não mencionar quem chegou no horário, assume 0

TAREFA:
Extraia os dados do texto abaixo e retorne APENAS um JSON válido (sem markdown, sem explicações).

FORMATO DO JSON:
{{
  "periodo": "{mes_nome}/{ano_atual}",
  "dias": [
    {{"dia": "01/{mes_detectado:02d}", "entregadores": ["João Silva", "Pedro Santos"], "chegaram_horario": 0, "entregas": 20}},
    {{"dia": "02/{mes_detectado:02d}", "entregadores": ["João Silva", "Pedro Santos"], "chegaram_horario": 0, "entregas": 18}},
    ...
  ]
}}

IMPORTANTE SOBRE NOMES:
- "entregadores" deve ser uma LISTA com os NOMES dos entregadores que trabalharam naquele dia
- Se a Ranny não mencionar nomes específicos, use nomes genéricos como ["Entregador 1", "Entregador 2", etc]
- O número de nomes na lista deve corresponder à quantidade de entregadores do dia

TEXTO DA RANNY:
{texto}

RETORNE APENAS O JSON (sem ```json, sem explicações):"""
        else:
            # PROMPT SEMANAL - usa nomes de dias (segunda, terça, etc.)
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
- Para "periodo": tente identificar datas no texto (ex: "semana do dia 3", "semana passada")
- Se não houver datas mencionadas, use "Semana DD/MM a DD/MM" (será calculado automaticamente)

TAREFA:
Extraia os dados do texto abaixo e retorne APENAS um JSON válido (sem markdown, sem explicações).

FORMATO DO JSON:
{{
  "periodo": "Semana DD/MM a DD/MM",
  "dias": [
    {{"dia": "segunda", "entregadores": ["João Silva", "Pedro Santos", "Maria Costa"], "chegaram_horario": 0, "entregas": 20}},
    {{"dia": "terca", "entregadores": ["João Silva", "Pedro Santos", "Maria Costa"], "chegaram_horario": 0, "entregas": 18}},
    {{"dia": "quarta", "entregadores": ["João Silva", "Pedro Santos", "Maria Costa"], "chegaram_horario": 0, "entregas": 22}},
    {{"dia": "quinta", "entregadores": ["João Silva", "Pedro Santos", "Maria Costa"], "chegaram_horario": 0, "entregas": 19}},
    {{"dia": "sexta", "entregadores": ["João Silva", "Pedro Santos", "Maria Costa", "Lucas Oliveira"], "chegaram_horario": 3, "entregas": 30}},
    {{"dia": "sabado", "entregadores": ["João Silva", "Pedro Santos", "Maria Costa", "Lucas Oliveira"], "chegaram_horario": 4, "entregas": 35}},
    {{"dia": "domingo", "entregadores": ["João Silva", "Pedro Santos", "Maria Costa", "Lucas Oliveira"], "chegaram_horario": 3, "entregas": 28}}
  ]
}}

IMPORTANTE SOBRE NOMES:
- "entregadores" deve ser uma LISTA com os NOMES dos entregadores que trabalharam naquele dia
- Se a Ranny não mencionar nomes específicos, use nomes genéricos como ["Entregador 1", "Entregador 2", etc]
- O número de nomes na lista deve corresponder à quantidade de entregadores do dia

TEXTO DA RANNY:
{texto}

RETORNE APENAS O JSON (sem ```json, sem explicações):"""
        
        model_entregadores = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model_entregadores.generate_content(
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
            
            # Converte entregadores para lista se for número (compatibilidade)
            if isinstance(dia['entregadores'], int):
                num_entregadores = dia['entregadores']
                dia['entregadores'] = [f"Entregador {i+1}" for i in range(num_entregadores)]
            elif not isinstance(dia['entregadores'], list):
                return {
                    "sucesso": False,
                    "erro": f"Dia {dia.get('dia', '?')}: 'entregadores' deve ser lista ou número"
                }
        
        # Gera período se não tiver ou se for placeholder (apenas para semanal)
        if tipo_periodo == 'semanal' and ('periodo' not in dados or not dados['periodo'] or 'DD/MM' in dados.get('periodo', '')):
            from datetime import datetime, timedelta
            hoje = datetime.now()
            
            # Calcula segunda-feira da semana ANTERIOR (semana que acabou)
            dias_desde_segunda = hoje.weekday()  # 0=segunda, 6=domingo
            segunda_anterior = hoje - timedelta(days=dias_desde_segunda + 7)
            domingo_anterior = segunda_anterior + timedelta(days=6)
            
            dados['periodo'] = f"Semana {segunda_anterior.strftime('%d/%m')} a {domingo_anterior.strftime('%d/%m')}"
        
        logger.info(f"Dados de entregadores extraídos ({tipo_periodo}): {len(dados['dias'])} dias")
        
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



# ============ FUNÇÕES PARA PLANILHAS PERSONALIZADAS ============

async def extrair_estrutura_planilha(descricao: str) -> dict:
    """Extrai estrutura de planilha a partir de descrição natural
    
    Args:
        descricao: Descrição natural da planilha desejada (max 1000 chars)
    
    Returns:
        Dicionário com estrutura:
        {
            "sucesso": True/False,
            "estrutura": {
                "titulo": "Nome da Planilha",
                "colunas": [
                    {"nome": "Coluna1", "tipo": "texto|numero|moeda|data|porcentagem", "largura": 15},
                    ...
                ],
                "dados_exemplo": [
                    ["valor1", "valor2", ...],
                    ...
                ],
                "tem_total": True/False,
                "colunas_total": ["Coluna1", "Coluna2"]  // quais colunas devem ter total
            },
            "erro": "mensagem" (se falhar)
        }
    """
    try:
        # Sanitiza input do usuário
        if not descricao or not descricao.strip():
            return {
                "sucesso": False,
                "erro": "Descrição vazia"
            }
        
        descricao = descricao.strip()[:1000]  # Limita a 1000 caracteres
        prompt = f"""Você é um assistente especializado em criar planilhas Excel.

TAREFA:
Analise a descrição abaixo e extraia a estrutura da planilha desejada.

DESCRIÇÃO:
{descricao}

RETORNE APENAS UM JSON VÁLIDO (sem ```json, sem explicações, sem comentários) com esta estrutura:
{{
  "titulo": "Nome descritivo da planilha",
  "colunas": [
    {{
      "nome": "Nome da Coluna",
      "tipo": "texto",
      "largura": 15
    }}
  ],
  "dados_exemplo": [
    ["exemplo1", "exemplo2"]
  ],
  "tem_total": true,
  "colunas_total": ["Nome das colunas"]
}}

IMPORTANTE:
- Use APENAS aspas duplas ("), nunca aspas simples (')
- NÃO inclua comentários no JSON (nada com //)
- NÃO adicione vírgulas após o último item de arrays ou objetos
- Valores booleanos: true ou false (minúsculas, sem aspas)
- Valores numéricos: sem aspas (ex: 15, não "15")
- Valores de texto: sempre entre aspas duplas

REGRAS:
1. Identifique o tipo correto de cada coluna:
   - "texto": nomes, descrições, categorias
   - "numero": quantidades, contadores
   - "moeda": valores em R$
   - "data": datas (DD/MM/AAAA)
   - "porcentagem": valores em %

2. Largura sugerida:
   - texto curto: 15
   - texto longo (descrição): 30
   - numero/moeda: 12
   - data: 12
   - porcentagem: 10

3. tem_total = true se houver colunas numéricas/moeda que devem ser somadas

4. dados_exemplo: 
   - Se a descrição incluir dados específicos, extraia TODAS as linhas fornecidas
   - Identifique múltiplas linhas mesmo sem quebras de linha (ex: "05/01, A, 100Ativo10/01, B, 200Pendente" = 2 linhas)
   - Se não houver dados específicos, crie 2-3 linhas de exemplo com valores realistas

5. EXEMPLO DE MÚLTIPLAS LINHAS:
   Descrição: "Colunas: Data, Produto, Valor, Status05/01, Produto A, 100.00, Ativo10/01, Produto B, 200.00, Pendente"
   Resultado: "dados_exemplo": [["05/01", "Produto A", 100.00, "Ativo"], ["10/01", "Produto B", 200.00, "Pendente"]]

EXEMPLO DE JSON VÁLIDO:
{{
  "titulo": "Controle de Vendas",
  "colunas": [
    {{"nome": "Data", "tipo": "data", "largura": 12}},
    {{"nome": "Produto", "tipo": "texto", "largura": 20}},
    {{"nome": "Valor", "tipo": "moeda", "largura": 12}}
  ],
  "dados_exemplo": [
    ["01/02/2026", "Produto A", 150.50],
    ["02/02/2026", "Produto B", 200.00]
  ],
  "tem_total": true,
  "colunas_total": ["Valor"]
}}

RETORNE APENAS O JSON:"""

        model_planilha = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model_planilha.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=2000,
            )
        )
        
        if not response or not response.text:
            return {
                "sucesso": False,
                "erro": "IA não retornou resposta"
            }
        
        # Limpa resposta
        resposta_texto = response.text.strip()
        resposta_texto = resposta_texto.replace('```json', '').replace('```', '').strip()
        
        # Remove possíveis comentários no JSON (// ...)
        import re
        resposta_texto = re.sub(r'//.*', '', resposta_texto)
        
        # Parse JSON
        try:
            estrutura = json.loads(resposta_texto)
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido retornado pela IA: {resposta_texto[:200]}")
            logger.error(f"Erro de parse: {e}")
            return {
                "sucesso": False,
                "erro": f"IA retornou JSON inválido: {str(e)}"
            }
        
        # Valida estrutura básica
        if 'colunas' not in estrutura or not isinstance(estrutura['colunas'], list):
            return {
                "sucesso": False,
                "erro": "Estrutura JSON inválida - faltam colunas"
            }
        
        if not estrutura['colunas']:
            return {
                "sucesso": False,
                "erro": "Nenhuma coluna identificada"
            }
        
        # Valida tipos de coluna
        tipos_validos = {'texto', 'numero', 'moeda', 'data', 'porcentagem'}
        for idx, col in enumerate(estrutura['colunas']):
            if 'tipo' not in col or col['tipo'] not in tipos_validos:
                return {
                    "sucesso": False,
                    "erro": f"Coluna {idx+1}: tipo inválido (deve ser: texto, numero, moeda, data ou porcentagem)"
                }
            if 'nome' not in col or not col['nome']:
                return {
                    "sucesso": False,
                    "erro": f"Coluna {idx+1}: nome obrigatório"
                }
            if 'largura' in col and (not isinstance(col['largura'], (int, float)) or col['largura'] <= 0):
                return {
                    "sucesso": False,
                    "erro": f"Coluna {idx+1}: largura deve ser número positivo"
                }
        
        # Valida tem_total
        if 'tem_total' in estrutura and not isinstance(estrutura['tem_total'], bool):
            return {
                "sucesso": False,
                "erro": "tem_total deve ser true ou false"
            }
        
        # Valida colunas_total
        if 'colunas_total' in estrutura and not isinstance(estrutura['colunas_total'], list):
            return {
                "sucesso": False,
                "erro": "colunas_total deve ser uma lista"
            }
        
        logger.info(f"Estrutura de planilha extraída: {estrutura.get('titulo', 'Sem título')}, {len(estrutura['colunas'])} colunas")
        
        return {
            "sucesso": True,
            "estrutura": estrutura
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao fazer parse do JSON: {e}")
        return {
            "sucesso": False,
            "erro": f"Erro ao interpretar resposta da IA: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro ao extrair estrutura de planilha: {e}")
        return {
            "sucesso": False,
            "erro": str(e)
        }


async def interpretar_edicao_planilha(instrucao: str, estrutura: dict) -> dict:
    """Interpreta instrução de edição de planilha
    
    Args:
        instrucao: Comando natural de edição (max 500 chars)
        estrutura: Estrutura atual da planilha (colunas, etc)
    
    Returns:
        Dicionário com ação:
        {
            "sucesso": True/False,
            "acao": "adicionar_linha|editar_celula|remover_linha|editar_coluna|substituir_valor",
            "parametros": {
                "linha": numero ou null,
                "coluna": nome ou null,
                "valores": [...] ou null,
                "operacao": "multiplicar|dividir|somar|subtrair" ou null,
                "fator": numero ou null
            },
            "erro": "mensagem" (se falhar)
        }
    """
    try:
        # Sanitiza input do usuário
        if not instrucao or not instrucao.strip():
            return {
                "sucesso": False,
                "erro": "Instrução vazia"
            }
        
        instrucao = instrucao.strip()[:500]  # Limita a 500 caracteres
        # Monta descrição das colunas
        colunas_desc = []
        for idx, col in enumerate(estrutura.get('colunas', [])):
            colunas_desc.append(f"Coluna {idx+1}: {col['nome']} ({col['tipo']})")
        
        colunas_texto = "\n".join(colunas_desc)
        
        prompt = f"""Você é um assistente especializado em editar planilhas Excel.

ESTRUTURA DA PLANILHA:
{colunas_texto}

INSTRUÇÃO DO USUÁRIO:
{instrucao}

TAREFA:
Interprete a instrução e retorne APENAS UM JSON VÁLIDO (sem ```json, sem explicações) com esta estrutura:

{{
  "acao": "adicionar_linha|editar_celula|remover_linha|editar_coluna|substituir_valor",
  "parametros": {{
    "linha": numero_da_linha_ou_null,
    "coluna": "nome_da_coluna_ou_null",
    "valores": ["valor1", "valor2", ...] ou null,
    "operacao": "multiplicar|dividir|somar|subtrair" ou null,
    "fator": numero ou null
  }}
}}

TIPOS DE AÇÃO:
1. adicionar_linha: adicionar uma ou mais linhas de dados
   - valores: array com valores para cada coluna

2. editar_celula: alterar valor de célula específica
   - linha: número da linha (1, 2, 3...)
   - coluna: nome da coluna
   - valores: [novo_valor]

3. remover_linha: remover linha(s)
   - linha: número da linha ou "ultima" ou "todas"

4. editar_coluna: aplicar operação em coluna inteira
   - coluna: nome da coluna
   - operacao: tipo de operação
   - fator: número para aplicar

5. substituir_valor: buscar e substituir valores
   - coluna: nome da coluna (ou null para todas)
   - valores: [valor_antigo, valor_novo]

EXEMPLOS:
- "Adiciona: 10/02, Mercado, 150, Alimentação" → adicionar_linha com valores
- "Muda o valor da linha 2 para 200" → editar_celula, linha 2, coluna do tipo moeda
- "Remove a última linha" → remover_linha, linha "ultima"
- "Multiplica todos os valores por 2" → editar_coluna, coluna do tipo moeda, operacao multiplicar, fator 2

RETORNE APENAS O JSON:"""

        model_edicao = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model_edicao.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        
        if not response or not response.text:
            return {
                "sucesso": False,
                "erro": "IA não retornou resposta"
            }
        
        # Limpa resposta
        resposta_texto = response.text.strip()
        resposta_texto = resposta_texto.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        acao_dict = json.loads(resposta_texto)
        
        # Valida estrutura básica
        if 'acao' not in acao_dict:
            return {
                "sucesso": False,
                "erro": "Estrutura JSON inválida - falta 'acao'"
            }
        
        # Valida tipo de ação
        acoes_validas = {'adicionar_linha', 'editar_celula', 'remover_linha', 'editar_coluna', 'substituir_valor'}
        if acao_dict['acao'] not in acoes_validas:
            return {
                "sucesso": False,
                "erro": f"Ação inválida: {acao_dict['acao']} (deve ser: {', '.join(acoes_validas)})"
            }
        
        # Valida parametros
        if 'parametros' not in acao_dict or not isinstance(acao_dict['parametros'], dict):
            return {
                "sucesso": False,
                "erro": "Estrutura JSON inválida - falta 'parametros' ou não é um objeto"
            }
        
        logger.info(f"Ação de edição interpretada: {acao_dict['acao']}")
        
        return {
            "sucesso": True,
            "acao": acao_dict['acao'],
            "parametros": acao_dict.get('parametros', {})
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao fazer parse do JSON: {e}")
        return {
            "sucesso": False,
            "erro": f"Erro ao interpretar resposta da IA: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Erro ao interpretar edição: {e}")
        return {
            "sucesso": False,
            "erro": str(e)
        }
