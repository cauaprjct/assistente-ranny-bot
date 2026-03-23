# 🚀 Deploy no Render.com - Assistente Ranny

Guia completo para fazer deploy do bot no Render.com **100% GRATUITO**.

---

## ✅ Por Que Render.com?

- ✅ **100% gratuito** (plano Free)
- ✅ **750 horas/mês** (suficiente para 24/7)
- ✅ **Não precisa cartão de crédito**
- ✅ **Deploy automático** do GitHub
- ✅ **SSL grátis** (HTTPS)
- ✅ **Logs em tempo real**
- ✅ **Fácil de configurar**

---

## 📋 Pré-requisitos

Antes de começar, você precisa ter:

1. ✅ **Conta no GitHub** - [github.com](https://github.com)
2. ✅ **Conta no Render** - [render.com](https://render.com) (criar é grátis)
3. ✅ **Token do Bot Telegram** - Do @BotFather
4. ✅ **Chave API do Gemini** - [aistudio.google.com](https://aistudio.google.com)
5. ✅ **ID do Grupo Telegram** - Onde o bot vai funcionar

---

## 🔧 Passo a Passo

### 1️⃣ Preparar o Código no GitHub

#### Se ainda não tem repositório:

```bash
# Na pasta assistente-ranny
cd assistente-ranny

# Inicializa git
git init

# Adiciona todos os arquivos
git add .

# Faz o primeiro commit
git commit -m "Deploy inicial - Assistente Ranny"

# Cria repositório no GitHub (vá em github.com e crie um repo novo)
# Depois conecte:
git remote add origin https://github.com/SEU_USUARIO/assistente-ranny.git
git branch -M main
git push -u origin main
```

#### Se já tem repositório:

```bash
# Certifique-se que está atualizado
git add .
git commit -m "Preparando para deploy no Render"
git push origin main
```

---

### 2️⃣ Criar Conta no Render

1. Acesse [render.com](https://render.com)
2. Clique em **"Get Started"**
3. Faça login com sua conta do **GitHub**
4. Autorize o Render a acessar seus repositórios

---

### 3️⃣ Criar Novo Web Service

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório:
   - Clique em **"Connect a repository"**
   - Procure por `assistente-ranny`
   - Clique em **"Connect"**

---

### 4️⃣ Configurar o Serviço

Na tela de configuração, preencha:

#### **Informações Básicas:**
- **Name:** `assistente-ranny` (ou o nome que preferir)
- **Region:** `Oregon (US West)` (mais próximo do Brasil)
- **Branch:** `main`
- **Root Directory:** deixe vazio (ou `assistente-ranny` se estiver em subpasta)

#### **Build & Deploy:**
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`

#### **Plano:**
- Selecione **"Free"** (0$/mês)

---

### 5️⃣ Configurar Variáveis de Ambiente

Role até a seção **"Environment Variables"** e adicione:

#### **Obrigatórias:**

| Key | Value | Onde conseguir |
|-----|-------|----------------|
| `TELEGRAM_BOT_TOKEN` | `7***` | @BotFather no Telegram |
| `GEMINI_API_KEY` | `AIz***` | [aistudio.google.com](https://aistudio.google.com) |
| `GROUP_ID` | `-1003536252896` | ID do grupo (use @userinfobot) |

#### **Tópicos do Telegram:**

| Key | Value |
|-----|-------|
| `TOPIC_CHAT` | `47` |
| `TOPIC_FINANCEIRO` | `2` |
| `TOPIC_EMPRESA` | `3` |
| `TOPIC_JURIDICO` | `5` |
| `TOPIC_PESSOAL` | `4` |
| `TOPIC_FUNCIONARIOS` | `6` |
| `TOPIC_MANUTENCAO` | `7` |
| `TOPIC_OUTROS` | `8` |
| `TOPIC_OPERACIONAL` | `214` |
| `TOPIC_MIDIA` | `215` |
| `TOPIC_CONTROLES` | `216` |

#### **Opcionais (Supabase - se usar):**

| Key | Value |
|-----|-------|
| `SUPABASE_URL` | `https://seu-projeto.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJ***` |
| `SUPABASE_SERVICE_KEY` | `eyJ***` |

#### **Opcionais (OneDrive - se usar):**

| Key | Value |
|-----|-------|
| `MICROSOFT_CLIENT_ID` | Seu Client ID do Azure |
| `MICROSOFT_CLIENT_SECRET` | Seu Client Secret |

---

### 6️⃣ Configurar Health Check

Role até **"Health Check Path"** e configure:

- **Health Check Path:** `/health`
- **Health Check Interval:** `30` segundos

Isso garante que o Render reinicie o bot se ele parar de responder.

---

### 7️⃣ Deploy!

1. Clique em **"Create Web Service"**
2. O Render vai começar o deploy automaticamente
3. Aguarde ~2-3 minutos

#### **Acompanhe o progresso:**
- Veja os logs em tempo real na tela
- Procure por mensagens como:
  ```
  ✅ Bot online! Aguardando mensagens...
  🌐 Servidor web iniciando na porta 8000...
  ```

---

### 8️⃣ Verificar se Funcionou

#### **1. Verificar Health Check:**

Acesse a URL do seu serviço + `/health`:
```
https://assistente-ranny.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.0.0"
}
```

#### **2. Testar o Bot:**

1. Abra o Telegram
2. Vá para o grupo configurado
3. No tópico Chat, envie: **"oi"**
4. O bot deve responder! 🎉

---

## 🎯 Configurações Importantes

### **Auto-Deploy (Recomendado)**

O Render faz deploy automático quando você faz push no GitHub:

```bash
# Faça suas alterações
git add .
git commit -m "Atualização do bot"
git push origin main

# Render faz deploy automático em ~2 minutos
```

### **Logs em Tempo Real**

Para ver os logs:
1. Vá no dashboard do Render
2. Clique no seu serviço
3. Vá em **"Logs"**
4. Veja tudo em tempo real

### **Reiniciar Manualmente**

Se precisar reiniciar:
1. No dashboard, clique em **"Manual Deploy"**
2. Selecione **"Clear build cache & deploy"**

---

## 🐛 Troubleshooting

### **Bot não responde no Telegram**

**Possíveis causas:**

1. **Token errado:**
   - Verifique `TELEGRAM_BOT_TOKEN` nas variáveis de ambiente
   - Teste o token com @BotFather

2. **Group ID errado:**
   - Verifique `GROUP_ID` (deve começar com `-100`)
   - Use @userinfobot para pegar o ID correto

3. **Bot não está no grupo:**
   - Adicione o bot ao grupo
   - Dê permissões de administrador

**Como verificar:**
```bash
# Veja os logs no Render
# Procure por erros como:
# "Unauthorized" → Token errado
# "Chat not found" → Group ID errado
```

---

### **Erro "Application failed to respond"**

**Causa:** O bot não está respondendo no health check.

**Solução:**
1. Verifique se `bot.py` tem o servidor web
2. Verifique se a porta é `8000` (ou a variável `PORT`)
3. Veja os logs para erros de inicialização

---

### **Erro de dependências**

**Causa:** Alguma biblioteca não instalou.

**Solução:**
1. Verifique `requirements.txt`
2. Teste localmente: `pip install -r requirements.txt`
3. Se alguma biblioteca falhar, atualize a versão

---

### **Bot "dorme" após 15 minutos**

**Causa:** Plano Free do Render dorme após inatividade.

**Solução:**
- Bots Telegram mantêm conexão ativa, então **não deve dormir**
- Se dormir, considere:
  - Usar um serviço de "ping" (ex: UptimeRobot)
  - Ou migrar para Railway ($5/mês)

---

### **Erro de memória/CPU**

**Causa:** Plano Free tem limites de recursos.

**Solução:**
1. Otimize o código (remova logs desnecessários)
2. Use SQLite em vez de Supabase (menos overhead)
3. Se precisar de mais recursos, upgrade para plano pago ($7/mês)

---

## 📊 Monitoramento

### **Métricas Disponíveis:**

No dashboard do Render você vê:
- ✅ **Status:** Online/Offline
- ✅ **CPU:** Uso de processamento
- ✅ **Memória:** Uso de RAM
- ✅ **Logs:** Em tempo real
- ✅ **Deploy History:** Histórico de deploys

### **Alertas:**

Configure alertas de email:
1. Vá em **Settings**
2. Ative **"Email notifications"**
3. Receba alertas se o bot cair

---

## 🔄 Atualizações

### **Deploy Automático:**

```bash
# Faça suas alterações
git add .
git commit -m "Nova funcionalidade"
git push origin main

# Render detecta e faz deploy automático
```

### **Deploy Manual:**

1. No dashboard, clique em **"Manual Deploy"**
2. Selecione a branch
3. Clique em **"Deploy"**

---

## 💰 Custos

### **Plano Free:**
- ✅ **$0/mês**
- ✅ **750 horas/mês** (31 dias = 744 horas)
- ✅ **Suficiente para 24/7**
- ⚠️ Pode dormir após 15 min de inatividade (mas bots geralmente não dormem)

### **Se precisar de mais:**
- **Starter:** $7/mês (sem sleep, mais recursos)
- **Standard:** $25/mês (ainda mais recursos)

---

## 🎉 Pronto!

Seu bot está no ar 24/7 de graça! 🚀

### **Próximos Passos:**

1. ✅ Teste todas as funcionalidades
2. ✅ Configure alertas de email
3. ✅ Monitore os logs nos primeiros dias
4. ✅ Documente qualquer problema

### **Suporte:**

- **Render Docs:** [render.com/docs](https://render.com/docs)
- **Telegram Bot API:** [core.telegram.org/bots](https://core.telegram.org/bots)
- **Gemini API:** [ai.google.dev](https://ai.google.dev)

---

**Feito com ❤️ para a Ranny!**

_Última atualização: 02/02/2026_
