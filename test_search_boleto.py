import sys
sys.path.insert(0, 'assistente-ranny')

from database_sqlite import buscar_documentos

# Test search for "boleto"
print('Testando busca por "boleto":')
print('=' * 80)

resultados = buscar_documentos(query='boleto')
print(f'Resultados encontrados: {len(resultados)}')
print()

if resultados:
    for doc in resultados:
        print(f'✅ {doc["nome_arquivo"]}')
        print(f'   Categoria: {doc["categoria"]}')
        print(f'   Message ID: {doc.get("message_id", "N/A")}')
        print(f'   File ID: {doc.get("file_id", "N/A")[:30]}...')
        print()
else:
    print('❌ Nenhum resultado encontrado!')
    print()
    print('Verificando se há documentos no banco...')
    todos = buscar_documentos(query='')
    print(f'Total de documentos no banco: {len(todos)}')
