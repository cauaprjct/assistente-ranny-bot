"""
Parser de datas em português para o sistema de lembretes

Suporta padrões como:
- amanhã, hoje, depois de amanhã
- segunda, terça, quarta, quinta, sexta, sábado, domingo
- próxima semana, próximo mês
- daqui 3 dias, daqui uma semana
- daqui 5 minutos, daqui 1 hora
- dia 15, dia 7
- 15/01, 15/01/2025

Requirements: 3.1, 3.2
"""

import re
from datetime import datetime, date, timedelta
from typing import Optional, Tuple, Dict

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# Fuso horário de Brasília
TIMEZONE_BR = ZoneInfo('America/Sao_Paulo')


def agora_brasil() -> datetime:
    """Retorna datetime atual no fuso horário de Brasília"""
    return datetime.now(TIMEZONE_BR)


def hoje_brasil() -> date:
    """Retorna data atual no fuso horário de Brasília"""
    return agora_brasil().date()


def parse_lembrete(texto: str) -> Dict[str, str]:
    """
    Extrai data, hora e descrição de um pedido de lembrete.
    
    Args:
        texto: Texto do pedido de lembrete (ex: "me lembra amanhã às 14h de pagar FGTS")
    
    Returns:
        dict com:
            - data: string no formato YYYY-MM-DD
            - hora: string no formato HH:MM (padrão 09:00)
            - descricao: texto limpo sem palavras de data/hora
    
    Property 5: Se hora não especificada, usa 09:00
    """
    texto_original = texto
    texto_lower = texto.lower()
    
    # 0. Verificar padrões relativos de tempo (daqui X minutos/horas)
    resultado_relativo = extrair_tempo_relativo(texto_lower)
    if resultado_relativo:
        data, hora, texto_lower = resultado_relativo
        descricao = limpar_descricao(texto_lower)
        if not descricao.strip():
            descricao = limpar_descricao(texto_original.lower())
        return {
            'data': data,
            'hora': hora,
            'descricao': descricao.strip()
        }
    
    # 1. Extrair data PRIMEIRO (para não confundir "dia 15" com hora)
    data, texto_lower = extrair_data(texto_lower)
    
    # 2. Extrair hora (se presente)
    hora, texto_lower = extrair_hora(texto_lower)
    
    # 3. Limpar descrição
    descricao = limpar_descricao(texto_lower)
    
    # Se descrição ficou vazia, usar texto original limpo
    if not descricao.strip():
        descricao = limpar_descricao(texto_original.lower())
    
    return {
        'data': data,
        'hora': hora,
        'descricao': descricao.strip()
    }


def extrair_tempo_relativo(texto: str) -> Optional[Tuple[str, str, str]]:
    """
    Extrai tempo relativo como "daqui X minutos" ou "daqui X horas".
    
    Args:
        texto: Texto do pedido
    
    Returns:
        Tuple[data YYYY-MM-DD, hora HH:MM, texto_restante] ou None se não encontrar
    """
    agora = agora_brasil()
    
    # Padrão: daqui X minuto(s)
    match = re.search(r'daqui\s+(?:a\s+)?(\d+)\s+minutos?', texto)
    if match:
        minutos = int(match.group(1))
        futuro = agora + timedelta(minutes=minutos)
        texto = texto[:match.start()] + texto[match.end():]
        return futuro.strftime('%Y-%m-%d'), futuro.strftime('%H:%M'), texto
    
    # Padrão: daqui um/1 minuto
    match = re.search(r'daqui\s+(?:a\s+)?(?:um?|1)\s+minutos?', texto)
    if match:
        futuro = agora + timedelta(minutes=1)
        texto = texto[:match.start()] + texto[match.end():]
        return futuro.strftime('%Y-%m-%d'), futuro.strftime('%H:%M'), texto
    
    # Padrão: daqui X hora(s)
    match = re.search(r'daqui\s+(?:a\s+)?(\d+)\s+horas?', texto)
    if match:
        horas = int(match.group(1))
        futuro = agora + timedelta(hours=horas)
        texto = texto[:match.start()] + texto[match.end():]
        return futuro.strftime('%Y-%m-%d'), futuro.strftime('%H:%M'), texto
    
    # Padrão: daqui uma/1 hora
    match = re.search(r'daqui\s+(?:a\s+)?(?:uma?|1)\s+horas?', texto)
    if match:
        futuro = agora + timedelta(hours=1)
        texto = texto[:match.start()] + texto[match.end():]
        return futuro.strftime('%Y-%m-%d'), futuro.strftime('%H:%M'), texto
    
    # Padrão: daqui meia hora
    match = re.search(r'daqui\s+(?:a\s+)?meia\s+hora', texto)
    if match:
        futuro = agora + timedelta(minutes=30)
        texto = texto[:match.start()] + texto[match.end():]
        return futuro.strftime('%Y-%m-%d'), futuro.strftime('%H:%M'), texto
    
    return None


def extrair_hora(texto: str) -> Tuple[str, str]:
    """
    Extrai hora do texto e retorna (hora, texto_sem_hora).
    
    Padrões suportados:
    - às 14h, às 14:30, as 14h30
    - 14 horas, 14h
    - de manhã (09:00), à tarde (14:00), à noite (20:00)
    - meio-dia (12:00), meia-noite (00:00)
    
    Returns:
        Tuple[hora no formato HH:MM, texto com hora removida]
        Se não encontrar hora, retorna ('09:00', texto_original)
    """
    hora_padrao = '09:00'
    
    # Padrão: às 14h30, às 14:30, as 14h, às 14 horas
    # Requer "às" ou "as" como palavra separada (não parte de outra palavra)
    match = re.search(r'(?:^|[\s,])([àa]s)\s+(\d{1,2})\s*[h:]?\s*(\d{2})?\s*(?:horas?)?', texto)
    if match:
        h = int(match.group(2))
        m = int(match.group(3)) if match.group(3) else 0
        if 0 <= h <= 23 and 0 <= m <= 59:
            texto = texto[:match.start()] + texto[match.end():]
            return f'{h:02d}:{m:02d}', texto
    
    # Padrão: 14h30, 14h, 14:30 (sem "às") - mas NÃO captura "dia 15" ou números soltos
    # Requer que tenha 'h' ou ':' explicitamente
    match = re.search(r'(?<!\bdia\s)(?<!\d)(\d{1,2})\s*[h:]\s*(\d{2})?\b', texto)
    if match:
        h = int(match.group(1))
        m = int(match.group(2)) if match.group(2) else 0
        if 0 <= h <= 23 and 0 <= m <= 59:
            texto = texto[:match.start()] + texto[match.end():]
            return f'{h:02d}:{m:02d}', texto
    
    # Padrão: de manhã, pela manhã
    if re.search(r'(?:de|pela)\s+manh[aã]', texto):
        texto = re.sub(r'(?:de|pela)\s+manh[aã]', '', texto)
        return '09:00', texto
    
    # Padrão: à tarde, de tarde, pela tarde
    if re.search(r'(?:[àa]|de|pela)\s+tarde', texto):
        texto = re.sub(r'(?:[àa]|de|pela)\s+tarde', '', texto)
        return '14:00', texto
    
    # Padrão: à noite, de noite, pela noite
    if re.search(r'(?:[àa]|de|pela)\s+noite', texto):
        texto = re.sub(r'(?:[àa]|de|pela)\s+noite', '', texto)
        return '20:00', texto
    
    # Padrão: meio-dia, ao meio-dia
    if re.search(r'(?:ao\s+)?meio[- ]?dia', texto):
        texto = re.sub(r'(?:ao\s+)?meio[- ]?dia', '', texto)
        return '12:00', texto
    
    # Padrão: meia-noite
    if re.search(r'meia[- ]?noite', texto):
        texto = re.sub(r'meia[- ]?noite', '', texto)
        return '00:00', texto
    
    return hora_padrao, texto


def extrair_data(texto: str) -> Tuple[str, str]:
    """
    Extrai data do texto e retorna (data, texto_sem_data).
    
    Padrões suportados (em ordem de prioridade):
    - Data completa: 15/01/2025, 15-01-2025
    - Data parcial: 15/01, 15-01
    - Dia do mês: dia 15, no dia 7
    - Relativos: amanhã, hoje, depois de amanhã
    - Dias da semana: segunda, terça, etc.
    - Próxima: próxima semana, próximo mês
    - Daqui: daqui 3 dias, daqui uma semana
    
    Returns:
        Tuple[data no formato YYYY-MM-DD, texto com data removida]
        Se não encontrar data, retorna (amanhã, texto_original)
    """
    hoje = hoje_brasil()
    
    # Padrão: data completa DD/MM/YYYY ou DD-MM-YYYY
    match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})', texto)
    if match:
        dia, mes, ano = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if ano < 100:
            ano += 2000
        try:
            data = date(ano, mes, dia)
            texto = texto[:match.start()] + texto[match.end():]
            return data.strftime('%Y-%m-%d'), texto
        except ValueError:
            pass
    
    # Padrão: data parcial DD/MM ou DD-MM
    match = re.search(r'(\d{1,2})[/\-](\d{1,2})(?!\d)', texto)
    if match:
        dia, mes = int(match.group(1)), int(match.group(2))
        ano = hoje.year
        try:
            data = date(ano, mes, dia)
            # Se data já passou, vai para próximo ano
            if data < hoje:
                data = date(ano + 1, mes, dia)
            texto = texto[:match.start()] + texto[match.end():]
            return data.strftime('%Y-%m-%d'), texto
        except ValueError:
            pass
    
    # Padrão: depois de amanhã
    if re.search(r'depois\s+de\s+amanh[aã]', texto):
        texto = re.sub(r'depois\s+de\s+amanh[aã]', '', texto)
        data = hoje + timedelta(days=2)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: amanhã
    if re.search(r'amanh[aã]', texto):
        texto = re.sub(r'amanh[aã]', '', texto)
        data = hoje + timedelta(days=1)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: hoje
    if re.search(r'\bhoje\b', texto):
        texto = re.sub(r'\bhoje\b', '', texto)
        return hoje.strftime('%Y-%m-%d'), texto
    
    # Padrão: daqui X dias
    match = re.search(r'daqui\s+(?:a\s+)?(\d+)\s+dias?', texto)
    if match:
        dias = int(match.group(1))
        texto = texto[:match.start()] + texto[match.end():]
        data = hoje + timedelta(days=dias)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: daqui uma/1 semana
    if re.search(r'daqui\s+(?:a\s+)?(?:uma?|1)\s+semanas?', texto):
        texto = re.sub(r'daqui\s+(?:a\s+)?(?:uma?|1)\s+semanas?', '', texto)
        data = hoje + timedelta(days=7)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: daqui X semanas
    match = re.search(r'daqui\s+(?:a\s+)?(\d+)\s+semanas?', texto)
    if match:
        semanas = int(match.group(1))
        texto = texto[:match.start()] + texto[match.end():]
        data = hoje + timedelta(weeks=semanas)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: daqui um/1 mês
    if re.search(r'daqui\s+(?:a\s+)?(?:um?|1)\s+m[eê]s', texto):
        texto = re.sub(r'daqui\s+(?:a\s+)?(?:um?|1)\s+m[eê]s', '', texto)
        data = hoje + timedelta(days=30)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: próxima semana
    if re.search(r'pr[oó]xima?\s+semana', texto):
        texto = re.sub(r'pr[oó]xima?\s+semana', '', texto)
        data = hoje + timedelta(days=7)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: próximo mês
    if re.search(r'pr[oó]xim[oa]?\s+m[eê]s', texto):
        texto = re.sub(r'pr[oó]xim[oa]?\s+m[eê]s', '', texto)
        data = hoje + timedelta(days=30)
        return data.strftime('%Y-%m-%d'), texto
    
    # Padrão: dia X (do mês)
    match = re.search(r'(?:no\s+)?dia\s+(\d{1,2})', texto)
    if match:
        dia = int(match.group(1))
        texto = texto[:match.start()] + texto[match.end():]
        data = calcular_dia_mes(dia)
        return data.strftime('%Y-%m-%d'), texto
    
    # Dias da semana
    dias_semana = [
        (r'segunda(?:[- ]feira)?', 0),
        (r'ter[çc]a(?:[- ]feira)?', 1),
        (r'quarta(?:[- ]feira)?', 2),
        (r'quinta(?:[- ]feira)?', 3),
        (r'sexta(?:[- ]feira)?', 4),
        (r's[aá]bado', 5),
        (r'domingo', 6),
    ]
    
    for pattern, dia_semana in dias_semana:
        # Padrão: próxima segunda, na próxima terça
        match = re.search(rf'(?:na\s+)?pr[oó]xima?\s+{pattern}', texto)
        if match:
            texto = texto[:match.start()] + texto[match.end():]
            data = proxima_dia_semana(dia_semana)
            return data.strftime('%Y-%m-%d'), texto
        
        # Padrão: segunda, terça (sem "próxima")
        match = re.search(rf'\b{pattern}\b', texto)
        if match:
            texto = texto[:match.start()] + texto[match.end():]
            data = proxima_dia_semana(dia_semana)
            return data.strftime('%Y-%m-%d'), texto
    
    # Se não encontrou nenhum padrão, usa amanhã como padrão
    data = hoje + timedelta(days=1)
    return data.strftime('%Y-%m-%d'), texto


def proxima_dia_semana(dia_semana: int) -> date:
    """
    Calcula a próxima ocorrência de um dia da semana.
    
    Args:
        dia_semana: 0=segunda, 1=terça, ..., 6=domingo
    
    Returns:
        date da próxima ocorrência (mínimo 1 dia no futuro)
    """
    hoje = hoje_brasil()
    dias_ate = (dia_semana - hoje.weekday()) % 7
    
    # Se é o mesmo dia da semana, vai para próxima semana
    if dias_ate == 0:
        dias_ate = 7
    
    return hoje + timedelta(days=dias_ate)


def calcular_dia_mes(dia: int) -> date:
    """
    Calcula a data para um dia específico do mês.
    
    Se o dia já passou no mês atual, retorna o dia no próximo mês.
    
    Args:
        dia: Dia do mês (1-31)
    
    Returns:
        date com o dia especificado
    """
    hoje = hoje_brasil()
    
    # Tenta no mês atual
    try:
        data = date(hoje.year, hoje.month, dia)
        if data >= hoje:
            return data
    except ValueError:
        pass
    
    # Vai para próximo mês
    if hoje.month == 12:
        proximo_mes = 1
        proximo_ano = hoje.year + 1
    else:
        proximo_mes = hoje.month + 1
        proximo_ano = hoje.year
    
    try:
        return date(proximo_ano, proximo_mes, dia)
    except ValueError:
        # Dia inválido para o mês (ex: 31 de fevereiro)
        # Retorna último dia do mês
        if proximo_mes == 12:
            return date(proximo_ano + 1, 1, 1) - timedelta(days=1)
        else:
            return date(proximo_ano, proximo_mes + 1, 1) - timedelta(days=1)


def limpar_descricao(texto: str) -> str:
    """
    Remove palavras-chave de lembrete e limpa a descrição.
    
    Remove: me lembra, lembrete, de, pra, para, que, não esquecer, avisa, alerta
    """
    # Palavras e frases a remover
    remover = [
        r'\bme\s+lembra\b',
        r'\blembrete\b',
        r'\bn[aã]o\s+esquecer\b',
        r'\bavisa\b',
        r'\balerta\b',
        r'\bpreciso\b',
        r'\btenho\s+que\b',
        r'\bque\s+eu\b',
        r'\bpra\s+eu\b',
        r'\bpara\s+eu\b',
        r'^\s*de\s+',  # "de" no início
        r'^\s*pra\s+',  # "pra" no início
        r'^\s*para\s+',  # "para" no início
        r'^\s*que\s+',  # "que" no início
    ]
    
    for pattern in remover:
        texto = re.sub(pattern, '', texto, flags=re.IGNORECASE)
    
    # Remove espaços extras
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()


def detectar_recorrencia(texto: str) -> Optional[str]:
    """
    Detecta se o lembrete é recorrente.
    
    Returns:
        'diario', 'semanal', 'mensal' ou None
    """
    texto_lower = texto.lower()
    
    # Padrões de recorrência - ordem importa! Mensal antes de diário
    # "todo dia X" é mensal, "todo dia" (sem número) é diário
    if re.search(r'todo\s+dia\s+\d+|todos\s+os\s+meses|mensal|todo\s+m[eê]s', texto_lower):
        return 'mensal'
    
    if re.search(r'toda\s+semana|todas\s+as\s+semanas|semanal', texto_lower):
        return 'semanal'
    
    if re.search(r'todo\s+dia(?!\s+\d)|todos\s+os\s+dias|di[aá]rio', texto_lower):
        return 'diario'
    
    return None


# ============ FUNÇÕES DE CONVENIÊNCIA PARA O BOT ============

def parse_data_hora(texto: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Função de conveniência para o bot extrair data e hora.
    
    Args:
        texto: Texto do pedido de lembrete
    
    Returns:
        Tuple (data YYYY-MM-DD, hora HH:MM)
    """
    resultado = parse_lembrete(texto)
    return resultado.get('data'), resultado.get('hora')


def extrair_descricao_lembrete(texto: str) -> str:
    """
    Função de conveniência para extrair apenas a descrição.
    
    Args:
        texto: Texto do pedido de lembrete
    
    Returns:
        Descrição limpa
    """
    resultado = parse_lembrete(texto)
    return resultado.get('descricao', '')
