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
PALAVRAS_CHAVE_PLANILHA = {'planilha', 'entregador', 'entregadores', 'semana', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'sabado', 'domingo'}
VERBOS_CRIACAO = {'cria', 'criar', 'faz', 'fazer', 'gera', 'gerar', 'monta', 'montar'}


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
        dia: Nome do dia da semana
        entregadores: Número de entregadores escalados
        chegaram_horario: Quantos chegaram até 18:10h
        entregas: Total de entregas realizadas
    
    Returns:
        dict com: custo_entregadores, bonus_horario, custo_entregas, total
    """
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
        
        # ===== BUSCA DE DOCUMENTOS =====
        if await handle_busca_documentos(update, context, text):
            return
        
        # ===== REENVIO DE DOCUMENTO =====
        if await handle_reenvio_documento(update, context, text, user_id):
            return
        
        # ===== RELATÓRIOS =====
        if await handle_relatorios(update, context, text):
            return
        
        # ===== CRIAÇÃO DE ARQUIVOS =====
        if await handle_criar_arquivo(update, context, text):
            return
        
        # ===== PLANILHA DE ENTREGADORES =====
        if await handle_planilha_entregadores(update, context, text):
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


async def handle_busca_documentos(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Detecta e processa busca de documentos"""
    
    text_lower = text.lower()
    user_id = update.effective_user.id
    
    # Padrões de busca (expandidos)
    padroes_busca = [
        'cadê', 'cade', 'onde está', 'onde esta', 'onde tá', 'onde ta',
        'acha', 'procura', 'busca', 'tem algum', 'você tem', 
        'quantos', 'total', 'quanto',
        'cite', 'lista', 'listar', 'mostra', 'mostrar', 'mostre',
        'quais', 'todos', 'tudo', 'qual', 'me dá', 'me da'
    ]
    
    if any(padrao in text_lower for padrao in padroes_busca):
        
        # ===== PERGUNTA SOBRE QUANTIDADE/TOTAL =====
        if any(palavra in text_lower for palavra in ['quantos', 'total', 'quanto']) and 'nome' not in text_lower:
            await update.message.reply_text("📊 Contando documentos...")
            
            try:
                # Busca estatísticas do banco
                stats = db.contar_documentos_por_categoria()
                total = stats.get('total', 0)
                por_categoria = stats.get('por_categoria', {})
                
                if total == 0:
                    await update.message.reply_text("📭 Ainda não há documentos salvos no banco.")
                    return True
                
                # Monta resposta com números reais
                resposta = f"📊 **Total: {total} documento(s) salvos**\n\n"
                resposta += "📁 **Por categoria:**\n"
                
                # Ordena por quantidade (maior primeiro)
                categorias_ordenadas = sorted(por_categoria.items(), key=lambda x: x[1], reverse=True)
                
                for categoria, count in categorias_ordenadas:
                    emoji = {
                        'empresa': '🏢',
                        'financeiro': '💰',
                        'funcionarios': '👥',
                        'juridico': '⚖️',
                        'pessoal': '👤',
                        'operacional': '🔧',
                        'midia': '📸',
                        'controles': '📊',
                        'outros': '📎'
                    }.get(categoria, '📄')
                    
                    resposta += f"{emoji} {categoria.title()}: **{count}**\n"
                
                resposta += f"\n💡 Dica: Pergunte 'lista todos' para ver os nomes!"
                
                await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
                return True
                
            except Exception as e:
                logger.error(f"Erro ao contar documentos: {e}")
                await update.message.reply_text("❌ Erro ao contar documentos. Tente novamente.")
                return True
        
        # ===== LISTAR TODOS OS DOCUMENTOS =====
        if any(palavra in text_lower for palavra in ['todos', 'tudo', 'lista', 'cite', 'quais', 'nome de todos', 'nomes']):
            # Verifica se não é uma busca específica (ex: "todos os contratos")
            palavras_especificas = ['contrato', 'boleto', 'nota', 'comprovante', 'pdf', 'excel', 'word']
            tem_termo_especifico = any(palavra in text_lower for palavra in palavras_especificas)
            
            # Se não tem termo específico, lista TODOS
            if not tem_termo_especifico:
                logger.info(f"📋 LISTANDO TODOS OS DOCUMENTOS")
                await update.message.reply_text("📋 Listando todos os documentos...")
                
                try:
                    logger.info(f"📊 Consultando banco de dados...")
                    
                    # Busca TODOS os documentos com timeout
                    documentos = await asyncio.wait_for(
                        asyncio.to_thread(db.buscar_documentos, termo='', limit=100),
                        timeout=10.0
                    )
                    
                    logger.info(f"✅ Busca concluída: {len(documentos)} documento(s) encontrado(s)")
                    
                    if not documentos:
                        await update.message.reply_text("📭 Ainda não há documentos salvos.")
                        return True
                    
                    # Salva resultados para reenvio
                    user_search_results[user_id] = documentos
                    
                    # Agrupa por categoria
                    por_categoria = {}
                    for doc in documentos:
                        cat = doc.get('categoria', 'outros')
                        if cat not in por_categoria:
                            por_categoria[cat] = []
                        por_categoria[cat].append(doc)
                    
                    # Monta resposta agrupada
                    resposta = f"📁 **Total: {len(documentos)} documento(s)**\n\n"
                    
                    numero = 1
                    for categoria in sorted(por_categoria.keys()):
                        docs = por_categoria[categoria]
                        
                        emoji = {
                            'empresa': '🏢',
                            'financeiro': '💰',
                            'funcionarios': '👥',
                            'juridico': '⚖️',
                            'pessoal': '👤',
                            'operacional': '🔧',
                            'midia': '📸',
                            'controles': '📊',
                            'outros': '📎'
                        }.get(categoria, '📄')
                        
                        resposta += f"{emoji} **{categoria.title()}** ({len(docs)}):\n"
                        
                        for doc in docs:
                            nome = doc.get('descricao', 'Sem nome')
                            # Limita tamanho do nome
                            if len(nome) > 40:
                                nome = nome[:37] + "..."
                            # Escapa caracteres especiais do Markdown
                            nome = escape_markdown(nome)
                            resposta += f"{numero}. {nome}\n"
                            numero += 1
                        
                        resposta += "\n"
                    
                    resposta += "💡 Quer que eu te mande algum? Diz o número (ex: 'manda o 1')"
                    
                    logger.info(f"📤 Enviando resposta com {len(documentos)} documentos")
                    await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
                    logger.info(f"✅ Resposta enviada com sucesso!")
                    return True
                    
                except asyncio.TimeoutError:
                    logger.error(f"⏱️ TIMEOUT ao listar todos os documentos após 10s")
                    await update.message.reply_text("⏱️ A busca está demorando muito. Tente novamente.")
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ ERRO ao listar documentos: {e}", exc_info=True)
                    await update.message.reply_text(f"❌ Erro ao listar documentos: {str(e)}")
                    return True
        
        # ===== BUSCA POR TERMO ESPECÍFICO =====
        # Extrai termo de busca (melhorado)
        termo = text_lower
        
        # Remove apenas palavras de busca, não palavras importantes
        # Usa regex com word boundaries para evitar remover partes de palavras
        import re
        palavras_remover = [
            r'\bcadê\b', r'\bcade\b', r'\bonde está\b', r'\bonde esta\b', r'\bonde tá\b', r'\bonde ta\b',
            r'\bprocura\b', r'\bbusca\b', r'\bbuscar\b', r'\bacha\b', r'\bachar\b',
            r'\bvocê tem\b', r'\btem algum\b',
            r'\bmostra\b', r'\bmostre\b', r'\bme dá\b', r'\bme da\b',
            r'\bo\b', r'\ba\b', r'\bos\b', r'\bas\b', r'\bum\b', r'\buma\b', r'\bde\b', r'\bdo\b', r'\bda\b',
            r'\bguardados\b', r'\bsalvos\b', r'\barquivos\b', r'\bdocumentos\b'
        ]
        
        for pattern in palavras_remover:
            termo = re.sub(pattern, ' ', termo, flags=re.IGNORECASE)
        
        termo = ' '.join(termo.split())  # Remove espaços extras
        
        if len(termo) < 3:
            return False  # Termo muito curto
        
        logger.info(f"🔍 INICIANDO BUSCA: termo='{termo}'")
        await update.message.reply_text("🔍 Buscando...")
        
        # Busca no banco com timeout
        documentos = []
        try:
            logger.info(f"📊 Consultando banco de dados...")
            
            # Adiciona timeout de 10 segundos
            documentos = await asyncio.wait_for(
                asyncio.to_thread(db.buscar_documentos, termo, limit=50),
                timeout=10.0
            )
            
            logger.info(f"✅ Busca concluída: {len(documentos)} documento(s) encontrado(s)")
            
        except asyncio.TimeoutError:
            logger.error(f"⏱️ TIMEOUT na busca após 10s: termo='{termo}'")
            await update.message.reply_text("⏱️ A busca está demorando muito. Tente um termo mais específico ou tente novamente.")
            return True
            
        except Exception as e:
            logger.error(f"❌ ERRO NA BUSCA: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Erro ao buscar: {str(e)}")
            return True
        
        # Se não encontrou nada
        if not documentos:
            resposta = f"❌ Não encontrei documentos com **'{termo}'**\n\n"
            resposta += "💡 Tente:\n"
            resposta += "• Usar palavras-chave diferentes\n"
            resposta += "• Verificar a ortografia\n"
            resposta += "• Perguntar 'lista todos' para ver todos os arquivos"
            
            await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
            return True
        
        # Salva resultados para reenvio
        user_search_results[user_id] = documentos
        
        # Monta resposta
        resposta = f"📁 **Encontrei {len(documentos)} documento(s):**\n\n"
        
        for i, doc in enumerate(documentos[:10], 1):
            nome = doc.get('descricao', 'Sem descrição')
            # Escapa caracteres especiais do Markdown
            nome = escape_markdown(nome)
            
            resposta += f"{i}. 📄 {nome}\n"
            resposta += f"   📂 {doc.get('categoria', 'outros').title()}\n"
            
            # Link para a mensagem original (se tiver message_id)
            if doc.get('message_id'):
                link = f"https://t.me/c/{str(config.GROUP_ID)[4:]}/{doc['message_id']}"
                resposta += f"   🔗 [Ver mensagem]({link})\n"
            
            resposta += "\n"
        
        if len(documentos) > 10:
            resposta += f"_... e mais {len(documentos) - 10} documento(s)_\n\n"
        
        resposta += "💡 Quer que eu te mande algum? Diz o número (ex: 'manda o 1')"
        
        logger.info(f"📤 Enviando resposta com {len(documentos)} documentos encontrados")
        await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"✅ Resposta enviada com sucesso!")
        return True
    
    return False


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
                resposta += f"📋 {resultado['num_planilhas']} planilha(s)\n\n"
                
                # Mostra primeiras linhas
                texto = resultado['texto'][:1000]
                resposta += f"```\n{texto}\n```"
                
                if len(resultado['texto']) > 1000:
                    resposta += f"\n\n_...conteúdo truncado_"
                
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
        
        else:
            await update.message.reply_text("❌ Comando não reconhecido. Use:\n• 'adiciona: texto'\n• 'substitui X por Y'")
    
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
            # CONFIRMOU - Criar planilha
            await update.message.reply_text("✅ Confirmado! Criando planilha...")
            
            try:
                dados_planilha = context.user_data['planilha_pendente']
                
                # Cria Excel
                xlsx_bytes = pdf_tools.criar_xlsx_entregadores(
                    dados_planilha,
                    custo_semana=CUSTO_ENTREGADOR_SEMANA,
                    custo_fds=CUSTO_ENTREGADOR_FDS,
                    bonus_horario=BONUS_HORARIO_FDS,
                    custo_entrega=CUSTO_POR_ENTREGA
                )
                
                if not xlsx_bytes:
                    await update.message.reply_text("❌ Erro ao criar planilha Excel")
                    return True
                
                # Usa tópico fixo ou cria na primeira vez
                periodo = dados_planilha.get('periodo', 'Semana')
                topico_id = config.TOPICS.get('planilha_entregadores', 0)
                
                # Se não tem tópico configurado (0), cria um fixo
                if not topico_id or topico_id == 0:
                    try:
                        result = await context.bot.create_forum_topic(
                            chat_id=config.GROUP_ID,
                            name="📊 Planilha dos Entregadores"
                        )
                        topico_id = result.message_thread_id
                        logger.info(f"✅ Tópico criado: Planilha dos Entregadores (ID: {topico_id})")
                        logger.info(f"💡 Adicione no .env: TOPIC_PLANILHA_ENTREGADORES={topico_id}")
                    except Exception as e:
                        logger.error(f"❌ Erro ao criar tópico: {e}")
                        # Se falhar, envia no tópico Chat
                        topico_id = config.TOPICS['chat']
                        await update.message.reply_text(f"⚠️ Não consegui criar tópico, enviando no Chat")
                
                # Envia planilha no tópico fixo
                nome_arquivo = f"entregadores_{periodo.replace('/', '_').replace(' ', '_')}.xlsx"
                
                await context.bot.send_document(
                    chat_id=config.GROUP_ID,
                    message_thread_id=topico_id,
                    document=io.BytesIO(xlsx_bytes),
                    filename=nome_arquivo,
                    caption=f"📊 *Planilha de Entregadores*\n\n{periodo}\n\n✅ Planilha criada automaticamente pelo bot!",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                await update.message.reply_text(
                    f"✅ *Planilha criada com sucesso!*\n\n"
                    f"📁 Tópico: Planilha dos Entregadores\n"
                    f"📊 Arquivo: {nome_arquivo}\n\n"
                    f"A planilha já está com todas as fórmulas calculadas! 🎉",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Erro ao criar planilha: {e}")
                await update.message.reply_text(f"❌ Erro ao criar planilha: {str(e)}")
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
            await update.message.reply_text("⏳ Analisando dados da semana...")
            
            try:
                # Extrai dados com IA
                resultado = await ai.extrair_dados_entregadores(text)
                
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
                
                # Calcula totais usando função auxiliar
                total_entregas = 0
                total_custo = 0
                resumo_dias = []
                
                for dia_info in dados['dias']:
                    dia = dia_info['dia']
                    entregadores = dia_info['entregadores']
                    chegaram_horario = dia_info['chegaram_horario']
                    entregas = dia_info['entregas']
                    
                    # Usa função auxiliar para calcular custos
                    custos = calcular_custo_dia(dia, entregadores, chegaram_horario, entregas)
                    
                    total_entregas += entregas
                    total_custo += custos['total']
                    
                    # Monta linha do resumo
                    if custos['is_fds'] and chegaram_horario > 0:
                        resumo_dias.append(
                            f"• {dia.capitalize()}: {entregadores} entregadores, "
                            f"{chegaram_horario} no horário, {entregas} entregas = R$ {custos['total']:,.2f}"
                        )
                    else:
                        resumo_dias.append(
                            f"• {dia.capitalize()}: {entregadores} entregadores, "
                            f"{entregas} entregas = R$ {custos['total']:,.2f}"
                        )
                
                # Monta mensagem de confirmação
                mensagem_confirmacao = (
                    f"📊 *Entendi! Vou criar a planilha:*\n\n"
                    f"*{dados.get('periodo', 'Semana')}*\n\n"
                    f"{chr(10).join(resumo_dias)}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *TOTAL DA SEMANA: R$ {total_custo:,.2f}*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 Resumo:\n"
                    f"• {len(dados['dias'])} dias\n"
                    f"• {total_entregas} entregas\n\n"
                    f"Está correto? *(responda 'sim' ou 'confirma')*"
                )
                
                # Formata valores monetários
                mensagem_confirmacao = mensagem_confirmacao.replace(',', 'X').replace('.', ',').replace('X', '.')
                
                await update.message.reply_text(mensagem_confirmacao, parse_mode=ParseMode.MARKDOWN)
                
                # Salva dados pendentes
                context.user_data['planilha_pendente'] = dados
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar planilha de entregadores: {e}")
                await update.message.reply_text(f"❌ Erro ao processar: {str(e)}")
                return True
    
    return False


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
