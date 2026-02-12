"""
🤖 Bot Telegram - Assistente Ranny V3
Integração completa com todos os módulos
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode
import io

# Importa módulos do projeto
import ai
import database_adapter as db
import config
import scheduler
import jobs
import pdf_reader
import pdf_tools
import date_parser

load_dotenv()

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Silencia logs verbosos
for noisy in ['httpx', 'httpcore', 'telegram', 'telegram.ext', 'apscheduler']:
    logging.getLogger(noisy).setLevel(logging.WARNING)


# ============ CACHE DE BUSCA ============
# Armazena resultados de busca para reenvio com "manda o 1"
user_search_results = {}

# ============ CACHE DE TÓPICOS ============
# Armazena IDs de tópicos criados dinamicamente para reutilização
cached_topic_ids = {}

# ============ CONSTANTES DE NEGÓCIO ============
# Custos de entregadores
CUSTO_ENTREGADOR_SEMANA = 1.00  # Segunda a quinta
CUSTO_ENTREGADOR_FDS = 10.00    # Sexta a domingo
BONUS_HORARIO_FDS = 10.00        # Chegou até 18:10h (só FDS)
CUSTO_POR_ENTREGA = 12.00        # Sempre

# Dias de fim de semana
DIAS_FDS = {'sexta', 'sabado', 'sábado', 'domingo'}

# Palavras-chave para detecção (convertidas para set para busca O(1))
PALAVRAS_CONFIRMACAO = {'sim', 'confirma', 'confirmo', 'ok', 'correto', 'certo', 'isso', 'exato'}
PALAVRAS_NEGACAO = {'não', 'nao', 'errado', 'cancela'}
PALAVRAS_CHAVE_PLANILHA = {
    'planilha', 'entregador', 'entregadores', 
    'semana', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'sabado', 'domingo',
    'mês', 'mes', 'mensal', 'janeiro', 'fevereiro', 'março', 'marco', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
    'quinzena', 'periodo', 'período'
}
VERBOS_CRIACAO = {'cria', 'criar', 'faz', 'fazer', 'gera', 'gerar', 'monta', 'montar'}
PALAVRAS_PERIODO_MENSAL = {'mês', 'mes', 'mensal', 'janeiro', 'fevereiro', 'março', 'marco', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro', 'quinzena'}

# Palavras-chave para edição de planilhas
PALAVRAS_ADICIONAR = {'adiciona', 'adicionar', 'insere', 'inserir', 'coloca', 'põe', 'poe'}
PALAVRAS_EDITAR = {'muda', 'mudar', 'altera', 'alterar', 'corrige', 'corrigir', 'edita', 'editar', 'atualiza', 'atualizar'}
PALAVRAS_REMOVER = {'remove', 'remover', 'apaga', 'apagar', 'deleta', 'deletar', 'exclui', 'excluir'}

# Palavras-chave para detectar planilhas pessoais (não relacionadas à pizzaria)
PALAVRAS_CHAVE_PESSOAL = {
    'pessoal', 'pessoais', 'particular', 'particulares',
    'financeiro', 'financeira', 'finanças', 'financas',
    'gastos', 'gasto', 'despesas', 'despesa',
    'receitas', 'receita', 'renda', 'rendas',
    'controle', 'controlar', 'acompanhamento',
    'orçamento', 'orcamento', 'budget',
    'investimento', 'investimentos', 'poupança', 'poupanca',
    'cartão', 'cartao', 'crédito', 'credito', 'débito', 'debito',
    'conta', 'contas', 'pagamento', 'pagamentos',
    'salário', 'salario', 'salários', 'salarios'
}


# ============ FUNÇÕES AUXILIARES ============

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiais do Markdown V2"""
    if not text:
        return text
    
    # Caracteres que precisam ser escapados no MarkdownV2
    chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in chars_to_escape:
        text = text.replace(char, f'\\{char}')
    
    return text


def calcular_custo_dia(dia: str, entregadores: int, chegaram_horario: int, entregas: int) -> dict:
    """Calcula custos de um dia de entregas
    
    Args:
        dia: Nome do dia da semana (ex: "segunda") ou data (ex: "01/02")
        entregadores: Número de entregadores escalados
        chegaram_horario: Quantos chegaram até 18:10h
        entregas: Total de entregas realizadas
    
    Returns:
        dict com: custo_entregadores, bonus_horario, custo_entregas, total
    """
    # Detecta se é fim de semana
    if '/' in dia:
        # Formato de data: parseia e verifica weekday
        try:
            from datetime import datetime
            dia_num, mes_num = dia.split('/')
            ano_atual = datetime.now().year
            data = datetime(ano_atual, int(mes_num), int(dia_num))
            # weekday: 0=segunda, 4=sexta, 5=sábado, 6=domingo
            is_fds = data.weekday() >= 4
        except:
            is_fds = False
    else:
        # Formato de nome de dia
        is_fds = any(d in dia.lower() for d in DIAS_FDS)
    
    if is_fds:
        custo_entregadores = entregadores * CUSTO_ENTREGADOR_FDS
        bonus_horario = chegaram_horario * BONUS_HORARIO_FDS
    else:
        custo_entregadores = entregadores * CUSTO_ENTREGADOR_SEMANA
        bonus_horario = 0
    
    custo_entregas = entregas * CUSTO_POR_ENTREGA
    total = custo_entregadores + bonus_horario + custo_entregas
    
    return {
        'custo_entregadores': custo_entregadores,
        'bonus_horario': bonus_horario,
        'custo_entregas': custo_entregas,
        'total': total,
        'is_fds': is_fds
    }

def detecta_tipo_periodo(texto: str) -> str:
    """Detecta se o período mencionado é semanal ou mensal
    
    Args:
        texto: Texto da descrição
    
    Returns:
        'semanal' ou 'mensal'
    """
    texto_lower = texto.lower()
    
    # Verifica se menciona palavras relacionadas a mês
    if any(palavra in texto_lower for palavra in PALAVRAS_PERIODO_MENSAL):
        return 'mensal'
    
    # Por padrão, assume semanal
    return 'semanal'


def valida_dados_entregadores(dados: dict, tipo_periodo: str) -> list:
    """Valida dados extraídos e retorna lista de alertas
    
    Args:
        dados: Dicionário com dados extraídos
        tipo_periodo: 'semanal' ou 'mensal'
    
    Returns:
        Lista de strings com alertas (vazia se tudo OK)
    """
    alertas = []
    
    if 'dias' not in dados or not dados['dias']:
        return alertas
    
    dias_data = dados['dias']
    
    # Valida quantidade de dias
    if tipo_periodo == 'semanal' and len(dias_data) > 7:
        alertas.append(f"⚠️ Período semanal com {len(dias_data)} dias (esperado: até 7)")
    elif tipo_periodo == 'mensal' and len(dias_data) > 31:
        alertas.append(f"⚠️ Período mensal com {len(dias_data)} dias (esperado: até 31)")
    
    # Valida dados de cada dia
    total_entregas = 0
    dias_sem_entregas = []
    dias_muitos_entregadores = []
    
    for dia_info in dias_data:
        dia = dia_info.get('dia', '?')
        entregadores = dia_info.get('entregadores', [])
        entregas = dia_info.get('entregas', 0)
        
        # Conta entregadores
        num_entregadores = len(entregadores) if isinstance(entregadores, list) else entregadores
        
        # Alerta: dia sem entregas
        if entregas == 0:
            dias_sem_entregas.append(dia)
        
        # Alerta: muitos entregadores (mais de 10 é suspeito)
        if num_entregadores > 10:
            dias_muitos_entregadores.append(f"{dia} ({num_entregadores} entregadores)")
        
        total_entregas += entregas
    
    # Gera alertas
    if dias_sem_entregas and len(dias_sem_entregas) <= 3:
        alertas.append(f"⚠️ Dias sem entregas: {', '.join(dias_sem_entregas)}")
    
    if dias_muitos_entregadores:
        alertas.append(f"⚠️ Muitos entregadores: {', '.join(dias_muitos_entregadores)}")
    
    if total_entregas == 0:
        alertas.append("⚠️ Total de entregas é ZERO")
    
    return alertas


def is_planilha_pessoal(texto: str, titulo: str = "") -> bool:
    """Detecta se uma planilha é pessoal (não relacionada à pizzaria)
    
    Args:
        texto: Texto da solicitação original
        titulo: Título da planilha (opcional)
    
    Returns:
        True se for planilha pessoal, False caso contrário
    """
    texto_completo = f"{texto} {titulo}".lower()
    
    # Verifica se contém palavras-chave pessoais
    tem_palavra_pessoal = any(palavra in texto_completo for palavra in PALAVRAS_CHAVE_PESSOAL)
    
    # Verifica se NÃO contém palavras relacionadas à pizzaria/operacional
    palavras_pizzaria = {
        'entregador', 'entregadores', 'motoboy', 'motoboys',
        'delivery', 'entregas', 'entrega',
        'pizzaria', 'pizza', 'grn',
        'operacional', 'operação', 'operacao'
    }
    tem_palavra_pizzaria = any(palavra in texto_completo for palavra in palavras_pizzaria)
    
    # É pessoal se tem palavra pessoal E não tem palavra de pizzaria
    return tem_palavra_pessoal and not tem_palavra_pizzaria


async def buscar_topico_por_nome(context: ContextTypes.DEFAULT_TYPE, nome_topico: str) -> int:
    """
    Busca um tópico existente no grupo pelo nome.
    Retorna o message_thread_id se encontrado, ou 0 se não encontrado.
    """
    try:
        # Tenta obter informações do fórum
        chat = await context.bot.get_chat(config.GROUP_ID)

        # Infelizmente, a API do Telegram não tem um método direto para listar todos os tópicos
        # Então vamos tentar uma abordagem alternativa: enviar uma mensagem de teste e deletar
        # Mas isso não é ideal. A melhor solução é cachear os IDs após a primeira criação.

        # Por enquanto, retornamos 0 para indicar que não encontramos
        # O bot criará o tópico e logará o ID para adicionar ao .env
        return 0

    except Exception as e:
        logger.error(f"❌ Erro ao buscar tópico '{nome_topico}': {e}")
        return 0



# ============ HANDLERS ============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    logger.info(f"🚀 Comando /start recebido")
    
    mensagem = """👋 Oi! Sou a Assistente Ranny!

Estou aqui para te ajudar com:
📁 Documentos (classifico e guardo automaticamente)
💰 Vencimentos e alertas
📊 Fechamento de caixa
📝 Lembretes inteligentes
🔍 Busca de arquivos
📄 Criar/editar PDF, Word e Excel

É só conversar comigo naturalmente! 😊

Exemplos:
• "fechei 2500"
• "me lembra amanhã de ligar pro contador"
• "cadê o contrato?"
• "cria um pdf com: [seu texto]"
• Envie fotos/PDFs que eu analiso e guardo"""
    
    await update.message.reply_text(mensagem)
    logger.info(f"✅ Resposta /start enviada")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    mensagem = """📚 **Comandos e Funcionalidades**

**💰 Financeiro:**
• Envie boletos/comprovantes → analiso e guardo
• "paguei a luz" → marco como pago

**📊 Fechamento:**
• "fechei 2500" → registro de caixa
• "mostra gráfico da semana" → relatório

**📝 Lembretes:**
• "me lembra amanhã às 14h de..."
• "todo dia 7 lembra do FGTS"
• "quais meus lembretes?"
• "cancela lembrete do FGTS"

**🔍 Busca:**
• "cadê o contrato?"
• "procura nota fiscal"
• "manda o 1" → mostra onde está o resultado

**📄 Criar Arquivos:**
• "cria um pdf com: [texto]"
• "cria um word com: [texto]"
• "cria uma planilha com: [dados]"

**📖 Ler Arquivos:**
• Envie .docx + "lê esse documento"
• Envie .xlsx + "lê essa planilha"

**✏️ Editar Arquivos:**
• Envie .docx + "adiciona: [texto]"
• Envie .xlsx + "adiciona linha: [dados]"
• Envie arquivo + "substitui X por Y"

É só conversar naturalmente! 💬"""
    
    await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para documentos (PDF, DOCX, XLSX, etc)"""
    
    message = update.message
    document = message.document
    caption = message.caption or ""
    user_id = update.effective_user.id
    
    try:
        # Baixa o arquivo
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        file_bytes = bytes(file_bytes)
        
        file_name = document.file_name or "documento"
        file_size = len(file_bytes)
        
        logger.info(f"📎 Documento recebido: {file_name} ({file_size} bytes)")
        
        # Verifica se usuário quer LER o arquivo
        if any(palavra in caption.lower() for palavra in ['lê', 'le', 'leia', 'ler', 'mostra', 'abre']):
            await handle_ler_arquivo(update, context, file_bytes, file_name, caption)
            return
        
        # Verifica se usuário quer EDITAR o arquivo
        if any(palavra in caption.lower() for palavra in ['adiciona', 'edita', 'substitui', 'remove', 'altera', 'muda']):
            await handle_editar_arquivo(update, context, file_bytes, file_name, caption)
            return
        
        # Se não é leitura/edição, processa como documento para GUARDAR
        await message.reply_text("⏳ Analisando documento...")
        
        # Analisa o arquivo
        dados = await ai.analyze_file(file_bytes, file_name, caption)
        
        # Classifica categoria
        texto_classificacao = dados.get('descricao', '') + ' ' + caption
        categoria = await ai.classify_document(texto_classificacao)
        
        # Salva no banco
        doc_record = db.add_documento(
            tipo=document.mime_type or 'application/octet-stream',
            descricao=dados.get('descricao', file_name),
            file_id=document.file_id,
            categoria=categoria,
            dados_extraidos=dados
        )
        
        # Se extraiu dados de boleto, cria vencimento
        if dados.get('tipo_documento') == 'boleto' and (dados.get('valor') or dados.get('vencimento')):
            vencimento = db.criar_vencimento_de_boleto(dados, doc_record.get('id'))
            if vencimento:
                logger.info(f"✅ Vencimento criado: {vencimento.get('descricao')}")
        
        # Monta resposta rica
        resposta = montar_resposta_documento(dados, categoria, file_name)
        
        # Envia para o tópico correto
        topic_id = config.CATEGORIA_TOPICO.get(categoria, config.TOPICS['outros'])
        
        await context.bot.send_message(
            chat_id=config.GROUP_ID,
            text=resposta,
            message_thread_id=topic_id,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Confirma no chat
        await message.reply_text(f"✅ Guardei em **{categoria.title()}**! 📁", parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar documento: {e}")
        await message.reply_text(f"❌ Erro ao processar documento: {str(e)}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para fotos"""
    
    message = update.message
    photo = message.photo[-1]  # Pega a maior resolução
    caption = message.caption or ""
    
    try:
        # Baixa a foto
        file = await photo.get_file()
        file_bytes = await file.download_as_bytearray()
        file_bytes = bytes(file_bytes)
        
        logger.info(f"🖼️ Foto recebida ({len(file_bytes)} bytes)")
        
        await message.reply_text("⏳ Analisando imagem...")
        
        # Analisa com Gemini Vision
        dados = await ai.analyze_image(file_bytes, caption)
        
        # Classifica categoria
        texto_classificacao = dados.get('descricao', '') + ' ' + caption
        categoria = await ai.classify_document(texto_classificacao)
        
        # Salva no banco
        doc_record = db.add_documento(
            tipo='image/jpeg',
            descricao=dados.get('descricao', 'Imagem'),
            file_id=photo.file_id,
            categoria=categoria,
            dados_extraidos=dados
        )
        
        # Se extraiu dados de boleto, cria vencimento
        if dados.get('tipo_documento') == 'boleto' and (dados.get('valor') or dados.get('vencimento')):
            vencimento = db.criar_vencimento_de_boleto(dados, doc_record.get('id'))
            if vencimento:
                logger.info(f"✅ Vencimento criado: {vencimento.get('descricao')}")
        
        # Monta resposta
        resposta = montar_resposta_documento(dados, categoria, 'Imagem')
        
        # Envia para o tópico correto
        topic_id = config.CATEGORIA_TOPICO.get(categoria, config.TOPICS['outros'])
        
        await context.bot.send_message(
            chat_id=config.GROUP_ID,
            text=resposta,
            message_thread_id=topic_id,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Confirma no chat
        await message.reply_text(f"✅ Guardei em **{categoria.title()}**! 📁", parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar foto: {e}")
        await message.reply_text(f"❌ Erro ao processar foto: {str(e)}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensagens de texto"""
    
    message = update.message
    text = message.text.strip()
    user_id = update.effective_user.id
    
    # Ignora mensagens vazias
    if not text:
        return
    
    logger.info(f"💬 Mensagem: {text[:50]}...")
    
    try:
        # ===== FECHAMENTO DE CAIXA =====
        if await handle_fechamento(update, context, text):
            return
        
        # ===== LEMBRETES =====
        if await handle_lembretes(update, context, text):
            return
        
        # ===== VENCIMENTOS =====
        if await handle_vencimentos(update, context, text):
            return
        
        # ===== PLANILHA DE ENTREGADORES ===== (MOVIDO PARA ANTES DA BUSCA)
        if await handle_planilha_entregadores(update, context, text):
            return
        
        # ===== BUSCA DE DOCUMENTOS ===== (DESABILITADO - grupo organizado)
        # if await handle_busca_documentos(update, context, text):
        #     return
        
        # ===== REENVIO DE DOCUMENTO =====
        if await handle_reenvio_documento(update, context, text, user_id):
            return
        
        # ===== RELATÓRIOS =====
        if await handle_relatorios(update, context, text):
            return
        
        # ===== EDIÇÃO DE PLANILHA COM CONTEXTO (antes de criar) =====
        if await handle_editar_planilha_contexto(update, context, text):
            return
        
        # ===== CRIAÇÃO DE PLANILHA PERSONALIZADA =====
        if await handle_criar_planilha_personalizada(update, context, text):
            return
        
        # ===== CRIAÇÃO DE ARQUIVOS (genérico) =====
        if await handle_criar_arquivo(update, context, text):
            return
        
        # ===== CONVERSA COM IA =====
        await message.reply_text("⏳ Pensando...")
        resposta = await ai.get_response(user_id, text)
        await message.reply_text(resposta)
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        await message.reply_text(f"❌ Ops! Algo deu errado: {str(e)}")


# ============ HANDLERS ESPECÍFICOS ============

async def handle_fechamento(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Detecta e processa fechamento de caixa"""
    
    import re
    
    # Padrões: "fechei 2500", "fechamento 2500", "caixa 2500"
    patterns = [
        r'(?:fechei|fechamento|caixa)\s+(\d+(?:[.,]\d+)?)',
        r'hoje\s+(?:foi|fechou|deu)\s+(\d+(?:[.,]\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
                
                # Registra fechamento
                db.add_fechamento(valor)
                
                # Busca fechamentos da semana
                fechamentos = db.get_fechamentos(7)
                total_semana = sum(f['valor'] for f in fechamentos)
                
                # Compara com dia anterior
                anterior = db.get_fechamento_anterior()
                
                resposta = f"✅ *Fechamento registrado!*\n\n"
                resposta += f"📊 Hoje: R$ {valor:,.2f}\n"
                
                if anterior:
                    dif = valor - anterior['valor']
                    perc = (dif / anterior['valor'] * 100) if anterior['valor'] > 0 else 0
                    emoji = "📈" if dif > 0 else "📉"
                    resposta += f"📅 Ontem: R$ {anterior['valor']:,.2f} ({emoji} {perc:+.1f}%)\n"
                
                resposta += f"📆 Semana: R$ {total_semana:,.2f}\n"
                
                if anterior and valor > anterior['valor']:
                    resposta += f"\n🎉 Melhor que ontem!"
                
                await update.message.reply_text(resposta.replace(',', 'X').replace('.', ',').replace('X', '.'), parse_mode=ParseMode.MARKDOWN)
                return True
                
            except ValueError:
                pass
    
    return False


async def handle_lembretes(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Detecta e processa lembretes"""
    
    text_lower = text.lower()
    
    # ===== LISTAR LEMBRETES =====
    if any(palavra in text_lower for palavra in ['quais', 'meus lembretes', 'lista', 'ver lembretes']):
        lembretes = db.get_lembretes_ativos()
        
        if not lembretes:
            await update.message.reply_text("📝 Você não tem lembretes ativos no momento.")
            return True
        
        resposta = f"📝 *Seus lembretes ativos:*\n\n"
        for i, lem in enumerate(lembretes[:10], 1):
            data = lem['data']
            hora = lem.get('hora', '09:00')
            desc = lem['descricao']
            recorrente = lem.get('recorrente', '')
            
            resposta += f"{i}. 📌 {desc}\n"
            resposta += f"   📅 {data} às {hora}\n"
            if recorrente:
                resposta += f"   🔄 {recorrente}\n"
            resposta += "\n"
        
        await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
        return True
    
    # ===== CANCELAR LEMBRETE =====
    if 'cancela' in text_lower and 'lembrete' in text_lower:
        # Extrai termo de busca
        termo = text_lower.replace('cancela', '').replace('lembrete', '').replace('do', '').replace('da', '').strip()
        
        if termo:
            lembretes = db.buscar_lembrete_por_descricao(termo)
            
            if lembretes:
                # Cancela o primeiro encontrado
                db.cancelar_lembrete(lembretes[0]['id'])
                await update.message.reply_text(f"✅ Lembrete cancelado: *{lembretes[0]['descricao']}*", parse_mode=ParseMode.MARKDOWN)
                return True
            else:
                await update.message.reply_text(f"❌ Não encontrei lembrete com '{termo}'")
                return True
    
    # ===== CRIAR LEMBRETE =====
    if any(palavra in text_lower for palavra in ['lembra', 'lembre', 'avisa', 'avise']):
        try:
            # Parse de data e hora
            data, hora = date_parser.parse_data_hora(text)
            
            if not data:
                await update.message.reply_text("❌ Não entendi a data. Use algo como:\n• 'me lembra amanhã'\n• 'me lembra dia 15'\n• 'me lembra segunda às 14h'")
                return True
            
            # Extrai descrição
            descricao = date_parser.extrair_descricao_lembrete(text)
            
            if not descricao:
                await update.message.reply_text("❌ Não entendi o que você quer que eu lembre. Tente:\n'me lembra amanhã de ligar pro contador'")
                return True
            
            # Detecta recorrência
            recorrente = date_parser.detectar_recorrencia(text)
            
            # Cria lembrete
            lembrete = db.add_lembrete(
                descricao=descricao,
                data_lembrete=data,
                hora=hora or '09:00',
                recorrente=recorrente
            )
            
            resposta = f"✅ *Lembrete criado!*\n\n"
            resposta += f"📅 {data} às {hora or '09:00'}\n"
            resposta += f"📝 {descricao}\n"
            
            if recorrente:
                tipo_rec = {'diario': 'diário', 'semanal': 'semanal', 'mensal': 'mensal'}.get(recorrente, recorrente)
                resposta += f"\n🔄 Lembrete {tipo_rec}"
            
            await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar lembrete: {e}")
            # Não retorna True - deixa cair na conversa com IA
    
    return False


async def handle_vencimentos(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Detecta e processa vencimentos"""
    
    text_lower = text.lower()
    
    # ===== MARCAR COMO PAGO =====
    if 'paguei' in text_lower or 'pago' in text_lower:
        # Extrai termo (ex: "paguei a luz" -> "luz")
        termo = text_lower.replace('paguei', '').replace('pago', '').replace('a ', '').replace('o ', '').strip()
        
        if termo:
            vencimentos = db.buscar_vencimentos_nao_pagos(termo)
            
            if vencimentos:
                venc = vencimentos[0]  # Pega o mais recente
                
                # Marca como pago
                proximo = db.marcar_pago(venc['id'])
                
                resposta = f"✅ *Marcado como pago!*\n\n"
                resposta += f"📄 {venc['descricao']}\n"
                resposta += f"💰 R$ {venc['valor']:,.2f}\n"
                
                if proximo:
                    resposta += f"\n🔄 Próximo vencimento criado: {proximo['data_vencimento']}"
                
                await update.message.reply_text(resposta.replace(',', 'X').replace('.', ',').replace('X', '.'), parse_mode=ParseMode.MARKDOWN)
                return True
    
    return False


async def buscar_documentos_telegram(context: ContextTypes.DEFAULT_TYPE, termo: str) -> list:
    """Busca documentos diretamente nos tópicos do Telegram"""
    
    documentos_encontrados = []
    termo_lower = termo.lower()
    
    # Lista de tópicos para buscar
    topicos = [
        ('EMPRESA', config.TOPICS.get('empresa')),
        ('FINANCEIRO', config.TOPICS.get('financeiro')),
        ('FUNCIONARIOS', config.TOPICS.get('funcionarios')),
        ('JURIDICO', config.TOPICS.get('juridico')),
        ('PESSOAL', config.TOPICS.get('pessoal')),
        ('OPERACIONAL', config.TOPICS.get('operacional')),
        ('MIDIA', config.TOPICS.get('midia')),
        ('CONTROLES', config.TOPICS.get('controles')),
        ('OUTROS', config.TOPICS.get('outros')),
    ]
    
    try:
        for categoria, topic_id in topicos:
            if not topic_id:
                continue
            
            # Busca mensagens no tópico (últimas 100)
            try:
                # Pega o histórico de mensagens do tópico
                messages = []
                offset = 0
                
                # Busca até 100 mensagens por tópico
                for _ in range(5):  # 5 páginas de 20 = 100 mensagens
                    chat_history = await context.bot.get_chat(config.GROUP_ID)
                    # Nota: A API do Telegram não permite buscar por tópico diretamente
                    # Vamos usar uma abordagem diferente
                    break
                
            except Exception as e:
                logger.error(f"Erro ao buscar no tópico {categoria}: {e}")
                continue
    
    except Exception as e:
        logger.error(f"Erro geral na busca: {e}")
    
    return documentos_encontrados


# ===== FUNÇÃO DE BUSCA DE DOCUMENTOS DESABILITADA =====
# Removida porque o grupo está organizado em tópicos
# e não há necessidade de busca
"""
async def handle_busca_documentos(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    # Função comentada - busca desabilitada
    return False
"""


async def handle_reenvio_documento(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, user_id: int) -> bool:
    """Reenvia documento da busca"""
    
    import re
    
    # Padrão: "manda o 1", "envia o 2", "me manda o 3"
    match = re.search(r'(?:manda|envia|me manda|me envia)\s+(?:o\s+)?(\d+)', text.lower())
    
    if match:
        numero = int(match.group(1))
        
        # Busca resultados salvos
        if user_id not in user_search_results:
            await update.message.reply_text("❌ Você precisa fazer uma busca primeiro. Tente: 'cadê o contrato?'")
            return True
        
        documentos = user_search_results[user_id]
        
        if numero < 1 or numero > len(documentos):
            await update.message.reply_text(f"❌ Número inválido. Escolha entre 1 e {len(documentos)}")
            return True
        
        doc = documentos[numero - 1]
        
        try:
            # Informa onde o documento está
            categoria = doc.get('categoria', 'outros')
            resposta = f"📁 **{doc.get('descricao')}**\n\n"
            resposta += f"📂 Categoria: {categoria.title()}\n"
            resposta += f"📅 Salvo em: {doc.get('created_at', 'N/A')}\n\n"
            resposta += f"💡 Você pode encontrar este arquivo no tópico **{categoria.title()}** do grupo!"
            
            await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao mostrar documento: {e}")
            await update.message.reply_text(f"❌ Erro: {str(e)}")
            return True
    
    return False


async def handle_relatorios(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Gera relatórios com gráficos"""
    
    text_lower = text.lower()
    
    if 'gráfico' in text_lower or 'grafico' in text_lower or 'relatório' in text_lower or 'relatorio' in text_lower:
        # Detecta período
        if 'hoje' in text_lower:
            dias = 1
            periodo = 'Hoje'
        elif 'semana' in text_lower:
            dias = 7
            periodo = 'Última semana'
        elif 'quinzena' in text_lower:
            dias = 15
            periodo = 'Últimos 15 dias'
        elif 'trimestre' in text_lower:
            dias = 90
            periodo = 'Últimos 3 meses'
        else:
            dias = 30
            periodo = 'Último mês'
        
        # Busca dados
        fechamentos = db.get_fechamentos(dias)
        vencimentos = db.get_vencimentos_periodo(dias)
        
        if not fechamentos and not vencimentos:
            await update.message.reply_text("❌ Não há dados suficientes para gerar relatório")
            return True
        
        # Cria token temporário
        dados = {
            'fechamentos': fechamentos,
            'vencimentos': vencimentos,
            'periodo': periodo,
            'periodo_dias': dias
        }
        
        token = db.criar_relatorio_temp('periodo', dados)
        
        if not token:
            await update.message.reply_text("❌ Erro ao gerar relatório")
            return True
        
        # Monta resposta
        total = sum(f['valor'] for f in fechamentos) if fechamentos else 0
        media = total / len(fechamentos) if fechamentos else 0
        
        resposta = f"📊 *Relatório - {periodo}*\n\n"
        
        if fechamentos:
            resposta += f"💰 Total: R$ {total:,.2f}\n"
            resposta += f"📊 Média diária: R$ {media:,.2f}\n"
            resposta += f"📅 {len(fechamentos)} dias registrados\n\n"
        
        relatorio_url = f"{config.BASE_URL}/relatorio/{token}"
        resposta += f"🔗 [Ver gráficos interativos]({relatorio_url})\n\n"
        resposta += f"⏰ _O link expira em 24 horas_"
        
        await update.message.reply_text(resposta.replace(',', 'X').replace('.', ',').replace('X', '.'), parse_mode=ParseMode.MARKDOWN)
        return True
    
    return False


async def handle_criar_arquivo(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Cria arquivos PDF, DOCX, XLSX"""
    
    text_lower = text.lower()
    
    # Detecta tipo de arquivo
    if 'cria' in text_lower or 'criar' in text_lower or 'gera' in text_lower or 'gerar' in text_lower:
        
        # === PDF ===
        if 'pdf' in text_lower:
            # Extrai conteúdo após "com:"
            import re
            match = re.search(r'(?:cria|criar|gera|gerar)\s+(?:um\s+)?pdf\s+com[:\s]+(.+)', text, re.IGNORECASE | re.DOTALL)
            
            if match:
                conteudo = match.group(1).strip()
                
                # Extrai título (primeira linha ou primeiras palavras)
                linhas = conteudo.split('\n')
                titulo = linhas[0][:50] if linhas else "Documento"
                
                # Cria PDF
                pdf_bytes = pdf_tools.criar_pdf_texto(conteudo, titulo)
                
                if pdf_bytes:
                    # Gera nome do arquivo
                    nome_arquivo = titulo.lower().replace(' ', '_')[:30] + '.pdf'
                    
                    # Envia
                    await update.message.reply_document(
                        document=io.BytesIO(pdf_bytes),
                        filename=nome_arquivo,
                        caption=f"📄 PDF criado: {titulo}"
                    )
                    return True
                else:
                    await update.message.reply_text("❌ Erro ao criar PDF")
                    return True
        
        # === WORD ===
        elif 'word' in text_lower or 'docx' in text_lower or 'documento' in text_lower:
            import re
            match = re.search(r'(?:cria|criar|gera|gerar)\s+(?:um\s+)?(?:word|docx|documento)\s+com[:\s]+(.+)', text, re.IGNORECASE | re.DOTALL)
            
            if match:
                conteudo = match.group(1).strip()
                
                linhas = conteudo.split('\n')
                titulo = linhas[0][:50] if linhas else "Documento"
                
                # Cria DOCX
                docx_bytes = pdf_tools.criar_docx_texto(conteudo, titulo)
                
                if docx_bytes:
                    nome_arquivo = titulo.lower().replace(' ', '_')[:30] + '.docx'
                    
                    await update.message.reply_document(
                        document=io.BytesIO(docx_bytes),
                        filename=nome_arquivo,
                        caption=f"📄 Word criado: {titulo}"
                    )
                    return True
                else:
                    await update.message.reply_text("❌ Erro ao criar Word")
                    return True
        
        # === EXCEL ===
        elif 'excel' in text_lower or 'xlsx' in text_lower or 'planilha' in text_lower:
            import re
            match = re.search(r'(?:cria|criar|gera|gerar)\s+(?:um[a]?\s+)?(?:excel|xlsx|planilha)\s+com[:\s]+(.+)', text, re.IGNORECASE | re.DOTALL)
            
            if match:
                conteudo = match.group(1).strip()
                
                linhas = conteudo.split('\n')
                titulo = linhas[0][:30] if linhas else "Planilha"
                
                # Cria XLSX
                xlsx_bytes = pdf_tools.criar_xlsx_texto(conteudo, titulo)
                
                if xlsx_bytes:
                    nome_arquivo = titulo.lower().replace(' ', '_')[:30] + '.xlsx'
                    
                    await update.message.reply_document(
                        document=io.BytesIO(xlsx_bytes),
                        filename=nome_arquivo,
                        caption=f"📊 Excel criado: {titulo}"
                    )
                    return True
                else:
                    await update.message.reply_text("❌ Erro ao criar Excel")
                    return True
    
    return False


async def handle_ler_arquivo(update: Update, context: ContextTypes.DEFAULT_TYPE, file_bytes: bytes, file_name: str, caption: str):
    """Lê conteúdo de arquivo DOCX ou XLSX"""
    
    try:
        if file_name.lower().endswith('.docx'):
            # Lê DOCX
            resultado = pdf_tools.ler_docx(file_bytes)
            
            if resultado:
                texto = resultado['texto'][:1000]  # Limita a 1000 caracteres
                num_paragrafos = resultado['num_paragrafos']
                num_tabelas = resultado['num_tabelas']
                
                resposta = f"📄 *Conteúdo do documento:*\n\n"
                resposta += f"📝 {num_paragrafos} parágrafos, {num_tabelas} tabelas\n\n"
                resposta += f"```\n{texto}\n```"
                
                if len(resultado['texto']) > 1000:
                    resposta += f"\n\n_...conteúdo truncado_"
                
                await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Erro ao ler documento")
        
        elif file_name.lower().endswith('.xlsx'):
            # Lê XLSX
            resultado = pdf_tools.ler_xlsx(file_bytes)
            
            if resultado:
                resposta = f"📊 *Conteúdo da planilha:*\n\n"
                resposta += f"📋 {resultado['num_planilhas']} planilha(s)\n"
                
                # Mostra info por aba
                for nome_aba, dados_aba in resultado['planilhas'].items():
                    resposta += f"  📄 _{nome_aba}_: {len(dados_aba)} linha(s)\n"
                resposta += "\n"
                
                # Mostra primeiras linhas (limite maior)
                limite = 2000
                texto = resultado['texto'][:limite]
                resposta += f"```\n{texto}\n```"
                
                if len(resultado['texto']) > limite:
                    resposta += f"\n\n_...conteúdo truncado ({len(resultado['texto'])} caracteres total)_"
                
                await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Erro ao ler planilha")
        
        else:
            await update.message.reply_text("❌ Formato não suportado para leitura. Use .docx ou .xlsx")
    
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        await update.message.reply_text(f"❌ Erro ao ler arquivo: {str(e)}")


async def handle_editar_arquivo(update: Update, context: ContextTypes.DEFAULT_TYPE, file_bytes: bytes, file_name: str, caption: str):
    """Edita arquivo DOCX ou XLSX"""
    
    import re
    
    try:
        caption_lower = caption.lower()
        
        # === ADICIONAR ===
        if 'adiciona' in caption_lower:
            match = re.search(r'adiciona[:\s]+(.+)', caption, re.IGNORECASE | re.DOTALL)
            
            if match:
                texto_novo = match.group(1).strip()
                
                if file_name.lower().endswith('.docx'):
                    # Adiciona ao DOCX
                    resultado = pdf_tools.editar_docx_adicionar_texto(file_bytes, texto_novo, 'fim')
                    
                    if resultado:
                        await update.message.reply_document(
                            document=io.BytesIO(resultado),
                            filename=file_name,
                            caption="✅ Documento editado"
                        )
                    else:
                        await update.message.reply_text("❌ Erro ao editar documento")
                
                elif file_name.lower().endswith('.xlsx'):
                    # Adiciona linha ao XLSX
                    # Parse: "adiciona linha: valor1, valor2, valor3"
                    if 'linha' in caption_lower:
                        valores = [v.strip() for v in texto_novo.replace('linha:', '').split(',')]
                    else:
                        valores = [texto_novo]
                    
                    resultado = pdf_tools.editar_xlsx_adicionar_linha(file_bytes, valores)
                    
                    if resultado:
                        await update.message.reply_document(
                            document=io.BytesIO(resultado),
                            filename=file_name,
                            caption="✅ Planilha editada"
                        )
                    else:
                        await update.message.reply_text("❌ Erro ao editar planilha")
        
        # === SUBSTITUIR ===
        elif 'substitui' in caption_lower:
            match = re.search(r'substitui\s+(.+?)\s+por\s+(.+)', caption, re.IGNORECASE)
            
            if match:
                texto_antigo = match.group(1).strip()
                texto_novo = match.group(2).strip()
                
                if file_name.lower().endswith('.docx'):
                    resultado = pdf_tools.editar_docx_substituir(file_bytes, texto_antigo, texto_novo)
                    
                    if resultado:
                        docx_bytes, num_subs = resultado
                        await update.message.reply_document(
                            document=io.BytesIO(docx_bytes),
                            filename=file_name,
                            caption=f"✅ {num_subs} substituição(ões) feita(s)"
                        )
                    else:
                        await update.message.reply_text("❌ Erro ao editar documento")
                
                elif file_name.lower().endswith('.xlsx'):
                    resultado = pdf_tools.editar_xlsx_substituir(file_bytes, texto_antigo, texto_novo)
                    
                    if resultado:
                        xlsx_bytes, num_subs = resultado
                        await update.message.reply_document(
                            document=io.BytesIO(xlsx_bytes),
                            filename=file_name,
                            caption=f"✅ {num_subs} substituição(ões) feita(s)"
                        )
                    else:
                        await update.message.reply_text("❌ Erro ao editar planilha")
        
        # === REMOVER ===
        elif 'remove' in caption_lower or 'remover' in caption_lower or 'apaga' in caption_lower or 'deleta' in caption_lower:
            if file_name.lower().endswith('.xlsx'):
                # Detecta número da linha
                match = re.search(r'(?:linha|row)\s*(\d+)', caption, re.IGNORECASE)
                
                if match:
                    numero_linha = int(match.group(1))
                    resultado = pdf_tools.editar_xlsx_remover_linha(file_bytes, numero_linha)
                    
                    if resultado:
                        await update.message.reply_document(
                            document=io.BytesIO(resultado),
                            filename=file_name,
                            caption=f"✅ Linha {numero_linha} removida"
                        )
                    else:
                        await update.message.reply_text("❌ Erro ao remover linha da planilha")
                else:
                    await update.message.reply_text("❌ Especifique a linha a remover. Ex: 'remove linha 3'")
            
            elif file_name.lower().endswith('.docx'):
                # Remove parágrafo contendo texto
                match = re.search(r'(?:remove|remover|apaga|deleta)[:\s]+(.+)', caption, re.IGNORECASE | re.DOTALL)
                
                if match:
                    texto_busca = match.group(1).strip()
                    resultado = pdf_tools.editar_docx_remover_paragrafo(file_bytes, texto_busca)
                    
                    if resultado:
                        docx_bytes, num_removidos = resultado
                        await update.message.reply_document(
                            document=io.BytesIO(docx_bytes),
                            filename=file_name,
                            caption=f"✅ {num_removidos} parágrafo(s) removido(s)"
                        )
                    else:
                        await update.message.reply_text("❌ Erro ao remover do documento")
                else:
                    await update.message.reply_text("❌ Especifique o que remover. Ex: 'remove: texto a apagar'")
        
        else:
            await update.message.reply_text("❌ Comando não reconhecido. Use:\n• 'adiciona: texto'\n• 'substitui X por Y'\n• 'remove linha 3'")
    
    except Exception as e:
        logger.error(f"Erro ao editar arquivo: {e}")
        await update.message.reply_text(f"❌ Erro ao editar: {str(e)}")


# Função handle_onedrive removida - usar monitor local em vez de integração Azure OneDrive


# ============ UTILIDADES ============

def montar_resposta_documento(dados: dict, categoria: str, file_name: str) -> str:
    """Monta resposta rica para documento classificado"""
    
    tipo_doc = dados.get('tipo_documento', 'outro')
    
    if tipo_doc == 'boleto':
        resposta = "📄 *Boleto Identificado*\n\n"
        
        if dados.get('beneficiario'):
            resposta += f"🏢 {dados['beneficiario']}\n"
        
        if dados.get('valor'):
            resposta += f"💰 R$ {dados['valor']:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        if dados.get('vencimento'):
            resposta += f"📅 Vence: {dados['vencimento']}\n"
        
        if dados.get('tipo_conta'):
            tipo_display = {
                'luz': '💡 Conta de Luz',
                'agua': '💧 Conta de Água',
                'gas': '🔥 Gás',
                'internet': '🌐 Internet',
                'telefone': '📞 Telefone',
                'aluguel': '🏠 Aluguel',
                'condominio': '🏢 Condomínio',
                'cartao': '💳 Fatura Cartão'
            }.get(dados['tipo_conta'], '📄 Conta')
            resposta += f"\n{tipo_display}\n"
        
        # Código de barras clicável
        if dados.get('codigo_barras'):
            codigo = dados['codigo_barras']
            resposta += f"\n📋 Código (clique p/ copiar):\n`{codigo}`"
    
    elif tipo_doc == 'comprovante':
        resposta = "✅ *Comprovante de Pagamento*\n\n"
        
        if dados.get('valor'):
            resposta += f"💰 R$ {dados['valor']:,.2f}\n".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        if dados.get('data_pagamento'):
            resposta += f"📅 {dados['data_pagamento']}\n"
        
        if dados.get('tipo_pagamento'):
            resposta += f"💳 {dados['tipo_pagamento'].upper()}\n"
        
        if dados.get('destinatario'):
            resposta += f"👤 {dados['destinatario']}"
    
    else:
        # Documento genérico
        descricao = dados.get('descricao', file_name)
        resposta = f"📄 *Documento*\n\n{descricao}"
    
    return resposta


async def handle_planilha_entregadores(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Detecta e processa criação de planilha de entregadores"""
    
    text_lower = text.lower()
    user_id = update.effective_user.id
    
    # ===== DETECTAR CONFIRMAÇÃO DE PLANILHA PENDENTE =====
    if 'planilha_pendente' in context.user_data:
        # Verifica se é confirmação (busca O(1) com set)
        if any(palavra in text_lower for palavra in PALAVRAS_CONFIRMACAO):
            # CONFIRMOU - Criar AMBAS as planilhas
            await update.message.reply_text("✅ Confirmado! Criando planilhas...")
            
            try:
                dados_planilha = context.user_data['planilha_pendente']
                periodo = dados_planilha.get('periodo', 'Semana')
                
                # ===== VERSÃO 1: SEM NOMES (para motoboy responsável) =====
                # Converte dados para formato compatível (números ao invés de listas)
                dados_v1 = {
                    'periodo': periodo,
                    'dias': []
                }
                
                for dia_info in dados_planilha['dias']:
                    dia_v1 = dia_info.copy()
                    # Se entregadores é lista, converte para número
                    if isinstance(dia_v1['entregadores'], list):
                        dia_v1['entregadores'] = len(dia_v1['entregadores'])
                    dados_v1['dias'].append(dia_v1)
                
                xlsx_v1_bytes = pdf_tools.criar_xlsx_entregadores(
                    dados_v1,
                    custo_semana=CUSTO_ENTREGADOR_SEMANA,
                    custo_fds=CUSTO_ENTREGADOR_FDS,
                    bonus_horario=BONUS_HORARIO_FDS,
                    custo_entrega=CUSTO_POR_ENTREGA
                )
                
                if not xlsx_v1_bytes:
                    await update.message.reply_text("❌ Erro ao criar planilha Versão 1 (sem nomes)")
                    return True
                
                # ===== VERSÃO 2: COM NOMES (para Ranny) =====
                xlsx_v2_bytes = pdf_tools.criar_xlsx_entregadores_com_nomes(
                    dados_planilha,
                    custo_entrega=CUSTO_POR_ENTREGA
                )
                
                if not xlsx_v2_bytes:
                    await update.message.reply_text("❌ Erro ao criar planilha Versão 2 (com nomes)")
                    return True
                
                # ===== TÓPICO PARA VERSÃO COM NOMES =====
                topico_com_nomes = config.TOPICS.get('planilha_entregadores_com_nomes', 0)
                
                # Se não tem tópico configurado (0), verifica cache ou cria um fixo
                if not topico_com_nomes or topico_com_nomes == 0:
                    # Verifica se já criamos este tópico antes (cache em memória)
                    if 'planilha_entregadores_com_nomes' in cached_topic_ids:
                        topico_com_nomes = cached_topic_ids['planilha_entregadores_com_nomes']
                        logger.info(f"♻️ Reutilizando tópico COM NOMES do cache (ID: {topico_com_nomes})")
                    else:
                        # Cria novo tópico apenas se não existe no cache
                        try:
                            result = await context.bot.create_forum_topic(
                                chat_id=config.GROUP_ID,
                                name="📊 Planilhas COM NOMES (Ranny)"
                            )
                            topico_com_nomes = result.message_thread_id
                            # Salva no cache para próximas execuções
                            cached_topic_ids['planilha_entregadores_com_nomes'] = topico_com_nomes
                            logger.info(f"✅ Tópico criado: Planilhas COM NOMES (ID: {topico_com_nomes})")
                            logger.info(f"💡 Adicione no .env: TOPIC_PLANILHA_ENTREGADORES_COM_NOMES={topico_com_nomes}")
                        except Exception as e:
                            logger.error(f"❌ Erro ao criar tópico COM NOMES: {e}")
                            # Se falhar, envia no tópico Chat
                            topico_com_nomes = config.TOPICS['chat']
                            await update.message.reply_text(f"⚠️ Não consegui criar tópico COM NOMES, enviando no Chat")
                
                # ===== TÓPICO PARA VERSÃO SEM NOMES =====
                topico_sem_nomes = config.TOPICS.get('planilha_entregadores_sem_nomes', 0)
                
                # Se não tem tópico configurado (0), verifica cache ou cria um fixo
                if not topico_sem_nomes or topico_sem_nomes == 0:
                    # Verifica se já criamos este tópico antes (cache em memória)
                    if 'planilha_entregadores_sem_nomes' in cached_topic_ids:
                        topico_sem_nomes = cached_topic_ids['planilha_entregadores_sem_nomes']
                        logger.info(f"♻️ Reutilizando tópico SEM NOMES do cache (ID: {topico_sem_nomes})")
                    else:
                        # Cria novo tópico apenas se não existe no cache
                        try:
                            result = await context.bot.create_forum_topic(
                                chat_id=config.GROUP_ID,
                                name="📊 Planilhas SEM NOMES (Responsável)"
                            )
                            topico_sem_nomes = result.message_thread_id
                            # Salva no cache para próximas execuções
                            cached_topic_ids['planilha_entregadores_sem_nomes'] = topico_sem_nomes
                            logger.info(f"✅ Tópico criado: Planilhas SEM NOMES (ID: {topico_sem_nomes})")
                            logger.info(f"💡 Adicione no .env: TOPIC_PLANILHA_ENTREGADORES_SEM_NOMES={topico_sem_nomes}")
                        except Exception as e:
                            logger.error(f"❌ Erro ao criar tópico SEM NOMES: {e}")
                            # Se falhar, envia no tópico Chat
                            topico_sem_nomes = config.TOPICS['chat']
                            await update.message.reply_text(f"⚠️ Não consegui criar tópico SEM NOMES, enviando no Chat")
                
                # Envia VERSÃO 2 (com nomes) - para Ranny
                nome_arquivo_v2 = f"entregadores_COM_NOMES_{periodo.replace('/', '_').replace(' ', '_')}.xlsx"
                
                await context.bot.send_document(
                    chat_id=config.GROUP_ID,
                    message_thread_id=topico_com_nomes,
                    document=io.BytesIO(xlsx_v2_bytes),
                    filename=nome_arquivo_v2,
                    caption=f"📊 *Planilha COM NOMES*\n\n{periodo}\n\n✅ Versão detalhada com nomes dos entregadores!\n\n💡 Esta planilha é para você (Ranny)",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Envia VERSÃO 1 (sem nomes) - para motoboy responsável
                nome_arquivo_v1 = f"entregadores_SEM_NOMES_{periodo.replace('/', '_').replace(' ', '_')}.xlsx"
                
                await context.bot.send_document(
                    chat_id=config.GROUP_ID,
                    message_thread_id=topico_sem_nomes,
                    document=io.BytesIO(xlsx_v1_bytes),
                    filename=nome_arquivo_v1,
                    caption=f"📊 *Planilha SEM NOMES*\n\n{periodo}\n\n✅ Versão resumida por dia!\n\n💡 Esta planilha é para o responsável",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                await update.message.reply_text(
                    f"✅ *Planilhas criadas com sucesso!*\n\n"
                    f"📁 *Tópico 1:* Planilhas COM NOMES (Ranny)\n"
                    f"   → Versão detalhada com cada entregador\n\n"
                    f"📁 *Tópico 2:* Planilhas SEM NOMES (Responsável)\n"
                    f"   → Versão resumida por dia\n\n"
                    f"Ambas já estão com todas as fórmulas calculadas! 🎉",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Salva planilha COM NOMES no contexto para edições futuras
                context.user_data['ultima_planilha'] = {
                    'nome_arquivo': nome_arquivo_v2,
                    'tipo': 'entregadores',
                    'timestamp': datetime.now(),
                    'bytes': xlsx_v2_bytes,
                    'estrutura': dados_planilha,
                    'descricao_original': f"Planilha de entregadores - {periodo}",
                    'versao': 1,
                    'historico_edicoes': [{'acao': 'criacao', 'timestamp': datetime.now()}]
                }
                
                logger.info(f"✅ Planilha de entregadores salva no contexto: {nome_arquivo_v2}")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar planilhas: {e}")
                import traceback
                logger.error(traceback.format_exc())
                await update.message.reply_text(f"❌ Erro ao criar planilhas: {str(e)}")
                return True
            finally:
                # Sempre limpa dados pendentes
                context.user_data.pop('planilha_pendente', None)
        
        elif any(palavra in text_lower for palavra in PALAVRAS_NEGACAO):
            # NEGOU - Cancelar
            await update.message.reply_text(
                "❌ Planilha cancelada.\n\n"
                "Se quiser criar outra, descreva a semana novamente! 😊"
            )
            context.user_data.pop('planilha_pendente', None)
            return True
        
        # Se não é confirmação nem negação, ignora (pode ser outra conversa)
        return False
    
    # ===== DETECTAR PEDIDO DE NOVA PLANILHA =====
    # Otimizado: conta palavras-chave em uma única passagem
    palavras_encontradas = sum(1 for palavra in PALAVRAS_CHAVE_PLANILHA if palavra in text_lower)
    tem_numeros = any(char.isdigit() for char in text)
    
    if palavras_encontradas >= 2 and tem_numeros:
        # Verifica se menciona verbo de criação
        tem_verbo = any(verbo in text_lower for verbo in VERBOS_CRIACAO)
        
        if tem_verbo or 'planilha' in text_lower:
            # É pedido de planilha!
            await update.message.reply_text("⏳ Analisando dados...")
            
            try:
                # Detecta tipo de período (semanal ou mensal)
                tipo_periodo = detecta_tipo_periodo(text)
                logger.info(f"Tipo de período detectado: {tipo_periodo}")
                
                # Extrai dados com IA passando o tipo de período
                resultado = await ai.extrair_dados_entregadores(text, tipo_periodo)
                
                if not resultado['sucesso']:
                    await update.message.reply_text(
                        f"❌ Não consegui entender os dados.\n\n"
                        f"Erro: {resultado.get('erro', 'Desconhecido')}\n\n"
                        f"Tente descrever assim:\n"
                        f"'Segunda teve 3 entregadores e 20 entregas\n"
                        f"Terça teve 3 entregadores e 18 entregas\n"
                        f"...'"
                    )
                    return True
                
                dados = resultado['dados']
                
                # Valida dados e obtém alertas
                alertas = valida_dados_entregadores(dados, tipo_periodo)
                
                # Calcula totais usando função auxiliar
                total_entregas = 0
                total_custo = 0
                resumo_dias = []
                
                for dia_info in dados['dias']:
                    dia = dia_info['dia']
                    entregadores_lista = dia_info['entregadores']
                    
                    # Compatibilidade: se for lista, pega o tamanho; se for número, usa direto
                    if isinstance(entregadores_lista, list):
                        num_entregadores = len(entregadores_lista)
                    else:
                        num_entregadores = entregadores_lista
                    
                    chegaram_horario = dia_info['chegaram_horario']
                    entregas = dia_info['entregas']
                    
                    # Usa função auxiliar para calcular custos
                    custos = calcular_custo_dia(dia, num_entregadores, chegaram_horario, entregas)
                    
                    total_entregas += entregas
                    total_custo += custos['total']
                    
                    # Monta linha do resumo
                    dia_display = dia.capitalize() if '/' not in dia else dia
                    
                    if custos['is_fds'] and chegaram_horario > 0:
                        resumo_dias.append(
                            f"• {dia_display}: {num_entregadores} entregadores, "
                            f"{chegaram_horario} no horário, {entregas} entregas = R$ {custos['total']:,.2f}"
                        )
                    else:
                        resumo_dias.append(
                            f"• {dia_display}: {num_entregadores} entregadores, "
                            f"{entregas} entregas = R$ {custos['total']:,.2f}"
                        )
                
                # Monta mensagem de confirmação
                tipo_display = "SEMANA" if tipo_periodo == 'semanal' else "MÊS"
                mensagem_confirmacao = (
                    f"📊 *Entendi! Vou criar a planilha:*\n\n"
                    f"*{dados.get('periodo', tipo_display)}*\n\n"
                    f"{chr(10).join(resumo_dias)}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *TOTAL: R$ {total_custo:,.2f}*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 Resumo:\n"
                    f"• {len(dados['dias'])} dias\n"
                    f"• {total_entregas} entregas\n"
                )
                
                # Adiciona alertas se houver
                if alertas:
                    mensagem_confirmacao += f"\n⚠️ *Alertas:*\n"
                    for alerta in alertas:
                        mensagem_confirmacao += f"• {alerta}\n"
                
                mensagem_confirmacao += f"\nEstá correto? *(responda 'sim' ou 'confirma')*"
                
                # Formata valores monetários
                mensagem_confirmacao = mensagem_confirmacao.replace(',', 'X').replace('.', ',').replace('X', '.')
                
                await update.message.reply_text(mensagem_confirmacao, parse_mode=ParseMode.MARKDOWN)
                
                # Salva dados pendentes com tipo de período
                dados['tipo_periodo'] = tipo_periodo
                context.user_data['planilha_pendente'] = dados
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar planilha de entregadores: {e}")
                await update.message.reply_text(f"❌ Erro ao processar: {str(e)}")
                return True
    
    return False


# ============ PLANILHAS PERSONALIZADAS COM CONTEXTO ============

async def handle_criar_planilha_personalizada(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Cria planilha personalizada a partir de descrição natural"""
    
    text_lower = text.lower()
    
    # Detecta pedido de planilha personalizada
    # Deve ter verbo de criação + "planilha" mas NÃO "entregadores"
    tem_verbo = any(verbo in text_lower for verbo in VERBOS_CRIACAO)
    tem_planilha = 'planilha' in text_lower or 'excel' in text_lower or 'xlsx' in text_lower
    nao_entregadores = 'entregador' not in text_lower and 'entregadores' not in text_lower
    
    if tem_verbo and tem_planilha and nao_entregadores:
        await update.message.reply_text("⏳ Analisando sua solicitação...")
        
        try:
            # Salva texto original para detecção posterior
            context.user_data['texto_solicitacao_planilha'] = text
            
            # Extrai estrutura com IA
            resultado = await ai.extrair_estrutura_planilha(text)
            
            if not resultado['sucesso']:
                await update.message.reply_text(
                    f"❌ Não consegui entender a estrutura da planilha.\n\n"
                    f"Erro: {resultado.get('erro', 'Desconhecido')}\n\n"
                    f"Tente descrever assim:\n"
                    f"'Cria planilha de gastos com colunas: data, descrição, valor, categoria'"
                )
                return True
            
            estrutura = resultado['estrutura']
            
            # Monta mensagem de confirmação
            colunas_desc = []
            if 'colunas' not in estrutura or not estrutura['colunas']:
                await update.message.reply_text("❌ Erro: estrutura sem colunas definidas")
                return True
            
            for idx, col in enumerate(estrutura['colunas'], 1):
                tipo_emoji = {
                    'texto': '📝',
                    'numero': '🔢',
                    'moeda': '💰',
                    'data': '📅',
                    'porcentagem': '📊'
                }.get(col['tipo'], '📋')
                colunas_desc.append(f"{idx}. {tipo_emoji} {col['nome']} ({col['tipo']})")
            
            mensagem = (
                f"📊 *Entendi! Vou criar:*\n\n"
                f"*{estrutura.get('titulo', 'Planilha')}*\n\n"
                f"*Colunas:*\n"
                f"{chr(10).join(colunas_desc)}\n\n"
            )
            
            if estrutura.get('tem_total'):
                mensagem += f"✅ Com linha de TOTAL\n\n"
            
            mensagem += f"Quer que eu adicione dados de exemplo? *(responda 'sim' ou 'não')*"
            
            await update.message.reply_text(mensagem, parse_mode=ParseMode.MARKDOWN)
            
            # Salva estrutura pendente
            context.user_data['planilha_personalizada_pendente'] = estrutura
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar planilha personalizada: {e}")
            await update.message.reply_text(f"❌ Erro ao processar: {str(e)}")
            return True
    
    # Verifica se é confirmação de planilha personalizada pendente
    if 'planilha_personalizada_pendente' in context.user_data:
        if any(palavra in text_lower for palavra in PALAVRAS_CONFIRMACAO):
            # CONFIRMOU - Criar planilha
            await update.message.reply_text("✅ Criando planilha...")
            
            try:
                estrutura = context.user_data['planilha_personalizada_pendente']
                
                # Usa dados de exemplo se houver
                dados = estrutura.get('dados_exemplo', [])
                
                # Cria planilha
                xlsx_bytes = pdf_tools.criar_xlsx_estruturada(estrutura, dados)
                
                if not xlsx_bytes:
                    await update.message.reply_text("❌ Erro ao criar planilha")
                    return True
                
                # Nome do arquivo
                titulo = estrutura.get('titulo', 'planilha')
                nome_arquivo = titulo.lower().replace(' ', '_')[:30] + '.xlsx'
                
                # Detecta se é planilha pessoal
                texto_original = context.user_data.get('texto_solicitacao_planilha', '')
                eh_pessoal = is_planilha_pessoal(texto_original, titulo)
                
                # Prepara caption
                caption = f"📊 *{titulo}*\n\n✅ Planilha criada com sucesso!\n\n💾 Salva no contexto por 2 horas\n💡 Você pode adicionar dados dizendo: 'Adiciona: valor1, valor2, ...'"
                
                if eh_pessoal:
                    # Planilha PESSOAL - envia no tópico Pessoal
                    topico_pessoal = config.TOPICS.get('pessoal', 0)
                    
                    if topico_pessoal and topico_pessoal != 0:
                        # Envia no tópico Pessoal
                        await context.bot.send_document(
                            chat_id=config.GROUP_ID,
                            message_thread_id=topico_pessoal,
                            document=io.BytesIO(xlsx_bytes),
                            filename=nome_arquivo,
                            caption=f"{caption}\n\n📁 *Salvo no tópico: Pessoal*",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        
                        # Confirma no chat onde foi solicitado
                        await update.message.reply_text(
                            f"✅ Planilha pessoal criada!\n\n"
                            f"📁 Enviada para o tópico *Pessoal*\n"
                            f"📊 Arquivo: {nome_arquivo}",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        
                        logger.info(f"✅ Planilha PESSOAL enviada para tópico Pessoal: {nome_arquivo}")
                    else:
                        # Fallback: envia no mesmo tópico
                        await update.message.reply_document(
                            document=io.BytesIO(xlsx_bytes),
                            filename=nome_arquivo,
                            caption=caption,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        logger.warning(f"⚠️ Tópico Pessoal não configurado, enviando no mesmo tópico")
                else:
                    # Planilha NÃO-PESSOAL - envia no mesmo tópico (comportamento original)
                    await update.message.reply_document(
                        document=io.BytesIO(xlsx_bytes),
                        filename=nome_arquivo,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    logger.info(f"✅ Planilha criada e enviada no mesmo tópico: {nome_arquivo}")
                
                # Salva no contexto para edições futuras
                context.user_data['ultima_planilha'] = {
                    'nome_arquivo': nome_arquivo,
                    'tipo': 'personalizada',
                    'eh_pessoal': eh_pessoal,
                    'timestamp': datetime.now(),
                    'bytes': xlsx_bytes,
                    'estrutura': estrutura,
                    'descricao_original': context.user_data.get('planilha_personalizada_pendente', {}).get('titulo', ''),
                    'versao': 1,
                    'historico_edicoes': [{'acao': 'criacao', 'timestamp': datetime.now()}]
                }
                
                logger.info(f"✅ Planilha personalizada salva no contexto: {nome_arquivo} (pessoal={eh_pessoal})")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar planilha: {e}")
                await update.message.reply_text(f"❌ Erro ao criar planilha: {str(e)}")
                return True
            finally:
                context.user_data.pop('planilha_personalizada_pendente', None)
        
        elif any(palavra in text_lower for palavra in PALAVRAS_NEGACAO):
            # NEGOU - Cancelar
            await update.message.reply_text("❌ Planilha cancelada.")
            context.user_data.pop('planilha_personalizada_pendente', None)
            return True
    
    return False


async def handle_editar_planilha_contexto(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Edita planilha usando contexto (sem precisar enviar arquivo)"""
    
    text_lower = text.lower()
    
    # Verifica se tem planilha no contexto
    if 'ultima_planilha' not in context.user_data:
        return False
    
    # Detecta comandos de edição
    tem_adicionar = any(palavra in text_lower for palavra in PALAVRAS_ADICIONAR)
    tem_editar = any(palavra in text_lower for palavra in PALAVRAS_EDITAR)
    tem_remover = any(palavra in text_lower for palavra in PALAVRAS_REMOVER)
    
    if not (tem_adicionar or tem_editar or tem_remover):
        return False
    
    # Verifica se planilha não expirou (2 horas)
    planilha_ctx = context.user_data['ultima_planilha']
    tempo_decorrido = datetime.now() - planilha_ctx['timestamp']
    if tempo_decorrido.total_seconds() > 7200:  # 2 horas
        await update.message.reply_text(
            "⏰ A planilha anterior expirou (mais de 2 horas).\n\n"
            "Envie o arquivo novamente ou crie uma nova planilha."
        )
        context.user_data.pop('ultima_planilha', None)
        return True
    
    await update.message.reply_text("⏳ Interpretando sua solicitação...")
    
    try:
        # Interpreta edição com IA
        estrutura = planilha_ctx['estrutura']
        resultado = await ai.interpretar_edicao_planilha(text, estrutura)
        
        if not resultado['sucesso']:
            await update.message.reply_text(
                f"❌ Não consegui entender a edição.\n\n"
                f"Erro: {resultado.get('erro', 'Desconhecido')}\n\n"
                f"Tente comandos como:\n"
                f"• 'Adiciona: valor1, valor2, ...'\n"
                f"• 'Muda o valor da linha 2 para 100'\n"
                f"• 'Remove a última linha'"
            )
            return True
        
        acao = resultado['acao']
        parametros = resultado['parametros']
        
        # Aplica edição na planilha
        xlsx_bytes = planilha_ctx['bytes']
        estrutura = planilha_ctx['estrutura']
        
        resultado_edicao = pdf_tools.aplicar_edicao_planilha(xlsx_bytes, acao, parametros, estrutura)
        
        if not resultado_edicao:
            await update.message.reply_text(
                f"❌ Erro ao aplicar edição.\n\n"
                f"Verifique se os parâmetros estão corretos e tente novamente."
            )
            return True
        
        xlsx_modificado, mensagem_sucesso = resultado_edicao
        
        # Atualiza contexto
        planilha_ctx['bytes'] = xlsx_modificado
        planilha_ctx['versao'] = planilha_ctx.get('versao', 1) + 1
        planilha_ctx['timestamp'] = datetime.now()
        planilha_ctx['historico_edicoes'].append({
            'acao': acao,
            'timestamp': datetime.now(),
            'parametros': parametros
        })
        
        # Envia planilha atualizada
        nome_arquivo = planilha_ctx['nome_arquivo']
        titulo = estrutura.get('titulo', 'Planilha')
        
        await update.message.reply_document(
            document=io.BytesIO(xlsx_modificado),
            filename=nome_arquivo,
            caption=f"📊 *{titulo}* (v{planilha_ctx['versao']})\n\n{mensagem_sucesso}\n\n💡 Você pode continuar editando por mais 2 horas.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"✅ Edição aplicada: {acao}, versão {planilha_ctx['versao']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao editar planilha: {e}")
        await update.message.reply_text(f"❌ Erro ao processar edição: {str(e)}")
        return True


# ============ MAIN ============

async def main():
    """Função principal"""
    
    # Verifica variáveis de ambiente
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN não configurado!")
        return
    
    if not config.GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY não configurado!")
        return
    
    logger.info("=" * 60)
    logger.info("🤖 ASSISTENTE RANNY V3")
    logger.info("=" * 60)
    
    # Testa conexão com banco
    if not db.test_connection():
        logger.error("❌ Erro ao conectar com Supabase!")
        return
    
    logger.info("✅ Supabase conectado")
    
    # Roda migração PostgreSQL se necessário
    if os.getenv('DATABASE_URL'):
        logger.info("🔄 Verificando migração PostgreSQL...")
        try:
            # Importa e roda migração diretamente
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            import migrar_para_postgres
            logger.info("✅ Migração concluída")
        except Exception as e:
            logger.warning(f"⚠️ Erro na migração: {e}")
    
    # Cria application
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Configura bot para jobs
    jobs.set_telegram_bot(app.bot)
    
    # Adiciona handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Handlers de mídia
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Handler de texto (deve ser o último)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("✅ Handlers configurados")
    
    # Inicia scheduler
    scheduler.start_scheduler()
    
    # Configura jobs
    from scheduler import add_interval_job, add_cron_job
    
    # Job de lembretes (verifica a cada minuto)
    add_interval_job(
        jobs.check_lembretes,
        job_id='lembretes',
        minutes=1
    )
    
    # Job de alertas de vencimento (todo dia às 8h)
    add_cron_job(
        jobs.check_vencimentos,
        job_id='vencimentos',
        hour=8,
        minute=0
    )
    
    # Job de resumo semanal (domingo às 20h)
    add_cron_job(
        jobs.resumo_semanal,
        job_id='resumo_semanal',
        hour=20,
        minute=0,
        day_of_week='sun'
    )
    
    # Job de keep-alive (a cada 10 minutos para evitar sleep no Render/Railway)
    add_interval_job(
        jobs.keep_alive,
        job_id='keep_alive',
        minutes=10
    )
    
    logger.info("✅ Jobs agendados (incluindo keep-alive)")
    
    # Inicia servidor web
    from web import app as web_app
    import uvicorn
    
    async def run_web():
        """Roda servidor FastAPI"""
        config_uvicorn = uvicorn.Config(
            web_app,
            host="0.0.0.0",
            port=config.PORT,
            log_level="warning"
        )
        server = uvicorn.Server(config_uvicorn)
        await server.serve()
    
    # Inicia bot
    async def run_bot():
        """Roda bot Telegram"""
        async with app:
            await app.start()
            await app.updater.start_polling(
                drop_pending_updates=True,
                poll_interval=1.0,
                timeout=20
            )
            
            logger.info("✅ Bot online!")
            logger.info(f"✅ Servidor web: http://localhost:{config.PORT}")
            logger.info(f"✅ Health check: {config.BASE_URL}/health")
            logger.info("")
            logger.info("Pressione Ctrl+C para parar")
            
            # Aguarda indefinidamente
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            
            await app.updater.stop()
            await app.stop()
    
    # Roda bot e web em paralelo
    try:
        await asyncio.gather(
            run_bot(),
            run_web()
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Encerrando...")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
    finally:
        scheduler.stop_scheduler()


if __name__ == '__main__':
    asyncio.run(main())
