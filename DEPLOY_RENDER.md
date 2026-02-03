# 🚀 Deploy no Render.com (GRÁTIS 750h/mês)

## 🎯 Por Que Render.com?

✅ **750 horas/mês grátis** (vs 500h Railway)  
✅ **Suficiente para 24/7 com keep-alive**  
✅ **Mais estável que Railway**  
✅ **Deploy automático via GitHub**  
✅ **SSL grátis**  
✅ **Logs ilimitados**  

## 📋 Passo a Passo

### 1. Criar Conta no Render

1. Acesse [render.com](https://render.com)
2. Clique em **"Get Started"**
3. Faça login com GitHub (recomendado)

### 2. Conectar Repositório

1. No dashboard, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub
4. Selecione o repositório do bot

### 3. Configurar Serviço

**Configurações básicas:**

```
Name: assistente-ranny
Region: Oregon (US West)
Branch: main
Root Directory: assistente-ranny
Runtime: Python 3
```

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python bot.py
```

### 4. Configurar Variáveis de Ambiente

Clique em **"Advanced"** e adicione:

```env
# Obrigatórias
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
GEMINI_API_KEY=sua_chave_gemini
GROUP_ID=-1003536252896

# Tópicos
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

### 5. Configurar Health Check

```
Health Check Path: /health
```

### 6. Selecionar Plano

Selecione: **Free** (750 horas/mês)

### 7. Deploy!

Clique em **"Create Web Service"**

O Render vai:
1. ✅ Clonar o repositório
2. ✅ Instalar dependências
3. ✅ Iniciar o bot
4. ✅ Configurar SSL
5. ✅ Gerar URL pública

## 🔍 Verificar Deploy

### A. Logs do Render

No dashboard do serviço, clique em **"Logs"**

Procure por:
```
✅ Bot online!
✅ Servidor web: http://0.0.0.0:8000
✅ Jobs agendados (incluindo keep-alive)
💓 Keep-alive: bot está acordado
```

### B. Health Check

```bash
curl https://assistente-ranny.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.0.0"
}
```

### C. Testar no Telegram

Envie mensagem para o bot - deve responder imediatamente!

## ⚙️ Configurações Avançadas

### Auto-Deploy

O Render faz deploy automático quando você faz push:

```bash
git add .
git commit -m "feat: nova funcionalidade"
git push
```

Deploy acontece automaticamente! 🎉

### Domínio Customizado (Opcional)

1. Vá em **Settings > Custom Domain**
2. Adicione seu domínio
3. Configure DNS CNAME
4. SSL configurado automaticamente

### Notificações

1. Settings > Notifications
2. Adicione email ou Slack
3. Receba alertas de deploy e crashes

## 📊 Monitoramento

### Dashboard do Render

Acesse: `https://dashboard.render.com`

Monitore:
- **CPU** - Deve ficar baixo (~5-10%)
- **Memory** - ~100-200MB
- **Bandwidth** - Pequenos picos (keep-alive)
- **Uptime** - Deve ser 100%

### Logs em Tempo Real

No dashboard, clique em **"Logs"** e veja em tempo real.

### Métricas

O Render mostra:
- Requests/segundo
- Response time
- Error rate
- Uptime %

## 💰 Limites do Plano Free

### O Que Você Tem

✅ **750 horas/mês** (31 dias completos!)  
✅ **512 MB RAM**  
✅ **0.1 CPU**  
✅ **Bandwidth ilimitado**  
✅ **SSL grátis**  
✅ **Deploy automático**  

### Limitações

⚠️ **Serviço dorme após 15 min de inatividade**  
✅ **Mas o keep-alive resolve isso!**

⚠️ **Builds podem ser lentos**  
✅ **Mas é só no primeiro deploy**

⚠️ **Região limitada (Oregon)**  
✅ **Mas funciona bem do Brasil**

## 🔄 Migração do Railway

Se você já tem no Railway:

### 1. Exportar Banco de Dados

```bash
# Baixar banco SQLite
railway run python -c "import shutil; shutil.copy('bot_database.db', 'backup.db')"
```

### 2. Fazer Deploy no Render

Siga os passos acima.

### 3. Importar Banco

```bash
# Upload do banco via Render Shell
# (Ou recomeçar do zero - recomendado)
```

### 4. Desativar Railway

1. Vá no dashboard do Railway
2. Settings > Delete Service

## 🆚 Render vs Railway

| Feature | Render Free | Railway Free |
|---------|-------------|--------------|
| **Horas/mês** | 750h | 500h |
| **RAM** | 512 MB | 512 MB |
| **CPU** | 0.1 | 0.1 |
| **Bandwidth** | Ilimitado | 100 GB |
| **SSL** | ✅ Grátis | ✅ Grátis |
| **Auto-deploy** | ✅ | ✅ |
| **Logs** | Ilimitados | 7 dias |
| **Uptime** | 99.9% | 99.5% |

**Vencedor:** 🏆 **Render** (750h é suficiente para 24/7!)

## 🔧 Troubleshooting

### Bot não inicia

**1. Verifique logs:**
```
Dashboard > Logs
```

**2. Verifique variáveis:**
```
Settings > Environment
```

**3. Rebuild:**
```
Manual Deploy > Clear build cache & deploy
```

### Keep-alive não funciona

**1. Verifique URL:**
```bash
curl https://seu-app.onrender.com/health
```

**2. Aguarde 10 minutos:**
O primeiro keep-alive demora um pouco.

**3. Veja logs:**
```
💓 Keep-alive: bot está acordado
```

### Bot dorme mesmo com keep-alive

**Causa:** Render tem limite de 15 min de inatividade.

**Solução:** O keep-alive (10 min) deve resolver. Se não:
- Reduza intervalo para 5 min
- Ou use Fly.io (sem sleep)

### Erro "Out of Memory"

**Causa:** Bot usando mais de 512 MB.

**Solução:**
1. Otimize código
2. Ou upgrade para plano pago ($7/mês)

## 🎯 Alternativas Gratuitas

Se o Render não funcionar:

### 1. Fly.io (Recomendado)

✅ **3 VMs grátis**  
✅ **Sem sleep**  
✅ **256 MB RAM cada**  
✅ **160 GB bandwidth**  

Deploy:
```bash
flyctl launch
flyctl deploy
```

### 2. Heroku

✅ **550 horas/mês grátis** (com cartão)  
⚠️ Precisa cartão de crédito  
⚠️ Dorme após 30 min  

### 3. Koyeb

✅ **Grátis para sempre**  
✅ **512 MB RAM**  
✅ **100 GB bandwidth**  
⚠️ Menos conhecido  

### 4. VPS Barato

Se quiser controle total:

- **Contabo** - €3.99/mês (4 GB RAM)
- **Hetzner** - €4.51/mês (4 GB RAM)
- **DigitalOcean** - $6/mês (1 GB RAM)

## 📝 Checklist de Deploy

- [ ] Conta criada no Render
- [ ] Repositório conectado
- [ ] Variáveis configuradas
- [ ] Health check configurado
- [ ] Deploy iniciado
- [ ] Logs verificados
- [ ] Bot testado no Telegram
- [ ] Keep-alive funcionando
- [ ] Documentação atualizada

## 🎉 Pronto!

Com o Render.com você tem:

✅ **750 horas/mês grátis** (suficiente para 24/7)  
✅ **Keep-alive funcionando**  
✅ **Bot sempre acordado**  
✅ **Lembretes e alertas 24/7**  
✅ **Custo: $0**  

---

## 📞 Suporte

### Documentação Oficial

- [Render Docs](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-python)
- [Environment Variables](https://render.com/docs/environment-variables)

### Comunidade

- [Render Community](https://community.render.com)
- [Discord](https://discord.gg/render)

---

**Deploy:** 02/02/2026  
**Plataforma:** Render.com (Free)  
**Status:** 🚀 Pronto para deploy!
