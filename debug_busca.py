"""
Debug da busca
"""

import sys
sys.path.insert(0, 'assistente-ranny')

from database_sqlite import buscar_documentos

print("=" * 80)
print("🔍 DEBUG BUSCA")
print("=" * 80)

docs = buscar_documentos(query='GRN', limit=3)

print(f"\n✅ Encontrados: {len(docs)} documentos")

for i, doc in enumerate(docs, 1):
    print(f"\n{i}. Documento:")
    print(f"   Type: {type(doc)}")
    print(f"   Keys: {list(doc.keys()) if hasattr(doc, 'keys') else 'N/A'}")
    print(f"   nome_arquivo: {doc.get('nome_arquivo')}")
    print(f"   resumo: {doc.get('resumo')[:50]}...")
