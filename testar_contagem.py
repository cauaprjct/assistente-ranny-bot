"""
Testa a função de contagem
"""

import sys
sys.path.insert(0, 'assistente-ranny')

import database_adapter as db

print("=" * 80)
print("🔍 TESTE DE CONTAGEM")
print("=" * 80)

# Testa contagem
print("\n📊 Testando contar_documentos_por_categoria()...")
try:
    stats = db.contar_documentos_por_categoria()
    print(f"✅ Resultado: {stats}")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Testa busca normal
print("\n📊 Testando buscar_documentos()...")
try:
    docs = db.buscar_documentos(termo='', limit=100)
    print(f"✅ Encontrados: {len(docs)} documentos")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
