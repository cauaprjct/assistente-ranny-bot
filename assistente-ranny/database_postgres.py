"""
Banco de dados PostgreSQL (Render)
Banco persistente para produção
"""
import os
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict
import json

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_DISPONIVEL = True
except ImportError:
    POSTGRES_DISPONIVEL = False
    print("⚠️ psycopg2 não instalado. Use: pip install psycopg2-binary")

TIMEZONE_BR = ZoneInfo('America/Sao_Paulo')

def agora_brasil() -> datetime:
    return datetime.now(TIMEZONE_BR)

def hoje_brasil() -> date:
    return agora_brasil().date()

# URL do banco (Render fornece via variável de ambiente)
DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    """Retorna conexão PostgreSQL"""
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada!")
    
    # Render usa postgres://, mas psycopg2 precisa de postgresql://
    db_url = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn

def init_database():
    """Inicializa tabelas PostgreSQL"""
    if not POSTGRES_DISPONIVEL:
        print("❌ PostgreSQL não disponível")
        return False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Tabela funcionarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funcionarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                cargo TEXT,
                salario REAL,
                data_admissao TEXT,
                cpf TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela vencimentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vencimentos (
                id SERIAL PRIMARY KEY,
                descricao TEXT NOT NULL,
                valor REAL,
                data_vencimento TEXT NOT NULL,
                categoria TEXT,
                fornecedor TEXT,
                status TEXT DEFAULT 'pendente',
                data_pagamento TEXT,
                observacoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela fechamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fechamentos (
                id SERIAL PRIMARY KEY,
                data_fechamento TEXT NOT NULL,
                total_vendas REAL DEFAULT 0,
                total_despesas REAL DEFAULT 0,
                saldo_final REAL DEFAULT 0,
                observacoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela lembretes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lembretes (
                id SERIAL PRIMARY KEY,
                descricao TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                recorrente TEXT,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela documentos (PRINCIPAL)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documentos (
                id SERIAL PRIMARY KEY,
                nome_arquivo TEXT NOT NULL,
                tipo_documento TEXT,
                categoria TEXT,
                file_id TEXT,
                file_path TEXT,
                resumo TEXT,
                tags TEXT,
                message_id INTEGER,
                topic_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices para melhorar performance de busca
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_documentos_nome 
            ON documentos(nome_arquivo)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_documentos_categoria 
            ON documentos(categoria)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_documentos_message_id 
            ON documentos(message_id)
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Tabelas PostgreSQL criadas/verificadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar PostgreSQL: {e}")
        return False

# ============ FUNÇÕES DE FUNCIONÁRIOS ============

def adicionar_funcionario(nome: str, cargo: Optional[str] = None, salario: Optional[float] = None,
                          cpf: Optional[str] = None, telefone: Optional[str] = None,
                          email: Optional[str] = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO funcionarios (nome, cargo, salario, cpf, telefone, email, data_admissao)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (nome, cargo, salario, cpf, telefone, email, str(hoje_brasil())))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao adicionar funcionário: {e}")
        return False

def listar_funcionarios(ativos_apenas: bool = True) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    if ativos_apenas:
        cursor.execute('SELECT * FROM funcionarios WHERE ativo = 1')
    else:
        cursor.execute('SELECT * FROM funcionarios')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in rows]

# ============ FUNÇÕES DE VENCIMENTOS ============

def adicionar_vencimento(descricao: str, valor: float, data_vencimento: str,
                         categoria: Optional[str] = None, fornecedor: Optional[str] = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vencimentos (descricao, valor, data_vencimento, categoria, fornecedor)
            VALUES (%s, %s, %s, %s, %s)
        ''', (descricao, valor, data_vencimento, categoria, fornecedor))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao adicionar vencimento: {e}")
        return False

def listar_vencimentos_proximos(dias: int = 7) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    data_limite = (hoje_brasil() + timedelta(days=dias)).isoformat()
    cursor.execute('''
        SELECT * FROM vencimentos 
        WHERE status = 'pendente' AND data_vencimento <= %s
        ORDER BY data_vencimento
    ''', (data_limite,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in rows]

def marcar_vencimento_pago(vencimento_id: int) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vencimentos SET status = 'pago', data_pagamento = %s
            WHERE id = %s
        ''', (str(hoje_brasil()), vencimento_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao marcar vencimento pago: {e}")
        return False

# ============ FUNÇÕES DE FECHAMENTOS ============

def adicionar_fechamento(data_fechamento: str, total_vendas: float, total_despesas: float,
                        observacoes: Optional[str] = None) -> bool:
    try:
        saldo = total_vendas - total_despesas
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fechamentos (data_fechamento, total_vendas, total_despesas, saldo_final, observacoes)
            VALUES (%s, %s, %s, %s, %s)
        ''', (data_fechamento, total_vendas, total_despesas, saldo, observacoes))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao adicionar fechamento: {e}")
        return False

def listar_fechamentos(limit: int = 10) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM fechamentos ORDER BY data_fechamento DESC LIMIT %s', (limit,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in rows]

# ============ FUNÇÕES DE LEMBRETES ============

def adicionar_lembrete(descricao: str, data_hora: str, recorrente: Optional[str] = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lembretes (descricao, data_hora, recorrente)
            VALUES (%s, %s, %s)
        ''', (descricao, data_hora, recorrente))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao adicionar lembrete: {e}")
        return False

def listar_lembretes_ativos() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lembretes WHERE ativo = 1 ORDER BY data_hora')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in rows]

def desativar_lembrete(lembrete_id: int) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE lembretes SET ativo = 0 WHERE id = %s', (lembrete_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao desativar lembrete: {e}")
        return False

# ============ FUNÇÕES DE DOCUMENTOS (PRINCIPAL) ============

def adicionar_documento(nome_arquivo: str, tipo_documento: Optional[str] = None,
                        categoria: Optional[str] = None, file_id: Optional[str] = None,
                        file_path: Optional[str] = None, resumo: Optional[str] = None,
                        tags: Optional[List[str]] = None, message_id: Optional[int] = None,
                        topic_id: Optional[int] = None) -> int:
    """Adiciona documento e retorna o ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        tags_str = json.dumps(tags) if tags else None
        
        cursor.execute('''
            INSERT INTO documentos (nome_arquivo, tipo_documento, categoria, file_id, file_path, resumo, tags, message_id, topic_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (nome_arquivo, tipo_documento, categoria, file_id, file_path, resumo, tags_str, message_id, topic_id))
        
        doc_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        return doc_id
    except Exception as e:
        print(f"Erro ao adicionar documento: {e}")
        return False

def buscar_documentos(query: str = '', categoria: Optional[str] = None,
                     tipo_documento: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Busca documentos no banco"""
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = 'SELECT * FROM documentos WHERE 1=1'
    params = []
    
    if query:
        sql += ' AND (nome_arquivo ILIKE %s OR resumo ILIKE %s)'
        params.extend([f'%{query}%', f'%{query}%'])
    if categoria:
        sql += ' AND categoria = %s'
        params.append(categoria)
    if tipo_documento:
        sql += ' AND tipo_documento = %s'
        params.append(tipo_documento)
    
    sql += ' ORDER BY created_at DESC LIMIT %s'
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for row in rows:
        doc = dict(row)
        if doc.get('tags'):
            try:
                doc['tags'] = json.loads(doc['tags'])
            except:
                doc['tags'] = []
        result.append(doc)
    return result

def contar_documentos() -> int:
    """Conta total de documentos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM documentos')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result['total'] if result else 0
    except Exception as e:
        print(f"Erro ao contar documentos: {e}")
        return 0
