"""
Adaptador de Banco de Dados - Automático
Usa PostgreSQL se DATABASE_URL estiver configurada, senão usa SQLite
"""

import sys
import io
import os

# Configura encoding UTF-8 para o stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Detecta qual banco usar
DATABASE_URL = os.getenv('DATABASE_URL')
DB_TYPE = "postgres" if DATABASE_URL else "sqlite"

if DB_TYPE == "postgres":
    print("🟢 Usando PostgreSQL (banco persistente)")
    try:
        # Importa funções do PostgreSQL
        from database_postgres import *
        # Importa funções de compatibilidade
        from database_sqlite_compat import (
            add_fechamento, get_fechamentos, get_fechamento_anterior,
            add_lembrete, get_lembretes_ativos, get_lembretes_para_disparar,
            marcar_lembrete_disparado, cancelar_lembrete, buscar_lembrete_por_descricao,
            criar_proximo_lembrete_recorrente,
            add_documento, buscar_documentos,
            add_vencimento, get_vencimentos_proximos, buscar_vencimentos_nao_pagos,
            marcar_pago, criar_vencimento_de_boleto, get_vencimentos_periodo,
            add_funcionario, get_funcionarios,
            criar_relatorio_temp, get_relatorio_temp,
            save_oauth_token, get_oauth_token, update_oauth_token, delete_oauth_token,
            contar_documentos_por_categoria, test_connection, check_connection,
            get_audiencias_proximas, get_problemas_ti
        )
        
        # Inicializa banco PostgreSQL
        init_database()
        
    except ImportError as e:
        print(f"⚠️ Erro ao importar PostgreSQL: {e}")
        print("🟡 Fallback para SQLite")
        DB_TYPE = "sqlite"
        from database_sqlite_compat import *
else:
    print("🟡 Usando SQLite (banco local)")
    # Importa todas as funções do SQLite
    from database_sqlite_compat import *

# Exporta informação sobre qual banco está sendo usado
def get_db_info():
    """Retorna informações sobre o banco de dados em uso"""
    if DB_TYPE == "postgres":
        return {
            'type': 'postgres',
            'url': DATABASE_URL
        }
    else:
        return {
            'type': 'sqlite',
            'url': 'bot_database.db'
        }
