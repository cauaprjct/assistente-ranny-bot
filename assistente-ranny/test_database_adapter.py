"""
Teste do Adaptador de Banco de Dados
"""

print("=" * 60)
print("🧪 TESTE DO ADAPTADOR DE BANCO DE DADOS")
print("=" * 60)
print()

# Teste 1: Importar o adaptador
print("1️⃣  Testando import do adaptador...")
try:
    import database_adapter as db
    print("   ✅ Adaptador importado com sucesso!")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    exit(1)

# Teste 2: Verificar qual banco está sendo usado
print()
print("2️⃣  Verificando banco de dados em uso...")
try:
    info = db.get_db_info()
    print(f"   📊 Tipo: {info['type'].upper()}")
    print(f"   🔗 URL/Path: {info['url']}")
    
    if info['using_supabase']:
        print("   ✅ Usando Supabase (PostgreSQL na nuvem)")
    else:
        print("   ✅ Usando SQLite (banco local)")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 3: Testar funções básicas
print()
print("3️⃣  Testando funções do banco...")
try:
    # Testa se as funções existem
    funcoes = [
        'add_fechamento',
        'get_fechamentos',
        'add_lembrete',
        'get_lembretes_ativos',
        'add_documento',
        'buscar_documentos',
        'add_vencimento',
        'get_vencimentos_proximos'
    ]
    
    for func in funcoes:
        if hasattr(db, func):
            print(f"   ✅ {func}")
        else:
            print(f"   ❌ {func} - NÃO ENCONTRADA")
    
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 4: Testar conexão (se Supabase)
print()
print("4️⃣  Testando conexão...")
try:
    if db.USE_SUPABASE:
        if hasattr(db, 'test_connection'):
            if db.test_connection():
                print("   ✅ Conexão com Supabase OK!")
            else:
                print("   ❌ Falha na conexão com Supabase")
                print("   ⚠️  Verifique SUPABASE_URL e SUPABASE_SERVICE_KEY")
        else:
            print("   ⚠️  Função test_connection não disponível")
    else:
        print("   ✅ SQLite não precisa de teste de conexão")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print()
print("=" * 60)
print("✅ TESTE CONCLUÍDO!")
print("=" * 60)
print()

# Resumo
info = db.get_db_info()
if info['using_supabase']:
    print("🎉 O bot está configurado para usar SUPABASE!")
    print("   Seus dados estarão seguros na nuvem.")
    print()
else:
    print("📝 O bot está usando SQLite local.")
    print("   Para usar Supabase:")
    print("   1. Configure SUPABASE_URL no .env")
    print("   2. Configure SUPABASE_SERVICE_KEY no .env")
    print("   3. Instale: pip install supabase")
    print("   4. Reinicie o bot")
    print()
