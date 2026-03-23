# 🚀 Deploy Rápido - Assistente Ranny com Keep-Alive

## ✅ Checklist Pré-Deploy

- [x] Keep-alive implementado
- [x] Jobs configurados
- [x] Documentação criada
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy no Railway

## 📋 Passo a Passo

### 1. Commit das Mudanças

```bash
# Adiciona todos os arquivos
git add .

# Commit com mensagem descritiva
git commit -m "feat: adiciona keep-alive para evitar sleep no Railway"

# Push para o repositório
git push origin main
```

### 2. Deploy no Railway

#### Opção A: Deploy Automático (se já conectado)

O Railway detecta o push e faz deploy automaticamente! 🎉

#### Opção B: Deploy Manual

1. Acesse [railway.app](https://railway.app)
2. Faça login
3. Selecione seu projeto
4. Clique em **"Deploy"**

### 3. Configurar Variáveis de Ambiente

No painel do Railway, vá em **Variables** e adicione:

```env
# Telegram (obrigatório)
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
GROUP_ID=-1003536252896

# Gemini AI (obrigatório)
GEMINI_API_KEY=sua_chave_gemini

# Tópicos do Telegram
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

# Railway define automaticamente (não precisa adicionar)
# RAILWAY_PUBLIC_DOMAIN=seu-app.up.railway.app
# PORT=8000
```

### 4. Verificar Deploy

#### A. Logs do Railway

```bash
railway logs --tail
```

Procure por:
```
✅ Bot online!
✅ Servidor web: http://0.0.0.0:8000
✅ Jobs agendados (incluindo keep-alive)
💓 Keep-alive: bot está acordado
```

#### B. Health Check

```bash
curl https://seu-app.up.railway.app/health
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

#### C. Testar no Telegram

1. Abra o Telegram
2. Vá para o grupo "Documentos Ranny"
3. Envie: "oi"
4. Bot deve responder imediatamente! ✅

### 5. Monitorar Keep-Alive

Aguarde 10 minutos e verifique os logs:

```bash
railway logs | grep "Keep-alive"
```

Deve aparecer:
```
💓 Keep-alive: bot está acordado
💓 Keep-alive: bot está acordado
💓 Keep-alive: bot está acordado
```

## 🔧 Troubleshooting

### Bot não responde

**1. Verifique se está rodando:**
```bash
railway logs --tail
```

**2. Verifique variáveis:**
```bash
railway variables
```

**3. Reinicie o serviço:**
```bash
railway restart
```

### Keep-alive não funciona

**1. Verifique BASE_URL:**
```bash
railway logs | grep "BASE_URL"
```

**2. Verifique jobs:**
```bash
railway logs | grep "Jobs agendados"
```

Deve mostrar:
```
✅ Jobs agendados (incluindo keep-alive)
```

**3. Teste manualmente:**
```bash
curl https://seu-app.up.railway.app/health
```

### Erro "Connection refused"

O keep-alive tenta conectar antes do servidor estar pronto.

**Solução:** Aguarde 1-2 minutos após o deploy. O erro deve parar.

### Bot dorme mesmo com keep-alive

**Possíveis causas:**

1. **Plano gratuito esgotado** (500h/mês)
   - Solução: Upgrade para $5/mês

2. **Intervalo muito longo**
   - Solução: Reduza para 5 minutos

3. **Railway com problemas**
   - Solução: Verifique status em [railway.app/status](https://railway.app/status)

## 📊 Monitoramento Contínuo

### Dashboard do Railway

Acesse: `https://railway.app/project/seu-projeto`

Monitore:
- **CPU Usage** - Deve ficar baixo (~5-10%)
- **Memory** - Deve ficar estável (~100-200MB)
- **Network** - Pequenos picos a cada 10 min (keep-alive)

### Logs em Tempo Real

```bash
railway logs --tail
```

### Alertas

Configure alertas no Railway:
1. Settings > Notifications
2. Adicione email ou Slack
3. Receba alertas de crashes

## 💰 Custos

### Plano Gratuito
- **500 horas/mês** (~20 dias)
- **Com keep-alive:** Esgota em ~20 dias
- **Custo:** $0

### Plano Hobby ($5/mês)
- **Horas ilimitadas**
- **Recursos garantidos**
- **Suporte prioritário**
- **Custo:** $5/mês

### Recomendação

Para uso em produção: **Upgrade para Hobby** ($5/mês)

Benefícios:
- ✅ Bot 24/7 sem preocupações
- ✅ Recursos garantidos
- ✅ Suporte melhor
- ✅ Sem limite de horas

## 🎯 Próximos Passos

Após deploy bem-sucedido:

1. ✅ **Testar todas as funcionalidades**
   - Fechamento de caixa
   - Lembretes
   - Upload de documentos
   - Busca

2. ✅ **Treinar a Ranny**
   - Mostrar como usar
   - Explicar comandos
   - Responder dúvidas

3. ✅ **Monitorar por 1 semana**
   - Ver logs diariamente
   - Verificar alertas
   - Ajustar se necessário

4. ✅ **Configurar backup**
   - Exportar banco SQLite
   - Guardar em local seguro
   - Agendar backups semanais

## 📞 Suporte

### Problemas Comuns

**Bot não inicia:**
- Verifique variáveis de ambiente
- Veja logs de erro
- Reinicie o serviço

**Keep-alive não funciona:**
- Aguarde 10 minutos
- Verifique logs
- Teste health check manualmente

**Custos altos:**
- Considere Render.com (750h grátis)
- Ou Fly.io (3 VMs grátis)
- Ou VPS barato (~€3/mês)

### Documentação Completa

- `assistente-ranny/README.md` - Documentação técnica
- `assistente-ranny/KEEP_ALIVE_RAILWAY.md` - Keep-alive detalhado
- `assistente-ranny/DEPLOY_RAILWAY.md` - Deploy completo
- `GUIA_PARA_RANNY.md` - Manual do usuário

---

## ✅ Checklist Final

Antes de considerar concluído:

- [ ] Deploy feito com sucesso
- [ ] Bot responde no Telegram
- [ ] Health check retorna 200
- [ ] Keep-alive aparece nos logs
- [ ] Jobs agendados funcionando
- [ ] Ranny testou e aprovou
- [ ] Documentação entregue
- [ ] Backup configurado

---

**Deploy:** 02/02/2026  
**Versão:** 3.1.0 (com keep-alive)  
**Status:** 🚀 Pronto para produção!
