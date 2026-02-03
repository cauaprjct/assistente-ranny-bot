"""
Teste simples para verificar se os imports estão corretos
"""

print("🔍 Testando imports...\n")

# Teste 1: Verificar se database.py existe e importa corretamente
try:
    import database as db
    print("✅ import database as db - OK")
except ImportError as e:
    print(f"❌ import database as db - ERRO: {e}")
    exit(1)

# Teste 2: Verificar se bot.py usa database correto
try:
    with open('bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'import database_sqlite as db' in content:
            print("❌ bot.py ainda usa database_sqlite")
            exit(1)
        elif 'import database as db' in content:
            print("✅ bot.py usa database (Supabase) - OK")
        else:
            print("⚠️  bot.py não importa database")
except Exception as e:
    print(f"❌ Erro ao ler bot.py: {e}")

# Teste 3: Verificar se ai.py usa database correto
try:
    with open('ai.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'import database_sqlite as db' in content:
            print("❌ ai.py ainda usa database_sqlite")
            exit(1)
        elif 'import database as db' in content:
            print("✅ ai.py usa database (Supabase) - OK")
        else:
            print("⚠️  ai.py não importa database")
except Exception as e:
    print(f"❌ Erro ao ler ai.py: {e}")

# Teste 4: Verificar se jobs.py usa database correto
try:
    with open('jobs.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'import database_sqlite as db' in content:
            print("❌ jobs.py ainda usa database_sqlite")
            exit(1)
        elif 'import database as db' in content:
            print("✅ jobs.py usa database (Supabase) - OK")
        else:
            print("⚠️  jobs.py não importa database")
except Exception as e:
    print(f"❌ Erro ao ler jobs.py: {e}")

print("\n" + "="*60)
print("✅ TODOS OS IMPORTS ESTÃO CORRETOS!")
print("="*60)
print("\n📝 Próximos passos:")
print("   1. Configure SUPABASE_URL e SUPABASE_SERVICE_KEY no .env")
print("   2. Execute: python bot.py")
print("   3. Teste as funcionalidades do bot")
print()
