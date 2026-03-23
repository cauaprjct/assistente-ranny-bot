"""
Sistema de Memória de Conversa Persistente
Assistente Ranny V3

Funcionalidades:
- Persistência em banco de dados (SQLite/PostgreSQL)
- Contexto por tópico do grupo
- Limite configurável de mensagens
- Limpeza automática de mensagens antigas
- Sumarização de contexto antigo
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

# Configurações
MAX_MESSAGES_PER_CHAT = 50  # Aumentado de 10 para 50
MAX_DAYS_MEMORY = 30  # Dias para manter histórico
SUMMARIZE_THRESHOLD = 40  # Quando chegar em 40 mensagens, sumariza as 20 mais antigas

# Cache em memória para performance
_memory_cache = defaultdict(list)
_last_cache_update = {}

# Tenta importar o adaptador de banco de dados
try:
    import database_adapter as db
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logger.warning("Database adapter não encontrado - usando apenas cache em memória")


def _ensure_table_exists():
    """Cria tabela de memória se não existir"""
    if not HAS_DATABASE:
        return
    
    try:
        # Verifica qual banco está sendo usado
        if hasattr(db, 'get_connection'):
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # SQLite
            if hasattr(conn, 'execute'):
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        chat_id INTEGER NOT NULL,
                        topic_id INTEGER DEFAULT 0,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Índices para performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_user ON conversation_memory(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_chat ON conversation_memory(chat_id, topic_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON conversation_memory(timestamp)')
                
                conn.commit()
                logger.info("Tabela conversation_memory criada/verificada")
    except Exception as e:
        logger.error(f"Erro ao criar tabela de memória: {e}")


def save_message(
    user_id: int,
    chat_id: int,
    content: str,
    role: str = "user",
    topic_id: int = 0,
    metadata: dict = None
) -> bool:
    """Salva uma mensagem no histórico de conversa
    
    Args:
        user_id: ID do usuário
        chat_id: ID do chat/grupo
        content: Conteúdo da mensagem
        role: "user" ou "assistant"
        topic_id: ID do tópico (para grupos com tópicos)
        metadata: Dados adicionais (opcional)
    
    Returns:
        True se salvou com sucesso
    """
    timestamp = datetime.now()
    
    # Atualiza cache em memória
    cache_key = f"{user_id}_{chat_id}_{topic_id}"
    _memory_cache[cache_key].append({
        'role': role,
        'content': content,
        'timestamp': timestamp.isoformat(),
        'metadata': metadata or {}
    })
    
    # Limita cache em memória
    if len(_memory_cache[cache_key]) > MAX_MESSAGES_PER_CHAT:
        _memory_cache[cache_key] = _memory_cache[cache_key][-MAX_MESSAGES_PER_CHAT:]
    
    _last_cache_update[cache_key] = timestamp
    
    # Salva no banco de dados
    if not HAS_DATABASE:
        return True
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        # SQLite
        if hasattr(conn, 'execute'):
            cursor.execute('''
                INSERT INTO conversation_memory 
                (user_id, chat_id, topic_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, chat_id, topic_id, role, content, timestamp, metadata_json))
            
            conn.commit()
            
            # Limpa mensagens antigas (mais de MAX_DAYS_MEMORY dias)
            cleanup_old_messages(chat_id, topic_id)
            
            return True
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem na memória: {e}")
        return False


def get_conversation_history(
    user_id: int,
    chat_id: int,
    topic_id: int = 0,
    limit: int = MAX_MESSAGES_PER_CHAT
) -> List[Dict[str, Any]]:
    """Recupera histórico de conversa
    
    Args:
        user_id: ID do usuário
        chat_id: ID do chat/grupo
        topic_id: ID do tópico (0 para geral)
        limit: Máximo de mensagens a retornar
    
    Returns:
        Lista de mensagens no formato [{"role": "user/assistant", "content": "..."}]
    """
    cache_key = f"{user_id}_{chat_id}_{topic_id}"
    
    # Verifica se cache está atualizado (menos de 5 minutos)
    if cache_key in _last_cache_update:
        cache_age = datetime.now() - _last_cache_update[cache_key]
        if cache_age.total_seconds() < 300 and len(_memory_cache[cache_key]) >= limit:
            return _memory_cache[cache_key][-limit:]
    
    # Busca do banco de dados
    if not HAS_DATABASE:
        return list(_memory_cache[cache_key])[-limit:]
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # SQLite
        if hasattr(conn, 'execute'):
            cursor.execute('''
                SELECT role, content, timestamp, metadata
                FROM conversation_memory
                WHERE user_id = ? AND chat_id = ? AND topic_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, chat_id, topic_id, limit))
            
            rows = cursor.fetchall()
            
            # Inverte para ordem cronológica
            messages = []
            for row in reversed(rows):
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'timestamp': row[2],
                    'metadata': json.loads(row[3]) if row[3] else {}
                })
            
            # Atualiza cache
            _memory_cache[cache_key] = messages
            _last_cache_update[cache_key] = datetime.now()
            
            return messages
    except Exception as e:
        logger.error(f"Erro ao recuperar histórico: {e}")
        return list(_memory_cache[cache_key])[-limit:]


def get_context_for_ai(
    user_id: int,
    chat_id: int,
    topic_id: int = 0,
    max_messages: int = 30
) -> str:
    """Monta contexto formatado para enviar à IA
    
    Args:
        user_id: ID do usuário
        chat_id: ID do chat/grupo
        topic_id: ID do tópico
        max_messages: Máximo de mensagens no contexto
    
    Returns:
        String formatada com histórico da conversa
    """
    messages = get_conversation_history(user_id, chat_id, topic_id, max_messages)
    
    if not messages:
        return ""
    
    # Formata mensagens
    formatted = []
    for msg in messages:
        role_name = "Ranny" if msg['role'] == 'user' else "Assistente"
        formatted.append(f"{role_name}: {msg['content']}")
    
    return "\n".join(formatted)


def cleanup_old_messages(chat_id: int, topic_id: int = 0, days: int = MAX_DAYS_MEMORY) -> int:
    """Remove mensagens antigas do banco de dados
    
    Args:
        chat_id: ID do chat
        topic_id: ID do tópico
        days: Dias para manter
    
    Returns:
        Número de mensagens removidas
    """
    if not HAS_DATABASE:
        return 0
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # SQLite
        if hasattr(conn, 'execute'):
            cursor.execute('''
                DELETE FROM conversation_memory
                WHERE chat_id = ? AND topic_id = ? AND timestamp < ?
            ''', (chat_id, topic_id, cutoff_date))
            
            deleted = cursor.rowcount
            conn.commit()
            
            if deleted > 0:
                logger.info(f"Limpeza: {deleted} mensagens antigas removidas")
            
            return deleted
    except Exception as e:
        logger.error(f"Erro ao limpar mensagens antigas: {e}")
        return 0


def clear_conversation(user_id: int, chat_id: int, topic_id: int = 0) -> bool:
    """Limpa histórico de conversa
    
    Args:
        user_id: ID do usuário
        chat_id: ID do chat
        topic_id: ID do tópico
    
    Returns:
        True se limpou com sucesso
    """
    cache_key = f"{user_id}_{chat_id}_{topic_id}"
    
    # Limpa cache
    _memory_cache[cache_key] = []
    if cache_key in _last_cache_update:
        del _last_cache_update[cache_key]
    
    # Limpa banco
    if not HAS_DATABASE:
        return True
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM conversation_memory
            WHERE user_id = ? AND chat_id = ? AND topic_id = ?
        ''', (user_id, chat_id, topic_id))
        
        conn.commit()
        logger.info(f"Histórico limpo para user={user_id}, chat={chat_id}, topic={topic_id}")
        return True
    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {e}")
        return False


def get_conversation_stats(user_id: int, chat_id: int, topic_id: int = 0) -> Dict[str, Any]:
    """Retorna estatísticas da conversa
    
    Returns:
        Dict com total de mensagens, primeira/última mensagem, etc.
    """
    cache_key = f"{user_id}_{chat_id}_{topic_id}"
    
    stats = {
        'total_messages': len(_memory_cache[cache_key]),
        'cached': cache_key in _memory_cache,
        'max_limit': MAX_MESSAGES_PER_CHAT
    }
    
    if not HAS_DATABASE:
        return stats
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
            FROM conversation_memory
            WHERE user_id = ? AND chat_id = ? AND topic_id = ?
        ''', (user_id, chat_id, topic_id))
        
        row = cursor.fetchone()
        if row:
            stats['total_in_db'] = row[0]
            stats['first_message'] = row[1]
            stats['last_message'] = row[2]
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return stats


def summarize_old_context(messages: List[Dict]) -> str:
    """Sumariza mensagens antigas para economizar tokens
    
    Args:
        messages: Lista de mensagens antigas
    
    Returns:
        String com resumo das mensagens
    """
    if not messages:
        return ""
    
    # Conta tópicos principais
    topics = defaultdict(int)
    for msg in messages:
        content = msg['content'].lower()
        # Detecta palavras-chave
        keywords = ['planilha', 'entregador', 'boleto', 'documento', 'relatório', 
                   'contrato', 'recibo', 'pagamento', 'entrega', 'fechamento']
        for kw in keywords:
            if kw in content:
                topics[kw] += 1
    
    # Monta resumo
    if topics:
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        summary = "Resumo da conversa anterior: "
        summary += ", ".join([f"{t[0]} ({t[1]}x)" for t in top_topics])
        return summary
    
    return f"[{len(messages)} mensagens anteriores sobre assuntos diversos]"


# Inicializa tabela ao importar o módulo
_ensure_table_exists()