# ⚡ Deploy Render.com - Guia Rápido (5 minutos)

## 🎯 Por Que Render?

✅ **750 horas/mês GRÁTIS** (vs 500h Railway)  
✅ **Suficiente para 24/7 com keep-alive**  
✅ **Não precisa cartão de crédito**  
✅ **Deploy em 5 minutos**  

## 🚀 Deploy em 5 Passos

### 1️⃣ Criar Conta (1 min)

1. Acesse: [render.com](https://render.com)
2. Clique em **"Get Started"**
3. Login com GitHub

### 2️⃣ Novo Serviço (1 min)

1. Clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório
3. Selecione o repositório do bot

### 3️⃣ Configurar (2 min)

**Configurações:**
```
Name: assistente-ranny
Region: Oregon (US West)
Branch: main
Root Directory: assistente-ranny
Runtime: Python 3

Build Command: pip install -r requirements.txt
Start Command: python bot.py

Health Check Path: /health
```

**Plano:** Free

### 4️⃣ Variáveis de Ambiente (1 min)

Clique em **"Advanced"** e adicione:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
GEMINI_API_KEY=sua_chave_aqui
GROUP_ID=-1003536252896
```

(Os tópicos já estão no código)

### 5️⃣ Deploy! (30 seg)

Clique em **"Create Web Service"**

Aguarde 2-3 minutos... ☕

## ✅ Verificar

### Logs

Veja em tempo real:
```
✅ Bot online!
✅ Jobs agendados (incluindo keep-alive)
💓 Keep-alive: bot está acordado
```

### Telegram

Envie mensagem: **"oi"**

Bot deve responder! 🎉

## 🎯 Pronto!

Seu bot está:
- ✅ Online 24/7
- ✅ Com keep-alive funcionando
- ✅ Totalmente grátis
- ✅ 750h/mês (suficiente!)

## 📊 Monitorar

Dashboard: `https://dashboard.render.com`

Veja:
- CPU (~5-10%)
- Memory (~100-200MB)
- Uptime (100%)

## 🔄 Atualizar

Basta fazer push:
```bash
git add .
git commit -m "update"
git push
```

Deploy automático! 🚀

---

## 💡 Dicas

### Domínio Grátis

Render dá: `seu-app.onrender.com`

### SSL Grátis

Já vem configurado! 🔒

### Logs Ilimitados

Veja tudo que acontece!

### Auto-Deploy

Push = Deploy automático

---

## ⚠️ Importante

**750h/mês = 31 dias completos**

Com keep-alive a cada 10 min:
- Bot nunca dorme
- Lembretes funcionam
- Alertas disparam
- Tudo 24/7

**Custo: $0** 🎉

---

## 🆘 Problemas?

### Bot não inicia

1. Veja logs no dashboard
2. Verifique variáveis
3. Clique em "Manual Deploy"

### Keep-alive não funciona

1. Aguarde 10 minutos
2. Veja logs: `💓 Keep-alive`
3. Teste: `curl https://seu-app.onrender.com/health`

### Precisa de ajuda?

Veja: `DEPLOY_RENDER.md` (guia completo)

---

**Deploy:** 5 minutos  
**Custo:** $0  
**Resultado:** Bot 24/7 online! 🚀
