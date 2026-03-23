# 🚀 Guia de Deploy no Railway - Assistente Ranny V3

Este guia detalha os passos para fazer o deploy do Assistente Ranny no Railway.

## ✅ Pré-requisitos

Antes de começar, certifique-se de ter:

1. **Conta no Railway** - [railway.app](https://railway.app)
2. **Conta no GitHub** - Para conectar o repositório
3. **Git instalado** - Para push do código
4. **Credenciais configuradas**:
   - Token do Bot Telegram (do @BotFather)
   - Chave API do Gemini
   - Projeto Supabase configurado com schema SQL

## 📋 Checklist de Arquivos

Verifique se todos os arquivos necessários estão presentes:

- [x] `bot.py` - Bot principal + servidor web
- [x] `ai.py` - Integração Gemini
- [x] `database.py` - Banco Supabase
- [x] `config.py` - Configurações centralizadas
- [x] `scheduler.py` - Agendador de tarefas
- [x] `jobs.py` - Jobs automáticos
- [x] `web.py` - FastAPI (relatórios, health check)
- [x] `onedrive.py` - Integração OneDrive
- [x] `date_parser.py` - Parser de datas
- [x] `Procfile` - Comando de start
- [x] `railway.toml` - Configuração Railway
- [x] `requirements.txt` - Dependências Python
- [x] `.gitignore` - Arquivos ignorados

## 🔧 Passo a Passo

### 1. Criar Repositório no GitHub

```bash
# Na pasta assistente-ranny
git init
git add .
git commit -m "Initial commit - Assistente Ranny V3"

# Criar repositório no GitHub e conectar
git remote add origin https://github.com/SEU_USUARIO/assistente-ranny.git
git branch -M main
git push -u origin main
```

### 2. Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Autorize o Railway a acessar seu GitHub
5. Selecione o repositório `assistente-ranny`

### 3. Configurar Variáveis de Ambiente

No painel do Railway, vá em **Settings > Variables** e adicione:

#### Obrigatórias

```env
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
GEMINI_API_KEY=sua_chave_gemini
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_anon_key
SUPABASE_SERVICE_KEY=sua_service_key
GROUP_ID=-1003536252896
```

#### Tópicos do Grupo Telegram

```env
TOPIC_CHAT=47
TOPIC_FINANCEIRO=2
TOPIC_EMPRESA=3
TOPIC_JURIDICO=5
TOPIC_PESSOAL=4
TOPIC_FUNCIONARIOS=6
TOPIC_MANUTENCAO=7
TOPIC_OUTROS=8
```

#### OneDrive (Opcional)

```env
MICROSOFT_CLIENT_ID=seu_client_id_azure
MICROSOFT_CLIENT_SECRET=seu_client_secret_azure
```

### 4. Verificar Configurações do Railway

O arquivo `railway.toml` já está configurado com:

- **Health check**: `/health` (timeout 30s)
- **Réplicas**: 1 (evita conflitos com o bot)
- **Restart policy**: ON_FAILURE (max 3 retries)

### 5. Deploy

O Railway faz deploy automático quando você faz push para o GitHub:

```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

### 6. Verificar Logs

No painel do Railway:

1. Clique no serviço
2. Vá em **"Deployments"**
3. Clique no deploy mais recente
4. Veja os logs em tempo real

#### Logs esperados no startup:

```
========================================
🤖 ASSISTENTE RANNY V3
========================================
📊 Fechamento de caixa
📁 Documentos e busca
📝 Lembretes
🌐 Servidor web para relatórios
📅 Scheduler para alertas automáticos
========================================
🕐 Timezone: America/Sao_Paulo
📝 Job de lembretes configurado (a cada 1 minuto)
💰 Job de alertas de vencimento configurado (8h diário)
📊 Job de resumo semanal configurado (domingo 20h)
🌐 Servidor web iniciando na porta 8000...
🤖 Bot Telegram iniciando...
✅ Bot online! Aguardando mensagens...
```

### 7. Configurar Domínio (Opcional)

Para usar domínio customizado:

1. No Railway, vá em **Settings > Domains**
2. Adicione seu domínio (ex: `ranny.seudominio.com`)
3. Configure DNS CNAME apontando para Railway
4. Adicione variável: `BASE_URL=https://ranny.seudominio.com`

## 🔍 Verificação Pós-Deploy

### Health Check

Acesse: `https://seu-app.up.railway.app/health`

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.0.0",
  "components": {
    "web": "healthy",
    "database": {"status": "healthy"},
    "scheduler": {"status": "healthy", "jobs_count": 3}
  }
}
```

### Teste do Bot

1. Abra o Telegram
2. Vá para o grupo configurado
3. No tópico Chat, envie: "oi"
4. O bot deve responder

### Teste de Relatório

1. No tópico Chat, envie: "mostra gráfico da semana"
2. O bot deve enviar um link
3. Clique no link e verifique os gráficos

## 🐛 Troubleshooting

### Bot não responde

1. Verifique se `TELEGRAM_BOT_TOKEN` está correto
2. Verifique se `GROUP_ID` está correto
3. Verifique os logs no Railway

### Erro de conexão com banco

1. Verifique `SUPABASE_URL` e chaves
2. Verifique se o schema SQL foi executado
3. Teste a conexão via health check

### Relatórios não funcionam

1. Verifique se `BASE_URL` ou `RAILWAY_PUBLIC_DOMAIN` está configurado
2. Verifique se Plotly está instalado (requirements.txt)
3. Teste o endpoint `/health`

### Scheduler não funciona

1. Verifique os logs para erros de timezone
2. Verifique se `pytz` está instalado
3. O scheduler usa timezone `America/Sao_Paulo`

## 📊 Monitoramento

### Métricas do Railway

- CPU e memória em **Metrics**
- Logs em tempo real em **Deployments**
- Alertas configuráveis em **Settings**

### Health Check Automático

O Railway verifica `/health` automaticamente e reinicia se falhar.

## 🔄 Atualizações

Para atualizar o bot:

```bash
# Faça suas alterações
git add .
git commit -m "Descrição da atualização"
git push origin main
```

O Railway faz deploy automático em ~2 minutos.

## 📞 Suporte

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)
- **Telegram Bot API**: [core.telegram.org/bots/api](https://core.telegram.org/bots/api)
