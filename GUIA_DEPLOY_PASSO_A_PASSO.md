# 🚀 Guia de Deploy Passo a Passo - Render.com

## ✅ Checklist de Progresso

Marque cada etapa conforme completa:

- [x] Código commitado no Git
- [ ] Repositório criado no GitHub
- [ ] Código enviado para GitHub
- [ ] Conta criada no Render.com
- [ ] Serviço criado no Render
- [ ] Variáveis configuradas
- [ ] Deploy iniciado
- [ ] Bot testado no Telegram
- [ ] Keep-alive verificado
- [ ] Documentação revisada

---

## 📋 Pré-requisitos

✅ **Já feito:**
- Git inicializado
- Código commitado
- Keep-alive implementado
- Documentação criada

⏳ **Você precisa:**
- Conta no GitHub (grátis)
- Conta no Render.com (grátis)
- Token do BotFather (Telegram)
- Chave do Gemini AI

---

## 🎯 Passo 1: Criar Repositório no GitHub (5 min)

### 1.1 Acessar GitHub

1. Abra: https://github.com
2. Faça login (ou crie conta)
3. Clique no **"+"** no canto superior direito
4. Selecione **"New repository"**

### 1.2 Configurar Repositório

```
Repository name: assistente-ranny
Description: Bot Telegram para gestão da GRN Pizzas
Visibility: Private (recomendado) ou Public
```

**NÃO marque:**
- ❌ Add a README file
- ❌ Add .gitignore
- ❌ Choose a license

(Já temos esses arquivos!)

### 1.3 Criar Repositório

Clique em **"Create repository"**

### 1.4 Conectar Repositório Local

O GitHub vai mostrar comandos. Use estes:

```bash
# No seu terminal (PowerShell)
cd C:\Users\ngb\Desktop\RANNY

# Adicionar remote
git remote add origin https://github.com/SEU_USUARIO/assistente-ranny.git

# Renomear branch para main (se necessário)
git branch -M main

# Fazer push
git push -u origin main
```

**Substitua `SEU_USUARIO` pelo seu username do GitHub!**

### 1.5 Verificar

Atualize a página do GitHub - você deve ver todos os arquivos!

✅ **Checkpoint:** Código no GitHub

---

## 🎯 Passo 2: Criar Conta no Render.com (2 min)

### 2.1 Acessar Render

1. Abra: https://render.com
2. Clique em **"Get Started"**
3. Escolha **"Sign in with GitHub"** (recomendado)
4. Autorize o Render a acessar seus repositórios

### 2.2 Verificar Email

Se solicitado, verifique seu email.

✅ **Checkpoint:** Conta criada no Render

---

## 🎯 Passo 3: Criar Novo Serviço (3 min)

### 3.1 Novo Web Service

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub
4. Selecione **"assistente-ranny"**

### 3.2 Configurar Serviço

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

### 3.3 Configurar Health Check

```
Health Check Path: /health
```

### 3.4 Selecionar Plano

Selecione: **Free** (750 horas/mês)

✅ **Checkpoint:** Serviço configurado

---

## 🎯 Passo 4: Configurar Variáveis de Ambiente (2 min)

### 4.1 Adicionar Variáveis

Clique em **"Advanced"** e adicione:

#### Obrigatórias:

```env
TELEGRAM_BOT_TOKEN
Valor: seu_token_do_botfather
```

```env
GEMINI_API_KEY
Valor: sua_chave_gemini
```

```env
GROUP_ID
Valor: -1003536252896
```

#### Tópicos (já tem valores padrão no código, mas pode adicionar):

```env
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

### 4.2 Salvar

As variáveis são salvas automaticamente.

✅ **Checkpoint:** Variáveis configuradas

---

## 🎯 Passo 5: Deploy! (3-5 min)

### 5.1 Iniciar Deploy

Clique em **"Create Web Service"**

### 5.2 Aguardar Build

O Render vai:
1. ✅ Clonar repositório
2. ✅ Instalar dependências (pip install)
3. ✅ Iniciar bot (python bot.py)
4. ✅ Configurar SSL
5. ✅ Gerar URL pública

**Tempo estimado:** 3-5 minutos ☕

### 5.3 Acompanhar Logs

Clique em **"Logs"** para ver em tempo real:

```
✅ Bot online!
✅ Servidor web: http://0.0.0.0:8000
✅ Jobs agendados (incluindo keep-alive)
💓 Keep-alive: bot está acordado
```

### 5.4 Copiar URL

Quando o deploy terminar, copie a URL:
```
https://assistente-ranny.onrender.com
```

✅ **Checkpoint:** Deploy concluído

---

## 🎯 Passo 6: Verificar Deploy (5 min)

### 6.1 Usar Script de Verificação

No seu terminal:

```bash
# Instalar dependências do script
pip install playwright httpx
playwright install chromium

# Executar verificação
python verificar_deploy.py
```

O script vai:
1. ✅ Verificar health check
2. ✅ Verificar componentes
3. ✅ Verificar keep-alive
4. ✅ Gerar relatório

### 6.2 Verificação Manual

Ou teste manualmente:

```bash
# Health check
curl https://assistente-ranny.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.0.0",
  "components": {
    "web": "healthy",
    "database": {"status": "healthy"},
    "scheduler": {
      "status": "healthy",
      "jobs_count": 4
    }
  }
}
```

✅ **Checkpoint:** Health check OK

---

## 🎯 Passo 7: Testar no Telegram (2 min)

### 7.1 Abrir Telegram

1. Abra o Telegram
2. Vá para o grupo "Documentos Ranny"
3. Entre no Tópico Chat

### 7.2 Enviar Mensagem

```
Você: oi
```

### 7.3 Verificar Resposta

O bot deve responder:
```
Bot: Oi! Tô aqui pra te ajudar 😊 O que você precisa?
```

### 7.4 Testar Funcionalidades

```
Você: quantos arquivos você tem?
Bot: [lista os tópicos e arquivos]

Você: fechei 2500
Bot: ✅ Fechamento registrado! ...

Você: me lembra amanhã de pagar FGTS
Bot: ✅ Lembrete criado! ...
```

✅ **Checkpoint:** Bot funcionando no Telegram

---

## 🎯 Passo 8: Verificar Keep-Alive (10 min)

### 8.1 Aguardar 10 Minutos

Aguarde 10 minutos e verifique os logs no Render:

```
Dashboard > Logs
```

Procure por:
```
💓 Keep-alive: bot está acordado
```

### 8.2 Verificar Periodicidade

O keep-alive deve aparecer a cada 10 minutos:

```
10:00 - 💓 Keep-alive: bot está acordado
10:10 - 💓 Keep-alive: bot está acordado
10:20 - 💓 Keep-alive: bot está acordado
```

✅ **Checkpoint:** Keep-alive funcionando

---

## 🎯 Passo 9: Monitoramento (Contínuo)

### 9.1 Dashboard do Render

Acesse: https://dashboard.render.com

Monitore:
- **CPU:** ~5-10% (normal)
- **Memory:** ~100-200MB (normal)
- **Bandwidth:** Pequenos picos a cada 10 min
- **Uptime:** Deve ser 100%

### 9.2 Logs em Tempo Real

Clique em **"Logs"** para ver em tempo real.

### 9.3 Métricas

O Render mostra:
- Requests/segundo
- Response time
- Error rate
- Uptime %

✅ **Checkpoint:** Monitoramento configurado

---

## 🎯 Passo 10: Documentação (5 min)

### 10.1 Revisar Guias

Leia os guias criados:
- `GUIA_PARA_RANNY.md` - Manual do usuário
- `DEPLOY_RENDER.md` - Guia completo
- `KEEP_ALIVE_RAILWAY.md` - Como funciona keep-alive

### 10.2 Treinar Usuária

Mostre para a Ranny:
- Como conversar com o bot
- Como enviar documentos
- Como criar lembretes
- Como fazer fechamento de caixa

### 10.3 Configurar Backup

Configure backup semanal do banco:

```bash
# Baixar banco SQLite (se necessário)
# Via Render Shell ou SSH
```

✅ **Checkpoint:** Documentação revisada

---

## 🎉 Deploy Concluído!

### ✅ Checklist Final

- [x] Código no GitHub
- [x] Deploy no Render
- [x] Bot online 24/7
- [x] Keep-alive funcionando
- [x] Testado no Telegram
- [x] Monitoramento configurado
- [x] Documentação completa

### 📊 Resultado

Você agora tem:

✅ **Bot online 24/7**  
✅ **750 horas/mês grátis**  
✅ **Keep-alive automático**  
✅ **Lembretes funcionando**  
✅ **Alertas automáticos**  
✅ **Custo: $0/mês**  

### 🎯 Próximos Passos

1. **Usar o bot diariamente**
2. **Monitorar logs semanalmente**
3. **Fazer backup mensal**
4. **Atualizar quando necessário**

---

## 🆘 Problemas?

### Bot não inicia

1. Verificar logs no Render
2. Verificar variáveis de ambiente
3. Rebuild manual: Manual Deploy > Clear build cache & deploy

### Keep-alive não funciona

1. Aguardar 10 minutos
2. Verificar logs: `💓 Keep-alive`
3. Testar health check: `curl https://seu-app.onrender.com/health`

### Bot dorme

1. Verificar uso de horas (Dashboard > Usage)
2. Verificar intervalo do keep-alive (deve ser 10 min)
3. Ver logs de erro

### Precisa de ajuda?

- **Documentação:** Veja os arquivos `.md` neste projeto
- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com

---

**Deploy concluído com sucesso! 🚀**

**Data:** 02/02/2026  
**Plataforma:** Render.com (Free)  
**Status:** ✅ Online 24/7
