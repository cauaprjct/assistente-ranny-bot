# 🚀 DEPLOY NO RENDER - PASSO A PASSO

**Data:** 03/02/2026  
**Status:** Executando deploy

---

## 📋 PRÉ-REQUISITOS

### ✅ Verificado:
- [x] Código completo e funcional
- [x] Procfile configurado
- [x] render.yaml configurado
- [x] requirements.txt atualizado
- [x] Variáveis de ambiente mapeadas
- [x] Health check implementado
- [x] Documentação atualizada

---

## 🔑 VARIÁVEIS DE AMBIENTE NECESSÁRIAS

### Obrigatórias:
```
TELEGRAM_BOT_TOKEN=8262619278:AAHYAIr5PddV9mxbn8zi95sFyTCwtTQWwSw
GEMINI_API_KEY=AIzaSyCxUdSoEnZWGq0l8_sMSZGKFjUoETNz8ps
GROUP_ID=-1003536252896
```

### Tópicos:
```
TOPIC_CHAT=47
TOPIC_FINANCEIRO=2
TOPIC_EMPRESA=3
TOPIC_JURIDICO=5
TOPIC_PESSOAL=4
TOPIC_FUNCIONARIOS=6
TOPIC_MANUTENCAO=7
TOPIC_OUTROS=8
TOPIC_OPERACIONAL=214
TOPIC_MIDIA=215
TOPIC_CONTROLES=216
```

### Supabase:
```
SUPABASE_URL=https://yaadvmghaccmakyqmhva.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhYWR2bWdoYWNjbWFreXFtaHZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0MzcwNjIsImV4cCI6MjA4NDAxMzA2Mn0.e7C097ez8_tCA-iXHw2fcP4Z_mDxhFlNYCL1cJQ0EIQ
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhYWR2bWdoYWNjbWFreXFtaHZhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODQzNzA2MiwiZXhwIjoyMDg0MDEzMDYyfQ.PhKYeysPVrnQt894VAKL5Q091NnWYhA1cZl6LTfWnbk
```

### Opcionais (OneDrive):
```
MICROSOFT_CLIENT_ID=<seu_client_id_azure>
MICROSOFT_CLIENT_SECRET=<seu_client_secret_azure>
MICROSOFT_REDIRECT_URI=https://assistente-ranny.onrender.com/oauth/callback
```

---

## 🎯 PASSOS PARA DEPLOY

### Opção 1: Deploy via Dashboard Render (Recomendado)

1. **Acessar Render Dashboard**
   - URL: https://dashboard.render.com
   - Login com sua conta

2. **Criar Novo Web Service**
   - Clicar em "New +" → "Web Service"
   - Conectar repositório GitHub
   - Selecionar branch: `main`

3. **Configurar Service**
   - Name: `assistente-ranny`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Root Directory: `assistente-ranny`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`

4. **Adicionar Variáveis de Ambiente**
   - Ir em "Environment"
   - Adicionar todas as variáveis listadas acima
   - **IMPORTANTE:** Atualizar `MICROSOFT_REDIRECT_URI` com URL do Render

5. **Configurar Health Check**
   - Health Check Path: `/health`
   - Health Check Interval: `60` segundos

6. **Deploy**
   - Clicar em "Create Web Service"
   - Aguardar build e deploy (~5 minutos)

### Opção 2: Deploy via CLI Render

```bash
# 1. Instalar Render CLI
npm install -g render-cli

# 2. Login
render login

# 3. Deploy
cd assistente-ranny
render deploy
```

### Opção 3: Deploy via Blueprint (render.yaml)

```bash
# 1. Commit e push do código
git add .
git commit -m "Deploy: Bot pronto para produção"
git push origin main

# 2. No Render Dashboard
# - New → Blueprint
# - Conectar repositório
# - Render detecta render.yaml automaticamente
# - Adicionar variáveis de ambiente secretas
# - Deploy
```

---

## 🔍 VERIFICAÇÃO PÓS-DEPLOY

### 1. Verificar Logs
```
# No Render Dashboard
- Ir em "Logs"
- Procurar por:
  ✅ "Bot online!"
  ✅ "Servidor web: http://..."
  ✅ "Health check: .../health"
```

### 2. Testar Health Check
```bash
curl https://assistente-ranny.onrender.com/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.2.0",
  "timestamp": "2026-02-03T...",
  "components": {
    "web": "healthy",
    "database": {"status": "healthy"},
    "scheduler": {"status": "healthy", "jobs_count": 4}
  }
}
```

### 3. Testar Bot no Telegram
```
1. Abrir Telegram
2. Buscar bot: @assistente_ranny_bot (ou seu bot)
3. Enviar: /start
4. Verificar resposta
5. Testar: "fechei 2500"
6. Testar: "me lembra amanhã de teste"
```

---

## 🐛 TROUBLESHOOTING

### Bot não responde
```
1. Verificar logs no Render
2. Verificar se TELEGRAM_BOT_TOKEN está correto
3. Verificar se bot está rodando (logs mostram "Bot online!")
4. Testar health check
```

### Erro de conexão com Supabase
```
1. Verificar SUPABASE_URL
2. Verificar SUPABASE_SERVICE_KEY
3. Verificar se projeto Supabase está ativo
4. Testar conexão manualmente
```

### Build falha
```
1. Verificar requirements.txt
2. Verificar Python version (3.10+)
3. Ver logs de build no Render
4. Verificar se todos os arquivos estão commitados
```

### Health check falha
```
1. Verificar se porta está correta (PORT env var)
2. Verificar se FastAPI está rodando
3. Verificar rota /health no web.py
4. Ver logs do servidor web
```

---

## 📊 MONITORAMENTO

### Métricas para Acompanhar
- ✅ Uptime (deve ser 99%+)
- ✅ Response time do health check
- ✅ Uso de memória
- ✅ Logs de erro
- ✅ Mensagens processadas

### Alertas Recomendados
- 🚨 Health check falha por 5 minutos
- 🚨 Uso de memória > 90%
- 🚨 Erro crítico nos logs
- 🚨 Bot offline por 10 minutos

---

## 🎉 SUCESSO!

### Quando o deploy estiver completo:
1. ✅ Bot online 24/7
2. ✅ Health check respondendo
3. ✅ Logs mostrando atividade
4. ✅ Telegram respondendo mensagens
5. ✅ Jobs automáticos rodando

### Próximos Passos:
1. Testar todas as funcionalidades
2. Monitorar logs por 24h
3. Ajustar se necessário
4. Treinar Ranny no uso
5. Celebrar! 🎉

---

_Deploy executado em: 03/02/2026_
