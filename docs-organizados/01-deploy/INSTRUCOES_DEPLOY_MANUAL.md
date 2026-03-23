# 🚀 INSTRUÇÕES PARA DEPLOY MANUAL

**Data:** 03/02/2026  
**Status:** Pronto para deploy

---

## ✅ O QUE JÁ FOI FEITO

1. ✅ Código atualizado e documentado
2. ✅ Limitações documentadas claramente
3. ✅ Commit criado localmente
4. ✅ Arquivos prontos para push

---

## 🔐 PROBLEMA DE AUTENTICAÇÃO

O push falhou por falta de autenticação no GitHub. Você precisa:

### Opção 1: Usar GitHub CLI (Recomendado)

```bash
# 1. Instalar GitHub CLI (se não tiver)
# Download: https://cli.github.com/

# 2. Fazer login
gh auth login

# 3. Push
git push origin main
```

### Opção 2: Usar Token de Acesso Pessoal

```bash
# 1. Criar token no GitHub
# - Ir em: https://github.com/settings/tokens
# - Generate new token (classic)
# - Selecionar scopes: repo (todos)
# - Copiar o token

# 2. Configurar credencial
git remote set-url origin https://SEU_TOKEN@github.com/cauaprjct/assistente-ranny-bot.git

# 3. Push
git push origin main
```

### Opção 3: Usar SSH

```bash
# 1. Gerar chave SSH (se não tiver)
ssh-keygen -t ed25519 -C "seu_email@example.com"

# 2. Adicionar chave ao GitHub
# - Copiar conteúdo de ~/.ssh/id_ed25519.pub
# - Ir em: https://github.com/settings/keys
# - New SSH key
# - Colar a chave

# 3. Mudar remote para SSH
git remote set-url origin git@github.com:cauaprjct/assistente-ranny-bot.git

# 4. Push
git push origin main
```

---

## 📋 PASSOS PARA DEPLOY NO RENDER

### 1. Fazer Push do Código

Escolha uma das opções acima e execute:

```bash
git push origin main
```

### 2. Acessar Render Dashboard

1. Ir em: https://dashboard.render.com
2. Fazer login com sua conta

### 3. Criar Novo Web Service

1. Clicar em **"New +"** → **"Web Service"**
2. Conectar repositório GitHub
3. Selecionar: `cauaprjct/assistente-ranny-bot`
4. Branch: `main`

### 4. Configurar Service

**Basic Settings:**
- **Name:** `assistente-ranny`
- **Region:** `Oregon (US West)`
- **Branch:** `main`
- **Root Directory:** `assistente-ranny`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`

**Advanced Settings:**
- **Plan:** `Free`
- **Auto-Deploy:** `Yes`

### 5. Adicionar Variáveis de Ambiente

Clicar em **"Environment"** e adicionar:

#### Obrigatórias:
```
TELEGRAM_BOT_TOKEN=8262619278:AAHYAIr5PddV9mxbn8zi95sFyTCwtTQWwSw
GEMINI_API_KEY=AIzaSyCxUdSoEnZWGq0l8_sMSZGKFjUoETNz8ps
GROUP_ID=-1003536252896
```

#### Tópicos:
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

#### Supabase:
```
SUPABASE_URL=https://yaadvmghaccmakyqmhva.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhYWR2bWdoYWNjbWFreXFtaHZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0MzcwNjIsImV4cCI6MjA4NDAxMzA2Mn0.e7C097ez8_tCA-iXHw2fcP4Z_mDxhFlNYCL1cJQ0EIQ
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhYWR2bWdoYWNjbWFreXFtaHZhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODQzNzA2MiwiZXhwIjoyMDg0MDEzMDYyfQ.PhKYeysPVrnQt894VAKL5Q091NnWYhA1cZl6LTfWnbk
```

#### Opcionais (OneDrive):
```
MICROSOFT_CLIENT_ID=<seu_client_id_azure>
MICROSOFT_CLIENT_SECRET=<seu_client_secret_azure>
```

**⚠️ IMPORTANTE:** Depois do deploy, atualizar:
```
MICROSOFT_REDIRECT_URI=https://assistente-ranny.onrender.com/oauth/callback
```

### 6. Configurar Health Check

Em **"Health & Alerts"**:
- **Health Check Path:** `/health`
- **Health Check Interval:** `60` segundos

### 7. Criar Web Service

1. Clicar em **"Create Web Service"**
2. Aguardar build (~5 minutos)
3. Aguardar deploy

---

## 🔍 VERIFICAÇÃO PÓS-DEPLOY

### 1. Verificar Logs

No Render Dashboard:
1. Ir em **"Logs"**
2. Procurar por:
   - ✅ `"Bot online!"`
   - ✅ `"Servidor web: http://..."`
   - ✅ `"Health check: .../health"`

### 2. Testar Health Check

Abrir no navegador:
```
https://assistente-ranny.onrender.com/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.2.0"
}
```

### 3. Testar Bot no Telegram

1. Abrir Telegram
2. Buscar seu bot
3. Enviar: `/start`
4. Verificar resposta
5. Testar: `"fechei 2500"`
6. Testar: `"me lembra amanhã de teste"`

---

## 🎉 SUCESSO!

Quando ver nos logs:
```
✅ Bot online!
✅ Servidor web: http://localhost:10000
✅ Health check: http://localhost:10000/health
```

**O bot está rodando! 🚀**

---

## 🐛 TROUBLESHOOTING

### Build Falha

**Erro:** `Could not find a version that satisfies the requirement...`

**Solução:**
1. Verificar `requirements.txt`
2. Verificar Python version (3.10+)
3. Ver logs completos de build

### Bot Não Responde

**Possíveis causas:**
1. `TELEGRAM_BOT_TOKEN` incorreto
2. Bot não está rodando (ver logs)
3. Erro no código (ver logs de erro)

**Solução:**
1. Verificar variáveis de ambiente
2. Ver logs no Render
3. Testar health check

### Erro de Conexão Supabase

**Erro:** `Connection refused` ou `Unauthorized`

**Solução:**
1. Verificar `SUPABASE_URL`
2. Verificar `SUPABASE_SERVICE_KEY`
3. Verificar se projeto Supabase está ativo

### Health Check Falha

**Erro:** `Health check failed`

**Solução:**
1. Verificar se porta está correta
2. Verificar se FastAPI está rodando
3. Ver logs do servidor web

---

## 📊 MONITORAMENTO

### Métricas Importantes

No Render Dashboard, monitorar:
- ✅ **Uptime:** Deve ser 99%+
- ✅ **Response Time:** Health check < 1s
- ✅ **Memory Usage:** < 512MB
- ✅ **Logs:** Sem erros críticos

### Alertas Recomendados

Configurar alertas para:
- 🚨 Health check falha por 5 minutos
- 🚨 Uso de memória > 90%
- 🚨 Bot offline por 10 minutos

---

## 📝 CHECKLIST FINAL

Antes de considerar completo:

- [ ] Push do código para GitHub
- [ ] Web Service criado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Health check configurado
- [ ] Build completado com sucesso
- [ ] Deploy completado com sucesso
- [ ] Logs mostram "Bot online!"
- [ ] Health check responde
- [ ] Bot responde no Telegram
- [ ] Testado fechamento de caixa
- [ ] Testado lembretes
- [ ] Testado busca de documentos

---

## 🎯 PRÓXIMOS PASSOS

Depois do deploy:

1. ✅ Monitorar logs por 24h
2. ✅ Testar todas as funcionalidades
3. ✅ Ajustar se necessário
4. ✅ Treinar Ranny no uso
5. ✅ Celebrar! 🎉

---

## 📞 SUPORTE

Se precisar de ajuda:

1. **Logs do Render:** Ver erros específicos
2. **Documentação:** Ler `README.md` e `STATUS_ATUAL_BOT_PARA_RANNY.md`
3. **GitHub Issues:** Criar issue no repositório
4. **Render Support:** https://render.com/docs

---

**🚀 Boa sorte com o deploy!**

_Criado em: 03/02/2026_
