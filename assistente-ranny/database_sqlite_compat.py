"""
SQLite - Banco de dados local
Interface simplificada para o bot
"""

from database_sqlite import *
from datetime import datetime, timedelta

# ============ FUNÇÕES DO BOT ============

# Fechamentos
def add_fechamento(valor: float, data_fechamento: str = None, observacao: str = ''):
    """Adiciona fechamento"""
    if not data_fechamento:
        data_fechamento = hoje_brasil().strftime('%Y-%m-%d')
    return adicionar_fechamento(data_fechamento, valor, 0, observacao)

def get_fechamentos(dias: int = 30):
    """Lista fechamentos dos últimos X dias"""
    fechamentos = listar_fechamentos(limit=dias * 2)  # Pega mais para filtrar
    
    # Filtra por data
    limite = (hoje_brasil() - timedelta(days=dias)).isoformat()
    result = []
    for f in fechamentos:
        if f.get('data_fechamento', '') >= limite:
            result.append({
                'id': f['id'],
                'valor': f['total_vendas'],
                'data': f['data_fechamento'],
                'observacao': f.get('observacoes'),
                'created_at': f.get('created_at')
            })
    
    return result

def get_fechamento_anterior():
    """Retorna fechamento do dia anterior"""
    fechamentos = get_fechamentos(7)
    if len(fechamentos) > 1:
        return fechamentos[1]
    return None

# Lembretes
def add_lembrete(descricao: str, data_lembrete: str, hora: str = '09:00', recorrente: str = None):
    """Adiciona lembrete"""
    data_hora = f"{data_lembrete} {hora}"
    return adicionar_lembrete(descricao, data_hora, recorrente)

def get_lembretes_ativos():
    """Lista lembretes ativos"""
    lembretes = listar_lembretes_ativos()
    
    result = []
    for lem in lembretes:
        # Separa data e hora
        data_hora = lem.get('data_hora', '')
        if ' ' in data_hora:
            data, hora = data_hora.split(' ', 1)
        else:
            data = data_hora
            hora = '09:00'
        
        result.append({
            'id': lem['id'],
            'descricao': lem['descricao'],
            'data': data,
            'hora': hora,
            'recorrente': lem.get('recorrente'),
            'ativo': bool(lem.get('ativo', 1)),
            'disparado': False,
            'created_at': lem.get('created_at')
        })
    
    return result

def get_lembretes_para_disparar(hora_atual: str = None):
    """Busca lembretes que devem ser disparados"""
    if hora_atual is None:
        hora_atual = agora_brasil().strftime('%H:%M:%S')
    
    hoje = hoje_brasil().strftime('%Y-%m-%d')
    data_hora_limite = f"{hoje} {hora_atual}"
    
    lembretes = listar_lembretes_ativos()
    
    result = []
    for lem in lembretes:
        if lem.get('data_hora', '') <= data_hora_limite:
            # Separa data e hora
            data_hora = lem.get('data_hora', '')
            if ' ' in data_hora:
                data, hora = data_hora.split(' ', 1)
            else:
                data = data_hora
                hora = '09:00'
            
            result.append({
                'id': lem['id'],
                'descricao': lem['descricao'],
                'data': data,
                'hora': hora,
                'recorrente': lem.get('recorrente'),
                'ativo': bool(lem.get('ativo', 1)),
                'disparado': False
            })
    
    return result

def marcar_lembrete_disparado(lembrete_id: int):
    """Marca lembrete como disparado"""
    desativar_lembrete(lembrete_id)

def cancelar_lembrete(lembrete_id: int):
    """Cancela lembrete"""
    return desativar_lembrete(lembrete_id)

def buscar_lembrete_por_descricao(termo: str):
    """Busca lembretes por descrição"""
    lembretes = listar_lembretes_ativos()
    result = []
    for lem in lembretes:
        if termo.lower() in lem.get('descricao', '').lower():
            # Separa data e hora
            data_hora = lem.get('data_hora', '')
            if ' ' in data_hora:
                data, hora = data_hora.split(' ', 1)
            else:
                data = data_hora
                hora = '09:00'
            
            result.append({
                'id': lem['id'],
                'descricao': lem['descricao'],
                'data': data,
                'hora': hora,
                'recorrente': lem.get('recorrente')
            })
    return result

def criar_proximo_lembrete_recorrente(lembrete: dict):
    """Cria próximo lembrete recorrente"""
    recorrente = lembrete.get('recorrente')
    if not recorrente:
        return None
    
    data_atual = datetime.strptime(lembrete['data'], '%Y-%m-%d').date()
    
    if recorrente == 'diario':
        proxima_data = data_atual + timedelta(days=1)
    elif recorrente == 'semanal':
        proxima_data = data_atual + timedelta(weeks=1)
    elif recorrente == 'mensal':
        if data_atual.month == 12:
            proxima_data = data_atual.replace(year=data_atual.year + 1, month=1)
        else:
            try:
                proxima_data = data_atual.replace(month=data_atual.month + 1)
            except ValueError:
                if data_atual.month == 11:
                    proxima_data = date(data_atual.year + 1, 1, 1) - timedelta(days=1)
                else:
                    proxima_data = date(data_atual.year, data_atual.month + 2, 1) - timedelta(days=1)
    else:
        return None
    
    return add_lembrete(
        descricao=lembrete['descricao'],
        data_lembrete=proxima_data.strftime('%Y-%m-%d'),
        hora=lembrete.get('hora', '09:00'),
        recorrente=recorrente
    )

# Documentos
def add_documento(tipo: str, descricao: str, file_id: str, categoria: str,
                  dados_extraidos: dict = None, message_id: int = None, topic_id: int = None):
    """Adiciona documento com localização no Telegram
    
    Args:
        tipo: MIME type do documento
        descricao: Nome/descrição do documento
        file_id: ID do arquivo no Telegram (para reenvio)
        categoria: Categoria do documento
        dados_extraidos: Dados extras extraídos pela IA
        message_id: ID da mensagem no Telegram (opcional)
        topic_id: ID do tópico onde o arquivo está (opcional)
    
    Returns:
        Dict com id, descricao e categoria do documento
    """
    # Salva dados extras no resumo como JSON
    resumo_completo = descricao
    if dados_extraidos:
        import json
        resumo_completo = f"{descricao}\n\nDados: {json.dumps(dados_extraidos, ensure_ascii=False)}"
    
    # Normaliza categoria para minúsculas
    categoria_lower = categoria.lower() if categoria else 'outros'
    
    doc_id = adicionar_documento(
        nome_arquivo=descricao or 'documento',
        tipo_documento=tipo,
        categoria=categoria_lower,
        file_id=file_id,
        resumo=resumo_completo,
        tags=[categoria_lower] if categoria_lower else None,
        message_id=message_id,
        topic_id=topic_id
    )
    
    # Retorna um dict com id
    return {'id': doc_id, 'descricao': descricao, 'categoria': categoria_lower, 'message_id': message_id, 'topic_id': topic_id}

def buscar_documentos(termo: str = '', categoria: str = None, limit: int = 20):
    """Busca documentos no banco"""
    # Importa a função do database_sqlite
    from database_sqlite import buscar_documentos as _buscar_docs
    
    # Normaliza categoria para minúsculas
    if categoria:
        categoria = categoria.lower()
    
    docs = _buscar_docs(query=termo, categoria=categoria, limit=limit)
    
    # Formata para o padrão esperado pelo bot
    result = []
    for doc in docs:
        # Usa nome_arquivo como descrição principal
        descricao = doc.get('nome_arquivo') or doc.get('resumo', 'Documento')
        
        result.append({
            'id': doc.get('id'),
            'descricao': descricao,
            'categoria': doc.get('categoria', 'outros'),
            'file_id': doc.get('file_id'),
            'tipo': doc.get('tipo_documento'),
            'resumo': doc.get('resumo'),
            'created_at': doc.get('created_at'),
            'message_id': doc.get('message_id'),
            'topic_id': doc.get('topic_id')
        })
    
    return result

# Vencimentos
def add_vencimento(tipo: str, descricao: str, valor: float, vencimento: str,
                   recorrente: bool = False, documento_id: int = None):
    """Adiciona vencimento"""
    return adicionar_vencimento(
        descricao=descricao,
        valor=valor,
        data_vencimento=vencimento,
        categoria=tipo,
        fornecedor=None
    )

def get_vencimentos_proximos(dias: int = 7):
    """Lista vencimentos próximos"""
    vencimentos = listar_vencimentos_proximos(dias)
    
    result = []
    for venc in vencimentos:
        venc_date = datetime.strptime(venc['data_vencimento'], '%Y-%m-%d').date()
        dias_restantes = (venc_date - hoje_brasil()).days
        
        result.append({
            'id': venc['id'],
            'tipo': venc.get('categoria', 'outro'),
            'descricao': venc['descricao'],
            'valor': venc.get('valor', 0),
            'data_vencimento': venc['data_vencimento'],
            'vencimento': venc['data_vencimento'],
            'recorrente': None,
            'pago': venc.get('status') == 'pago',
            'dias_restantes': dias_restantes,
            'created_at': venc.get('created_at')
        })
    
    return result

def buscar_vencimentos_nao_pagos(termo: str):
    """Busca vencimentos não pagos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM vencimentos
        WHERE status != 'pago'
        AND (descricao LIKE ? OR categoria LIKE ?)
        ORDER BY data_vencimento DESC
    ''', (f'%{termo}%', f'%{termo}%'))
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        venc = dict(row)
        result.append({
            'id': venc['id'],
            'tipo': venc.get('categoria', 'outro'),
            'descricao': venc['descricao'],
            'valor': venc.get('valor', 0),
            'data_vencimento': venc['data_vencimento'],
            'vencimento': venc['data_vencimento']
        })
    
    return result

def marcar_pago(venc_id: int):
    """Marca vencimento como pago"""
    marcar_vencimento_pago(venc_id)
    return None

def criar_vencimento_de_boleto(dados_boleto: dict, documento_id: int = None):
    """Cria vencimento de boleto"""
    valor = dados_boleto.get('valor')
    vencimento = dados_boleto.get('vencimento')
    
    if not valor and not vencimento:
        return None
    
    if not vencimento:
        return None
    
    beneficiario = dados_boleto.get('beneficiario', '')
    tipo_conta = dados_boleto.get('tipo_conta', 'outro')
    
    tipo_display = {
        'luz': 'Conta de Luz',
        'agua': 'Conta de Água',
        'internet': 'Internet',
        'telefone': 'Telefone',
        'gas': 'Gás',
        'aluguel': 'Aluguel',
        'condominio': 'Condomínio',
        'cartao': 'Fatura Cartão',
    }.get(tipo_conta, 'Conta')
    
    if beneficiario:
        descricao = f"{tipo_display} - {beneficiario}"
    else:
        descricao = tipo_display
    
    if len(descricao) > 100:
        descricao = descricao[:97] + "..."
    
    return add_vencimento(
        tipo=tipo_conta,
        descricao=descricao,
        valor=float(valor) if valor else 0.0,
        vencimento=vencimento,
        recorrente=False,
        documento_id=documento_id
    )

def get_vencimentos_periodo(dias: int = 30):
    """Lista vencimentos do período"""
    conn = get_connection()
    cursor = conn.cursor()
    
    limite = (hoje_brasil() - timedelta(days=dias)).strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT * FROM vencimentos
        WHERE data_vencimento >= ?
        ORDER BY data_vencimento DESC
    ''', (limite,))
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        venc = dict(row)
        result.append({
            'tipo': venc.get('categoria', 'outro'),
            'valor': venc.get('valor', 0),
            'data_vencimento': venc['data_vencimento'],
            'pago': venc.get('status') == 'pago',
            'descricao': venc['descricao']
        })
    
    return result

# Funcionários
def add_funcionario(nome: str, funcao: str, admissao: str):
    """Adiciona funcionário"""
    return adicionar_funcionario(nome, funcao, None, None, None, None)

def get_funcionarios(status: str = 'ativo'):
    """Lista funcionários"""
    return listar_funcionarios(ativos_apenas=(status == 'ativo'))

# Relatórios temporários
_relatorios_temp = {}

def criar_relatorio_temp(tipo: str, dados: dict):
    """Cria relatório temporário"""
    import uuid
    token = str(uuid.uuid4())
    _relatorios_temp[token] = {
        'tipo': tipo,
        'dados': dados,
        'created_at': datetime.now().isoformat()
    }
    return token

def get_relatorio_temp(token: str):
    """Busca relatório temporário"""
    return _relatorios_temp.get(token)

# OAuth tokens
_oauth_tokens = {}

def save_oauth_token(provider: str, access_token: str, refresh_token: str,
                     expires_at: datetime, scope: str = None):
    """Salva token OAuth"""
    _oauth_tokens[provider] = {
        'provider': provider,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at.isoformat() if isinstance(expires_at, datetime) else expires_at,
        'scope': scope
    }
    return _oauth_tokens[provider]

def get_oauth_token(provider: str):
    """Busca token OAuth"""
    return _oauth_tokens.get(provider)

def update_oauth_token(provider: str, access_token: str, expires_at: datetime):
    """Atualiza token OAuth"""
    if provider in _oauth_tokens:
        _oauth_tokens[provider]['access_token'] = access_token
        _oauth_tokens[provider]['expires_at'] = expires_at.isoformat() if isinstance(expires_at, datetime) else expires_at
        return True
    return False

def delete_oauth_token(provider: str):
    """Remove token OAuth"""
    if provider in _oauth_tokens:
        del _oauth_tokens[provider]
        return True
    return False

def contar_documentos_por_categoria():
    """Retorna contagem de documentos por categoria"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT categoria, COUNT(*) as total
            FROM documentos
            GROUP BY categoria
            ORDER BY total DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        result = {}
        total = 0
        for row in rows:
            cat = row['categoria'] if row['categoria'] else 'outros'
            count = row['total']
            result[cat] = count
            total += count
        
        return {'total': total, 'por_categoria': result}
    except Exception as e:
        print(f"Erro ao contar documentos: {e}")
        return {'total': 0, 'por_categoria': {}}

# Teste de conexão
def test_connection():
    """Testa conexão"""
    try:
        conn = get_connection()
        conn.close()
        return True
    except:
        return False

def check_connection():
    """Verifica conexão"""
    return test_connection()

# Processos e audiências
def get_audiencias_proximas(dias: int = 30):
    """Lista audiências próximas"""
    return []

# Problemas TI
def get_problemas_ti(status: str = None):
    """Lista problemas TI"""
    return []
