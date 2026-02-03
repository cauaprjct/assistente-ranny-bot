"""Verifica dados no banco SQLite"""
import sqlite3

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

# Lista todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=" * 60)
print("📊 VERIFICAÇÃO DO BANCO DE DADOS SQLite")
print("=" * 60)
print()

if not tables:
    print("✅ Banco vazio - nenhuma tabela encontrada")
else:
    print(f"Tabelas encontradas: {len(tables)}")
    print()
    
    total_registros = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        total_registros += count
        
        status = "✅ VAZIO" if count == 0 else f"⚠️  {count} registros"
        print(f"  {table_name}: {status}")
        
        # Se tiver registros, mostra alguns detalhes
        if count > 0:
            cursor.execute(f'SELECT * FROM {table_name} LIMIT 3')
            rows = cursor.fetchall()
            for row in rows:
                print(f"    - {row}")
    
    print()
    print(f"Total de registros em todas as tabelas: {total_registros}")
    
    if total_registros == 0:
        print()
        print("✅ TODAS AS TABELAS ESTÃO VAZIAS!")
        print("   O bot não tem nenhum dado de teste salvo.")
    else:
        print()
        print("⚠️  ATENÇÃO: Existem dados salvos no banco!")

conn.close()

print()
print("=" * 60)
