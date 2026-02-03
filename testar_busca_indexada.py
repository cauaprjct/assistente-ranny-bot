"""
Testa se os documentos indexados podem ser buscados
"""

import sys
sys.path.insert(0, 'assistente-ranny')

import database_adapter as db

print("=" * 80)
print("🔍 TESTE DE BUSCA DE DOCUMENTOS INDEXADOS")
print("=" * 80)

# Testa busca vazia (todos os documentos)
print("\n📊 Buscando TODOS os documentos...")
todos = db.buscar_documentos(termo='', limit=100)
print(f"✅ Encontrados: {len(todos)} documentos")

if todos:
    print("\n📄 Primeiros 5 documentos:")
    for i, doc in enumerate(todos[:5], 1):
        print(f"\n{i}. {doc.get('descricao', 'Sem descrição')}")
        print(f"   📂 Categoria: {doc.get('categoria', 'N/A')}")
        print(f"   📝 Resumo: {doc.get('resumo', 'N/A')[:80]}...")
        print(f"   🆔 File ID: {doc.get('file_id', 'N/A')[:30]}...")

# Testa busca por termo
print("\n" + "=" * 80)
print("🔍 Buscando por 'GRN'...")
grn_docs = db.buscar_documentos(termo='GRN', limit=20)
print(f"✅ Encontrados: {len(grn_docs)} documentos")

if grn_docs:
    print("\n📄 Documentos encontrados:")
    for i, doc in enumerate(grn_docs[:3], 1):
        print(f"\n{i}. {doc.get('descricao', 'Sem descrição')}")
        print(f"   📂 Categoria: {doc.get('categoria', 'N/A')}")

# Testa busca por categoria
print("\n" + "=" * 80)
print("🔍 Buscando por categoria 'empresa'...")
empresa_docs = db.buscar_documentos(termo='', categoria='empresa', limit=20)
print(f"✅ Encontrados: {len(empresa_docs)} documentos")

# Testa busca por termo específico
print("\n" + "=" * 80)
print("🔍 Buscando por 'contrato'...")
contrato_docs = db.buscar_documentos(termo='contrato', limit=20)
print(f"✅ Encontrados: {len(contrato_docs)} documentos")

# Testa busca por 'pdf'
print("\n" + "=" * 80)
print("🔍 Buscando por 'pdf'...")
pdf_docs = db.buscar_documentos(termo='pdf', limit=20)
print(f"✅ Encontrados: {len(pdf_docs)} documentos")

print("\n" + "=" * 80)
print("✅ Teste concluído!")
print("=" * 80)
