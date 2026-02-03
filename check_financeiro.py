import json

with open('relatorio_upload_backup.json', encoding='utf-8') as f:
    data = json.load(f)

financeiro = [f for f in data['arquivos'] if f['categoria'] == 'FINANCEIRO']
print(f'Total FINANCEIRO files: {len(financeiro)}')
print('\nFiles:')
for i, f in enumerate(financeiro, 1):
    print(f"{i}. {f['nome']}")
