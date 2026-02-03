import sqlite3

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

# Check boletos with message_id
cursor.execute("""
    SELECT nome_arquivo, categoria, message_id, file_id 
    FROM documentos 
    WHERE nome_arquivo LIKE '%boleto%' COLLATE NOCASE
    ORDER BY nome_arquivo
""")

print('Boletos no banco de dados:')
print('-' * 80)
for row in cursor.fetchall():
    nome = row[0]
    categoria = row[1]
    message_id = row[2]
    file_id = row[3][:30] if row[3] else 'None'
    status = '✅ TEM message_id' if message_id else '❌ SEM message_id'
    print(f'{status} | {nome}')
    print(f'  categoria: {categoria} | message_id: {message_id} | file_id: {file_id}...')
    print()

# Count total with and without message_id
cursor.execute("SELECT COUNT(*) FROM documentos WHERE message_id IS NOT NULL")
with_msg_id = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM documentos WHERE message_id IS NULL")
without_msg_id = cursor.fetchone()[0]

print('-' * 80)
print(f'RESUMO GERAL:')
print(f'  Total documentos: {with_msg_id + without_msg_id}')
print(f'  ✅ Com message_id: {with_msg_id}')
print(f'  ❌ Sem message_id: {without_msg_id}')

conn.close()
