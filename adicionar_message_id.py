"""
Adiciona campo message_id na tabela documentos
"""

import sqlite3

DB_PATH = 'bot_database.db'

print("=" * 80)
print("🔧 ADICIONANDO CAMPO message_id")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verifica se a coluna já existe
cursor.execute("PRAGMA table_info(documentos)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print(f"\n📊 Colunas atuais: {column_names}")

if 'message_id' not in column_names:
    print("\n🔄 Adicionando coluna message_id...")
    cursor.execute("ALTER TABLE documentos ADD COLUMN message_id INTEGER")
    conn.commit()
    print("✅ Coluna adicionada!")
else:
    print("\n✅ Coluna message_id já existe!")

if 'topic_id' not in column_names:
    print("\n🔄 Adicionando coluna topic_id...")
    cursor.execute("ALTER TABLE documentos ADD COLUMN topic_id INTEGER")
    conn.commit()
    print("✅ Coluna adicionada!")
else:
    print("\n✅ Coluna topic_id já existe!")

conn.close()

print("\n" + "=" * 80)
print("✅ Schema atualizado!")
print("=" * 80)
