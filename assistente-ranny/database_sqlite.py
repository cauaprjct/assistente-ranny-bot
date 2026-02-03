"""
Banco de dados com SQLite local (temporário, substitui Supabase)
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict
import sqlite3
import json
import os

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

TIMEZONE_BR = ZoneInfo('America/Sao_Paulo')

def agora_brasil() -> datetime:
    return datetime.now(TIMEZONE_BR)

def hoje_brasil() -> date:
    return agora_brasil().date()

DB_PATH = 'bot_database.db'

def get_connection():
    """Retorna conexão SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inicializa tabelas SQLite"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT,
            salario REAL,
            data_admissao TEXT,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            ativo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vencimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL,
            data_vencimento TEXT NOT NULL,
            categoria TEXT,
            fornecedor TEXT,
            status TEXT DEFAULT 'pendente',
            data_pagamento TEXT,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fechamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_fechamento TEXT NOT NULL,
            total_vendas REAL DEFAULT 0,
            total_despesas REAL DEFAULT 0,
            saldo_final REAL DEFAULT 0,
            observacoes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lembretes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            recorrente TEXT,
            ativo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_arquivo TEXT NOT NULL,
            tipo_documento TEXT,
            categoria TEXT,
            file_id TEXT,
            file_path TEXT,
            resumo TEXT,
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

def adicionar_funcionario(nome: str, cargo: Optional[str] = None, salario: Optional[float] = None,
                          cpf: Optional[str] = None, telefone: Optional[str] = None,
                          email: Optional[str] = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO funcionarios (nome, cargo, salario, cpf, telefone, email, data_admissao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, cargo, salario, cpf, telefone, email, str(hoje_brasil())))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def listar_funcionarios(ativos_apenas: bool = True) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    if ativos_apenas:
        cursor.execute('SELECT * FROM funcionarios WHERE ativo = 1')
    else:
        cursor.execute('SELECT * FROM funcionarios')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def adicionar_vencimento(descricao: str, valor: float, data_vencimento: str,
                         categoria: Optional[str] = None, fornecedor: Optional[str] = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vencimentos (descricao, valor, data_vencimento, categoria, fornecedor)
            VALUES (?, ?, ?, ?, ?)
        ''', (descricao, valor, data_vencimento, categoria, fornecedor))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def listar_vencimentos_proximos(dias: int = 7) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    data_limite = (hoje_brasil() + timedelta(days=dias)).isoformat()
    cursor.execute('''
        SELECT * FROM vencimentos 
        WHERE status = 'pendente' AND data_vencimento <= ?
        ORDER BY data_vencimento
    ''', (data_limite,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def marcar_vencimento_pago(vencimento_id: int) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vencimentos SET status = 'pago', data_pagamento = ?
            WHERE id = ?
        ''', (str(hoje_brasil()), vencimento_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def adicionar_fechamento(data_fechamento: str, total_vendas: float, total_despesas: float,
                        observacoes: Optional[str] = None) -> bool:
    try:
        saldo = total_vendas - total_despesas
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fechamentos (data_fechamento, total_vendas, total_despesas, saldo_final, observacoes)
            VALUES (?, ?, ?, ?, ?)
        ''', (data_fechamento, total_vendas, total_despesas, saldo, observacoes))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def listar_fechamentos(limit: int = 10) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM fechamentos ORDER BY data_fechamento DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def adicionar_lembrete(descricao: str, data_hora: str, recorrente: Optional[str] = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lembretes (descricao, data_hora, recorrente)
            VALUES (?, ?, ?)
        ''', (descricao, data_hora, recorrente))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def listar_lembretes_ativos() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lembretes WHERE ativo = 1 ORDER BY data_hora')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def desativar_lembrete(lembrete_id: int) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE lembretes SET ativo = 0 WHERE id = ?', (lembrete_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def adicionar_documento(nome_arquivo: str, tipo_documento: Optional[str] = None,
                        categoria: Optional[str] = None, file_id: Optional[str] = None,
                        file_path: Optional[str] = None, resumo: Optional[str] = None,
                        tags: Optional[List[str]] = None, message_id: Optional[int] = None,
                        topic_id: Optional[int] = None) -> bool:
    """
    Adiciona documento ao banco.
    message_id e topic_id são opcionais e mantidos apenas para compatibilidade.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        tags_str = json.dumps(tags) if tags else None
        
        # Verifica se as colunas message_id e topic_id existem na tabela
        cursor.execute("PRAGMA table_info(documentos)")
        columns = [col[1] for col in cursor.fetchall()]
        has_message_id = 'message_id' in columns
        has_topic_id = 'topic_id' in columns
        
        # Monta query dinamicamente baseado nas colunas disponíveis
        if has_message_id and has_topic_id:
            cursor.execute('''
                INSERT INTO documentos (nome_arquivo, tipo_documento, categoria, file_id, file_path, resumo, tags, message_id, topic_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome_arquivo, tipo_documento, categoria, file_id, file_path, resumo, tags_str, message_id, topic_id))
        else:
            cursor.execute('''
                INSERT INTO documentos (nome_arquivo, tipo_documento, categoria, file_id, file_path, resumo, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome_arquivo, tipo_documento, categoria, file_id, file_path, resumo, tags_str))
        
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        return doc_id
    except Exception as e:
        print(f"Erro ao adicionar documento: {e}")
        return False

def buscar_documentos(query: str = '', categoria: Optional[str] = None,
                     tipo_documento: Optional[str] = None, limit: int = 20) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    sql = 'SELECT * FROM documentos WHERE 1=1'
    params = []
    
    if query:
        sql += ' AND (nome_arquivo LIKE ? COLLATE NOCASE OR resumo LIKE ? COLLATE NOCASE)'
        params.extend([f'%{query}%', f'%{query}%'])
    if categoria:
        sql += ' AND categoria = ?'
        params.append(categoria)
    if tipo_documento:
        sql += ' AND tipo_documento = ?'
        params.append(tipo_documento)
    
    sql += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
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
