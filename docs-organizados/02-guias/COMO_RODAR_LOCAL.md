# 🚀 Como Rodar o Assistente Ranny

## ⚡ Início Rápido

### 1. Instalar Dependências

```bash
cd assistente-ranny
pip install -r requirements.txt
```

**Nota:** A biblioteca `supabase` pode falhar no Windows (normal!). O bot usará SQLite automaticamente.

---

### 2. Configurar Variáveis de Ambiente

O arquivo `.env` já está configurado com:
- ✅ Token do Telegram
- ✅ API Key do Gemini
- ✅ Credenciais do Supabase
- ✅ IDs dos tópicos do grupo

**Não precisa fazer nada!** 🎉

---

### 3. Rodar o Bot

```bash
python bot.py
```

**Saída esperada:**
```
🔵 Usando Supabase (PostgreSQL na nuvem)
⚠️  Erro ao importar Supabase: cannot import name 'AuthorizationError'...
📦 Caindo de volta para SQLite local
16:12:27 | INFO | __main__ | ============================================================
16:12:27 | INFO | __main__ | 🤖 ASSISTENTE RANNY V3
16:12:27 | INFO | __main__ | ============================================================
16:12:27 | INFO | __main__ | ✅ Supabase conectado
16:12:27 | INFO | jobs | 📱 Bot do Telegram configurado para jobs
16:12:27 | INFO | __main__ | ✅ Handlers configurados
16:12:27 | INFO | scheduler | 📅 Scheduler criado com timezone America/Sao_Paulo
16:12:27 | INFO | scheduler | ✅ Scheduler iniciado
16:12:27 | INFO | scheduler | 📅 Job 'lembretes' agendado a cada 1m
16:12:27 | INFO | scheduler | 📅 Job 'vencimentos' agendado para 08:00 (*)
16:12:27 | INFO | scheduler | 📅 Job 'resumo_semanal' agendado para 20:00 (sun)
16:12:27 | INFO | __main__ | ✅ Jobs agendados
16:12:29 | INFO | __main__ | ✅ Bot online!
16:12:29 | INFO | __main__ | ✅ Servidor web: http://localhost:8000
16:12:29 | INFO | __main__ | ✅ Health check: http://localhost:8000/health
16:12:29 | INFO | __main__ |
16:12:29 | INFO | __main__ | Pressione Ctrl+C para parar
```

---

### 4. Testar o Bot

Abra o Telegram e envie mensagens para o bot no grupo configurado:

**Comandos disponíveis:**
- `/start` - Inicia o bot
- `/help` - Mostra ajuda
- Envie documentos (PDF, Excel, Word) - Bot classifica automaticamente
- Envie boletos - Bot extrai dados e cria vencimentos
- Converse naturalmente - IA responde

---

## 🧪 Testar o Adaptador de Banco

```bash
python test_database_adapter.py
```

Verifica se o sistema híbrido SQLite/Supabase está funcionando.

---

## 🌐 Acessar Servidor Web

Enquanto o bot estiver rodando:

- **Health Check:** http://localhost:8000/health
- **Documentação API:** http://localhost:8000/docs

---

## 🛑 Parar o Bot

Pressione `Ctrl+C` no terminal onde o bot está rodando.

---

## 📊 Banco de Dados

### Localmente (Desenvolvimento)
- **Tipo:** SQLite
- **Arquivo:** `bot_database.db`
- **Localização:** Pasta `assistente-ranny/`

### Railway (Produção)
- **Tipo:** Supabase (PostgreSQL)
- **URL:** https://yaadvmghaccmakyqmhva.supabase.co
- **Dashboard:** https://supabase.com/dashboard

---

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'telegram'"

**Solução:**
```bash
pip install python-telegram-bot --upgrade
```

---

### Erro: "supabase library not installed"

**Isso é normal no Windows!** O bot usa SQLite automaticamente.

Se quiser forçar instalação do Supabase (não recomendado):
1. Instalar Visual Studio Build Tools
2. Instalar Microsoft Visual C++ 14.0+
3. `pip install supabase`

---

### Bot não responde no Telegram

**Verificar:**
1. Token do bot está correto no `.env`
2. Bot foi adicionado ao grupo
3. Bot tem permissões de administrador
4. `GROUP_ID` está correto no `.env`

**Como pegar o GROUP_ID:**
1. Adicione o bot @RawDataBot ao grupo
2. Ele mostrará o ID do grupo
3. Copie e cole no `.env`

---

### Erro: "Cannot connect to Supabase"

**No Windows:** Normal! Bot usa SQLite.

**No Railway:** Verificar variáveis de ambiente:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

---

## 📝 Logs

O bot gera logs detalhados no console. Para salvar em arquivo:

```bash
python bot.py > bot.log 2>&1
```

---

## 🚀 Deploy no Railway

1. **Fazer commit:**
```bash
git add .
git commit -m "Bot pronto para deploy"
git push
```

2. **Configurar Railway:**
- Criar novo projeto
- Conectar repositório GitHub
- Adicionar variáveis de ambiente do `.env`
- Deploy automático!

3. **Verificar logs no Railway:**
```
🔵 Usando Supabase (PostgreSQL na nuvem)
✅ Supabase conectado
✅ Bot online!
```

---

## 📚 Documentação Adicional

- `SOLUCAO_HIBRIDA_IMPLEMENTADA.md` - Detalhes técnicos da implementação
- `MIGRACAO_SUPABASE.md` - Guia de migração para Supabase
- `README.md` - Documentação completa do projeto

---

**Última atualização:** 18/01/2026
**Status:** ✅ Bot funcionando perfeitamente
