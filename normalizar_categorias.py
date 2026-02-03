"""
Normaliza categorias no banco de dados (maiúsculas -> minúsculas)
"""

import sqlite3

DB_PATH = 'bot_database.db'

print("=" * 80)
print("🔧 NORMALIZANDO CATEGORIAS NO BANCO")
print("=" * 80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Busca todas as categorias únicas
cursor.execute("SELECT DISTINCT categoria FROM documentos WHERE categoria IS NOT NULL")
categorias = cursor.fetchall()

print(f"\n📊 Categorias encontradas: {len(categorias)}")
for cat in categorias:
    print(f"   • {cat[0]}")

# Atualiza para minúsculas
print("\n🔄 Atualizando para minúsculas...")
cursor.execute("UPDATE documentos SET categoria = LOWER(categoria) WHERE categoria IS NOT NULL")

affected = cursor.rowcount
conn.commit()

print(f"✅ {affected} registros atualizados")

# Verifica resultado
cursor.execute("SELECT DISTINCT categoria FROM documentos WHERE categoria IS NOT NULL")
categorias_novas = cursor.fetchall()

print(f"\n📊 Categorias após normalização:")
for cat in categorias_novas:
    print(f"   • {cat[0]}")

conn.close()

print("\n" + "=" * 80)
print("✅ Normalização concluída!")
print("=" * 80)
