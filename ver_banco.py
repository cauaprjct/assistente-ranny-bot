"""
Visualiza dados do banco SQLite
"""

import sqlite3

DB_PATH = 'bot_database.db'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("📊 DOCUMENTOS NO BANCO")
print("=" * 80)

cursor.execute("SELECT * FROM documentos LIMIT 3")
docs = cursor.fetchall()

for i, doc in enumerate(docs, 1):
    print(f"\n{i}. ID: {doc['id']}")
    print(f"   Nome: {doc['nome_arquivo']}")
    print(f"   Tipo: {doc['tipo_documento']}")
    print(f"   Categoria: {doc['categoria']}")
    print(f"   Resumo: {doc['resumo'][:100]}...")
    print(f"   File ID: {doc['file_id'][:40]}...")

conn.close()
