# 🔄 Migração para Supabase

## ✅ Mudanças Realizadas

O bot foi padronizado para usar **Supabase** como banco de dados único.

### Arquivos Alterados:
- ✅ `bot.py` - Agora usa `import database as db`
- ✅ `ai.py` - Agora usa `import database as db`
- ✅ `jobs.py` - Agora usa `import database as db`
- ✅ `onedrive.py` - Já usava Supabase

### Arquivo Obsoleto:
- ⚠️ `database_sqlite.py` - Não é mais usado (pode ser removido)
- ⚠️ `bot_database.db` - Banco SQLite local (não é mais usado)

---

## 🔧 Configuração Necessária

### 1. Variáveis de Ambiente

Certifique-se de ter estas variáveis no `.env`:

```env
# Supabase (OBRIGATÓRIO)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_KEY=sua_service_key_aqui
# OU
SUPABASE_ANON_KEY=sua_anon_key_aqui

# Telegram (OBRIGATÓRIO)
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
GROUP_ID=-1003536252896

# Gemini AI (OBRIGATÓRIO)
GEMINI_API_KEY=sua_chave_gemini

# Tópicos do Grupo
TOPIC_CHAT=47
TOPIC_FINANCEIRO=2
TOPIC_EMPRESA=3
TOPIC_JURIDICO=5
TOPIC_PESSOAL=4
TOPIC_FUNCIONARIOS=6
TOPIC_MANUTENCAO=7
TOPIC_OUTROS=8

# OneDrive (OPCIONAL)
MICROSOFT_CLIENT_ID=seu_client_id_azure
MICROSOFT_CLIENT_SECRET=seu_client_secret_azure
```

### 2. Obter Credenciais Supabase

1. Acesse [supabase.com](https://supabase.com)
2. Faça login ou crie uma conta
3. Vá em **Project Settings** > **API**
4. Copie:
   - **URL**: `https://seu-projeto.supabase.co`
   - **service_role key** (recomendado) ou **anon key**

---

## 📊 Schema do Banco de Dados

As tabelas já estão criadas no Supabase:

### Tabelas Existentes:

1. **fechamentos** - Fechamentos de caixa diários
2. **lembretes** - Lembretes e alertas
3. **documentos** - Documentos classificados
4. **vencimentos** - Contas a pagar/vencimentos
5. **funcionarios** - Cadastro de funcionários
6. **relatorios_temp** - Relatórios temporários (TTL 24h)
7. **oauth_tokens** - Tokens OAuth (OneDrive)

### Verificar Schema:

```sql
-- Listar todas as tabelas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Ver estrutura de uma tabela
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'documentos';
```

---

## 🔄 Migração de Dados (Se Necessário)

Se você tinha dados no SQLite local (`bot_database.db`), pode migrar:

### Opção 1: Migração Manual via SQL

1. Exporte dados do SQLite:
```bash
sqlite3 bot_database.db .dump > backup.sql
```

2. Adapte o SQL para PostgreSQL (Supabase)
3. Execute no Supabase SQL Editor

### Opção 2: Migração via Python

```python
import sqlite3
from database import get_supabase

# Conecta SQLite
sqlite_conn = sqlite3.connect('bot_database.db')
sqlite_conn.row_factory = sqlite3.Row
cursor = sqlite_conn.cursor()

# Conecta Supabase
supabase = get_supabase()

# Exemplo: Migrar fechamentos
cursor.execute('SELECT * FROM fechamentos')
for row in cursor.fetchall():
    supabase.table('fechamentos').insert({
        'valor': row['total_vendas'],
        'data': row['data_fechamento'],
        'observacao': row['observacoes']
    }).execute()

print("Migração concluída!")
```

---

## ✅ Testar Conexão

Execute este teste para verificar se está tudo configurado:

```python
from database import test_connection

if test_connection():
    print("✅ Conexão com Supabase OK!")
else:
    print("❌ Erro na conexão com Supabase")
    print("Verifique SUPABASE_URL e SUPABASE_SERVICE_KEY no .env")
```

Ou use o endpoint de health check:

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "error": null
    }
  }
}
```

---

## 🚀 Deploy no Railway

O Railway já está configurado para usar Supabase. Certifique-se de:

1. Adicionar as variáveis de ambiente no Railway:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_API_KEY`
   - Todas as `TOPIC_*`

2. O Railway vai usar automaticamente o Supabase (não precisa de banco local)

---

## 🔒 Segurança

### Row Level Security (RLS)

Todas as tabelas têm RLS habilitado. Para desenvolvimento, você pode desabilitar temporariamente:

```sql
-- Desabilitar RLS (apenas desenvolvimento!)
ALTER TABLE fechamentos DISABLE ROW LEVEL SECURITY;
ALTER TABLE lembretes DISABLE ROW LEVEL SECURITY;
ALTER TABLE documentos DISABLE ROW LEVEL SECURITY;
ALTER TABLE vencimentos DISABLE ROW LEVEL SECURITY;
ALTER TABLE funcionarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE relatorios_temp DISABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_tokens DISABLE ROW LEVEL SECURITY;
```

**⚠️ IMPORTANTE:** Em produção, configure políticas RLS adequadas!

### Service Key vs Anon Key

- **service_role key**: Bypass RLS, acesso total (use no backend)
- **anon key**: Respeita RLS (use no frontend)

Para este bot, use **service_role key** pois ele precisa de acesso total.

---

## 📝 Vantagens do Supabase

✅ **Backup Automático** - Dados seguros na nuvem
✅ **Acesso Remoto** - Funciona de qualquer lugar
✅ **PostgreSQL** - Banco robusto e escalável
✅ **Dashboard Web** - Visualize dados facilmente
✅ **API REST** - Acesso via HTTP se necessário
✅ **Realtime** - Suporte a subscriptions (futuro)
✅ **Storage** - Pode guardar arquivos grandes (futuro)

---

## 🐛 Troubleshooting

### Erro: "SUPABASE_URL e SUPABASE_SERVICE_KEY são obrigatórios"

**Solução:** Adicione as variáveis no `.env`:
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_KEY=sua_service_key
```

### Erro: "relation 'fechamentos' does not exist"

**Solução:** As tabelas não foram criadas. Execute o SQL de criação no Supabase SQL Editor.

### Erro: "new row violates row-level security policy"

**Solução:** Desabilite RLS temporariamente ou configure políticas adequadas.

### Erro de conexão timeout

**Solução:** Verifique se o projeto Supabase está ativo (não pausado).

---

## 📚 Recursos

- [Documentação Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Data da Migração:** 18/01/2026
**Versão:** 3.2.0
