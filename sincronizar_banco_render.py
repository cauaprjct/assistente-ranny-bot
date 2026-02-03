"""
Script para sincronizar o banco local com o Render
Lê o relatorio_upload_backup.json e indexa todos os arquivos no banco
"""

import json
import sys
sys.path.insert(0, 'assistente-ranny')

from database_sqlite import adicionar_documento, buscar_documentos

def sincronizar_banco():
    """Sincroniza banco usando o relatório de upload"""
    
    print("🔄 SINCRONIZAÇÃO DO BANCO DE DADOS")
    print("=" * 80)
    
    # Carrega relatório
    print("\n📂 Carregando relatório de upload...")
    try:
        with open('relatorio_upload_backup.json', 'r', encoding='utf-8') as f:
            relatorio = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo relatorio_upload_backup.json não encontrado!")
        return False
    
    arquivos = relatorio.get('arquivos', [])
    print(f"✅ Relatório carregado: {len(arquivos)} arquivos")
    
    # Verifica estado atual do banco
    print("\n📊 Verificando banco atual...")
    docs_atuais = buscar_documentos(query='', limit=1000)
    print(f"   Documentos no banco: {len(docs_atuais)}")
    
    # Cria set de arquivos já indexados (por nome)
    arquivos_indexados = {doc['nome_arquivo'] for doc in docs_atuais}
    
    # Indexa arquivos que têm message_id
    print("\n🔄 Indexando arquivos...")
    total = 0
    sucesso = 0
    ja_existe = 0
    sem_message_id = 0
    
    for arquivo in arquivos:
        total += 1
        nome = arquivo.get('nome')
        message_id = arquivo.get('message_id')
        file_id = arquivo.get('file_id')
        categoria = arquivo.get('categoria', '').lower()
        extensao = arquivo.get('extensao', '')
        
        # Pula se não tem message_id
        if not message_id:
            sem_message_id += 1
            continue
        
        # Pula se já existe
        if nome in arquivos_indexados:
            ja_existe += 1
            continue
        
        # Determina tipo de documento
        tipo_doc = None
        if extensao in ['.pdf']:
            tipo_doc = 'pdf'
        elif extensao in ['.doc', '.docx']:
            tipo_doc = 'documento'
        elif extensao in ['.xls', '.xlsx', '.csv']:
            tipo_doc = 'planilha'
        elif extensao in ['.jpg', '.jpeg', '.png', '.gif']:
            tipo_doc = 'imagem'
        
        # Adiciona ao banco
        try:
            doc_id = adicionar_documento(
                nome_arquivo=nome,
                tipo_documento=tipo_doc,
                categoria=categoria,
                file_id=file_id,
                message_id=message_id,
                topic_id=arquivo.get('topico')
            )
            
            if doc_id:
                sucesso += 1
                if sucesso % 50 == 0:
                    print(f"   ✅ {sucesso} arquivos indexados...")
            else:
                print(f"   ❌ Erro ao indexar: {nome}")
                
        except Exception as e:
            print(f"   ❌ Erro ao indexar {nome}: {e}")
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DA SINCRONIZAÇÃO")
    print("=" * 80)
    print(f"Total de arquivos no relatório: {total}")
    print(f"✅ Indexados com sucesso: {sucesso}")
    print(f"⏭️  Já existiam no banco: {ja_existe}")
    print(f"⚠️  Sem message_id: {sem_message_id}")
    print(f"\n📈 Total no banco agora: {len(docs_atuais) + sucesso}")
    
    # Testa busca
    print("\n🔍 Testando busca por 'boleto'...")
    boletos = buscar_documentos(query='boleto')
    print(f"✅ Encontrados: {len(boletos)} boletos")
    
    return True

if __name__ == '__main__':
    sincronizar_banco()
