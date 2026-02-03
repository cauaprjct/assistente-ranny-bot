# ✅ Checklist - Deploy no Render.com

Use este checklist para garantir que tudo está pronto antes do deploy.

---

## 📋 Antes do Deploy

### 1. Código no GitHub
- [ ] Repositório criado no GitHub
- [ ] Código commitado e pushed
- [ ] Branch `main` atualizada
- [ ] `.gitignore` configurado (não subir `.env`)

### 2. Arquivos Necessários
- [ ] `bot.py` - Bot principal
- [ ] `requirements.txt` - Dependências
- [ ] `render.yaml` - Configuração do Render
- [ ] `.gitignore` - Arquivos ignorados
- [ ] `DEPLOY_RENDER.md` - Documentação

### 3. Credenciais Prontas
- [ ] Token do Bot Telegram (do @BotFather)
- [ ] Chave API do Gemini
- [ ] ID do Grupo Telegram
- [ ] IDs dos 11 tópicos

---

## 🚀 Durante o Deploy

### 1. Criar Conta no Render
- [ ] Conta criada em [render.com](https://render.com)
- [ ] Login feito com GitHub
- [ ] Render autorizado a acessar repositórios

### 2. Criar Web Service
- [ ] Novo Web Service criado
- [ ] Repositório `assistente-ranny` conectado
- [ ] Branch `main` selecionada

### 3. Configurações Básicas
- [ ] **Name:** `assistente-ranny`
- [ ] **Region:** `Oregon (US West)`
- [ ] **Runtime:** `Python 3`
- [ ] **Build Command:** `pip install -r requirements.txt`
- [ ] **Start Command:** `python bot.py`
- [ ] **Plan:** `Free`

### 4. Variáveis de Ambiente

#### Obrigatórias:
- [ ] `TELEGRAM_BOT_TOKEN` = seu token
- [ ] `GEMINI_API_KEY` = sua chave
- [ ] `GROUP_ID` = ID do grupo

#### Tópicos:
- [ ] `TOPIC_CHAT` = 47
- [ ] `TOPIC_FINANCEIRO` = 2
- [ ] `TOPIC_EMPRESA` = 3
- [ ] `TOPIC_JURIDICO` = 5
- [ ] `TOPIC_PESSOAL` = 4
- [ ] `TOPIC_FUNCIONARIOS` = 6
- [ ] `TOPIC_MANUTENCAO` = 7
- [ ] `TOPIC_OUTROS` = 8
- [ ] `TOPIC_OPERACIONAL` = 214
- [ ] `TOPIC_MIDIA` = 215
- [ ] `TOPIC_CONTROLES` = 216

### 5. Health Check
- [ ] **Health Check Path:** `/health`
- [ ] **Interval:** `30` segundos

### 6. Deploy
- [ ] Clicou em "Create Web Service"
- [ ] Deploy iniciado
- [ ] Logs acompanhados

---

## ✅ Após o Deploy

### 1. Verificar Health Check
- [ ] Acessou `https://seu-app.onrender.com/health`
- [ ] Retornou JSON com `"status": "healthy"`

### 2. Testar Bot no Telegram
- [ ] Abriu o grupo no Telegram
- [ ] Enviou "oi" no tópico Chat
- [ ] Bot respondeu

### 3. Testar Funcionalidades

#### Básicas:
- [ ] Comando `/start` funciona
- [ ] Comando `/help` funciona
- [ ] Bot responde mensagens de texto

#### Documentos:
- [ ] Enviar PDF → bot analisa e classifica
- [ ] Enviar foto → bot analisa
- [ ] Buscar documento → "cadê o contrato?"

#### Fechamento:
- [ ] "fechei 2500" → registra fechamento
- [ ] Mostra comparação com dia anterior

#### Lembretes:
- [ ] "me lembra amanhã de X" → cria lembrete
- [ ] "quais meus lembretes?" → lista lembretes

#### Relatórios:
- [ ] "mostra gráfico da semana" → gera link
- [ ] Link abre e mostra gráficos

### 4. Monitoramento
- [ ] Logs verificados (sem erros críticos)
- [ ] CPU/Memória em níveis normais
- [ ] Alertas de email configurados

---

## 🐛 Se Algo Der Errado

### Bot não responde:
1. [ ] Verificar logs no Render
2. [ ] Verificar `TELEGRAM_BOT_TOKEN`
3. [ ] Verificar `GROUP_ID`
4. [ ] Verificar se bot está no grupo

### Health check falha:
1. [ ] Verificar se porta é 8000
2. [ ] Verificar se servidor web está rodando
3. [ ] Ver logs de inicialização

### Erro de dependências:
1. [ ] Verificar `requirements.txt`
2. [ ] Testar localmente
3. [ ] Atualizar versões se necessário

---

## 📝 Notas Importantes

### Plano Free:
- ✅ 750 horas/mês (suficiente para 24/7)
- ⚠️ Pode dormir após 15 min de inatividade
- ✅ Bots Telegram geralmente mantêm conexão ativa

### Auto-Deploy:
- ✅ Ativado por padrão
- ✅ Deploy automático ao fazer push no GitHub
- ✅ ~2 minutos para completar

### Custos:
- ✅ **$0/mês** no plano Free
- ✅ Sem cartão de crédito necessário
- ✅ Upgrade opcional: $7/mês (Starter)

---

## 🎉 Conclusão

Quando todos os itens estiverem marcados:

✅ **Bot está no ar 24/7!**
✅ **Funcionando gratuitamente!**
✅ **Pronto para uso!**

---

**Data do Deploy:** ___/___/______

**URL do Serviço:** https://________________________.onrender.com

**Status:** [ ] Funcionando perfeitamente

---

_Mantenha este checklist para referência futura!_
