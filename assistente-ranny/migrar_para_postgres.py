"""
Script para migrar dados do SQLite para PostgreSQL
E reindexar arquivos usando o relatório JSON
"""
import os
import sys
import json

# Adiciona o diretório assistente-ranny ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistente-ranny'))

# Configura DATABASE_URL para usar PostgreSQL
# No Render, isso já vem configurado automaticamente
if not os.getenv('DATABASE_URL'):
    print("⚠️ DATABASE_URL não configurada. Configure antes de rodar.")
    print("   export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
    sys.exit(1)

print("🔄 MIGRAÇÃO PARA POSTGRESQL")
print("=" * 80)

# Importa PostgreSQL
try:
    import database_postgres as db_postgres
    print("✅ Módulo PostgreSQL importado")
except ImportError as e:
    print(f"❌ Erro ao importar PostgreSQL: {e}")
    print("   Instale: pip install psycopg2-binary")
    sys.exit(1)

# Inicializa banco PostgreSQL
print("\n📊 Inicializando tabelas PostgreSQL...")
if not db_postgres.init_database():
    print("❌ Falha ao inicializar PostgreSQL")
    sys.exit(1)

# Carrega relatório de upload
print("\n📂 Carregando relatório de upload...")
# Tenta vários caminhos possíveis
possible_paths = [
    'relatorio_upload_backup.json',  # Raiz do projeto (onde o script está)
    os.path.join(os.path.dirname(__file__), 'relatorio_upload_backup.json'),  # Mesma pasta
    'assistente-ranny/relatorio_upload_backup.json',  # Pasta assistente-ranny
    os.path.join(os.path.dirname(__file__), '..', 'relatorio_upload_backup.json'),  # Um nível acima
]

relatorio_path = None
for path in possible_paths:
    if os.path.exists(path):
        relatorio_path = path
        print(f"✅ Relatório encontrado em: {path}")
        break

if not relatorio_path:
    print(f"❌ Relatório não encontrado em nenhum dos caminhos:")
    for path in possible_paths:
        print(f"   - {os.path.abspath(path)}")
    print("\n⚠️ CONTINUANDO SEM MIGRAÇÃO - Banco ficará vazio")
    print("   Para indexar arquivos, rode o script manualmente com o relatório")
    sys.exit(0)  # Não falha o deploy, apenas avisa

try:
    with open(relatorio_path, 'r', encoding='utf-8') as f:
        relatorio = json.load(f)
    print(f"✅ Relatório carregado: {len(relatorio.get('arquivos', []))} arquivos")
except Exception as e:
    print(f"❌ Erro ao carregar relatório: {e}")
    sys.exit(1)

# Verifica estado atual do banco
print("\n📊 Verificando banco PostgreSQL...")
try:
    total_atual = db_postgres.contar_documentos()
    print(f"   Documentos no banco: {total_atual}")
except Exception as e:
    print(f"❌ Erro ao verificar banco: {e}")
    sys.exit(1)

# Indexa arquivos do relatório
print("\n🔄 Indexando arquivos no PostgreSQL...")
arquivos = relatorio.get('arquivos', [])
total = 0
sucesso = 0
ja_existe = 0
sem_message_id = 0
erros = []

for arquivo in arquivos:
    total += 1
    nome = arquivo.get('nome')
    message_id = arquivo.get('message_id')
    file_id = arquivo.get('file_id')
    categoria = arquivo.get('categoria', '').lower()
    extensao = arquivo.get('extensao', '')
    topico = arquivo.get('topico')
    
    # Pula se não tem message_id
    if not message_id:
        sem_message_id += 1
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
        doc_id = db_postgres.adicionar_documento(
            nome_arquivo=nome,
            tipo_documento=tipo_doc,
            categoria=categoria,
            file_id=file_id,
            message_id=message_id,
            topic_id=topico
        )
        
        if doc_id:
            sucesso += 1
            if sucesso % 50 == 0:
                print(f"   ✅ {sucesso} arquivos indexados...")
        else:
            erros.append(f"Erro ao indexar: {nome}")
            
    except Exception as e:
        erro_msg = f"Erro ao indexar {nome}: {str(e)}"
        erros.append(erro_msg)
        # Verifica se é erro de duplicata
        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
            ja_existe += 1
        else:
            print(f"   ❌ {erro_msg}")

# Resumo
print("\n" + "=" * 80)
print("📊 RESUMO DA MIGRAÇÃO")
print("=" * 80)
print(f"Total de arquivos no relatório: {total}")
print(f"✅ Indexados com sucesso: {sucesso}")
print(f"⏭️  Já existiam no banco: {ja_existe}")
print(f"⚠️  Sem message_id: {sem_message_id}")
print(f"❌ Erros: {len(erros) - ja_existe}")

if erros and len(erros) > ja_existe:
    print(f"\n⚠️ Primeiros erros:")
    for erro in erros[:5]:
        if 'duplicate' not in erro.lower() and 'unique' not in erro.lower():
            print(f"   - {erro}")

# Verifica total final
print(f"\n📈 Total no banco agora: {db_postgres.contar_documentos()}")

# Testa busca
print("\n🔍 Testando busca por 'boleto'...")
try:
    boletos = db_postgres.buscar_documentos(query='boleto')
    print(f"✅ Encontrados: {len(boletos)} boletos")
    if boletos:
        print("   Exemplos:")
        for i, boleto in enumerate(boletos[:3]):
            print(f"   {i+1}. {boleto['nome_arquivo']} (msg_id: {boleto.get('message_id')})")
except Exception as e:
    print(f"❌ Erro ao testar busca: {e}")

print("\n" + "=" * 80)
print("✅ MIGRAÇÃO CONCLUÍDA!")
print("=" * 80)
