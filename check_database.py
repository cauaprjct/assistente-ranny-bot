import sqlite3

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

# Check total documents
cursor.execute('SELECT COUNT(*) FROM documentos')
total = cursor.fetchone()[0]
print(f'Total documentos no banco: {total}')

# Check if message_id and topic_id columns exist
cursor.execute('PRAGMA table_info(documentos)')
columns = cursor.fetchall()
print(f'\nColunas na tabela documentos:')
for col in columns:
    print(f'  - {col[1]} ({col[2]})')

# Check first 10 documents
cursor.execute('SELECT nome_arquivo, categoria, file_id FROM documentos LIMIT 10')
print(f'\nPrimeiros 10 documentos:')
for row in cursor.fetchall():
    file_id_preview = row[2][:30] if row[2] else 'None'
    print(f'  - {row[0]} | {row[1]} | file_id={file_id_preview}...')

# Search for "boleto"
cursor.execute("SELECT nome_arquivo, categoria FROM documentos WHERE nome_arquivo LIKE '%boleto%' COLLATE NOCASE OR resumo LIKE '%boleto%' COLLATE NOCASE")
boletos = cursor.fetchall()
print(f'\nDocumentos com "boleto": {len(boletos)}')
for row in boletos:
    print(f'  - {row[0]} | {row[1]}')

conn.close()
