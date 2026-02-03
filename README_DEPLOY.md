# 🚀 Deploy do Assistente Ranny - README

## 📋 Resumo Executivo

Você tem um bot Telegram funcional que precisa ficar online 24/7. Implementamos **keep-alive** para evitar que durma, e agora você precisa escolher uma plataforma **gratuita** para hospedar.

## 🎯 Recomendação: Render.com

**Por quê?**
- ✅ **750 horas/mês grátis** (suficiente para 31 dias completos)
- ✅ **Não precisa cartão de crédito**
- ✅ **Deploy em 5 minutos**
- ✅ **Keep-alive funciona perfeitamente**

## ⚡ Deploy Rápido (5 minutos)

### 1. Acesse Render.com
```
https://render.com → Login com GitHub
```

### 2. Novo Serviço
```
New + → Web Service → Conectar seu repositório
```

### 3. Configurar
```
Name: assistente-ranny
Root Directory: assistente-ranny
Build: pip install -r requirements.txt
Start: python bot.py
Health Check: /health
Plan: Free
```

### 4. Variáveis de Ambiente
```env
TELEGRAM_BOT_TOKEN=seu_token
GEMINI_API_KEY=sua_chave
GROUP_ID=-1003536252896
```

### 5. Deploy!
```
Create Web Service → Aguardar 2-3 minutos
```

## ✅ Verificar

### Logs
```
✅ Bot online!
✅ Jobs agendados (incluindo keep-alive)
💓 Keep-alive: bot está acordado
```

### Telegram
```
Enviar: "oi"
Bot responde: "Oi! Tô aqui pra te ajudar 😊"
```

## 📊 O Que Foi Implementado

### Keep-Alive Automático

**Arquivo:** `assistente-ranny/jobs.py`
```python
async def keep_alive():
    """Faz requisição ao /health a cada 10 minutos"""
    response = await client.get(f"{BASE_URL}/health")
    return response.status_code == 200
```

**Configuração:** `assistente-ranny/bot.py`
```python
add_interval_job(jobs.keep_alive, job_id='keep_alive', minutes=10)
```

**Resultado:**
- Bot faz requisição a si mesmo a cada 10 minutos
- Render detecta atividade e mantém bot acordado
- Lembretes e alertas funcionam 24/7

## 📚 Documentação Disponível

### Guias de Deploy
- `DEPLOY_RENDER_RAPIDO.md` - Deploy em 5 minutos ⚡
- `DEPLOY_RENDER.md` - Guia completo e detalhado
- `ESCOLHA_SUA_PLATAFORMA.md` - Comparação de opções

### Documentação Técnica
- `KEEP_ALIVE_RAILWAY.md` - Como funciona o keep-alive
- `COMPARACAO_PLATAFORMAS.md` - Render vs Railway vs Fly.io
- `SOLUCAO_KEEP_ALIVE.md` - Solução implementada

### Guias do Bot
- `assistente-ranny/README.md` - Documentação completa do bot
- `GUIA_PARA_RANNY.md` - Manual do usuário
- `README_PROJETO_COMPLETO.md` - Visão geral do projeto

## 🆚 Comparação de Plataformas

| Plataforma | Horas/mês | Custo | Deploy | Recomendado |
|-----------|-----------|-------|--------|-------------|
| **Render** | 750h | $0 | 5 min | ✅ SIM |
| Fly.io | Ilimitado | $0 | 10 min | ✅ Sim |
| Railway | 500h | $0 | 5 min | ⚠️ Só 20 dias |
| Heroku | 550h | $0 | 5 min | ⚠️ Precisa cartão |

**Vencedor:** 🏆 **Render.com**

## 💰 Custos

### Render.com Free Tier
```
✅ 750 horas/mês (31 dias completos)
✅ 512 MB RAM
✅ Bandwidth ilimitado
✅ SSL grátis
✅ Deploy automático
✅ Logs ilimitados

Custo: $0/mês
```

### Cálculo de Horas
```
Bot 24/7 = 24h × 31 dias = 744 horas/mês
Render Free = 750 horas/mês
Sobra = 6 horas 🎉

Conclusão: PERFEITO!
```

## 🔄 Fluxo de Trabalho

### Desenvolvimento
```bash
# Fazer mudanças no código
git add .
git commit -m "feat: nova funcionalidade"
git push
```

### Deploy Automático
```
Render detecta push → Rebuild → Deploy → Bot atualizado
```

### Monitoramento
```
Dashboard Render → Logs → Ver keep-alive funcionando
```

## 🎯 Próximos Passos

### 1. Deploy Inicial (Hoje)
- [ ] Criar conta no Render
- [ ] Conectar repositório
- [ ] Configurar variáveis
- [ ] Deploy
- [ ] Testar bot

### 2. Verificação (Primeira Semana)
- [ ] Monitorar logs diariamente
- [ ] Verificar keep-alive funcionando
- [ ] Testar lembretes e alertas
- [ ] Confirmar uptime 100%

### 3. Uso em Produção
- [ ] Treinar Ranny
- [ ] Documentar processos
- [ ] Configurar backup
- [ ] Monitorar uso de horas

## 🆘 Suporte

### Problemas Comuns

**Bot não inicia:**
1. Verificar logs no dashboard
2. Verificar variáveis de ambiente
3. Rebuild manual

**Keep-alive não funciona:**
1. Aguardar 10 minutos
2. Verificar logs: `💓 Keep-alive`
3. Testar health check manualmente

**Bot dorme:**
1. Verificar uso de horas (deve ter sobra)
2. Verificar intervalo do keep-alive (10 min)
3. Ver logs de erro

### Onde Buscar Ajuda

1. **Documentação:** Veja os arquivos `.md` neste projeto
2. **Render Docs:** [render.com/docs](https://render.com/docs)
3. **Render Community:** [community.render.com](https://community.render.com)
4. **Discord Render:** [discord.gg/render](https://discord.gg/render)

## 📈 Métricas de Sucesso

### Após Deploy Bem-Sucedido

✅ **Bot responde no Telegram**  
✅ **Health check retorna 200**  
✅ **Keep-alive aparece nos logs a cada 10 min**  
✅ **Lembretes disparam no horário**  
✅ **Alertas funcionam**  
✅ **Uptime 100%**  

### Monitoramento Contínuo

- **CPU:** ~5-10% (normal)
- **Memory:** ~100-200MB (normal)
- **Uptime:** 100% (objetivo)
- **Response time:** <100ms (objetivo)

## 🎉 Resultado Final

Com o deploy no Render.com você terá:

✅ **Bot online 24/7**  
✅ **Keep-alive funcionando**  
✅ **Lembretes e alertas automáticos**  
✅ **Totalmente grátis**  
✅ **Fácil de manter**  

**Custo:** $0/mês  
**Esforço:** 5 minutos de setup  
**Resultado:** Bot profissional e confiável! 🚀

---

## 📞 Contato

**Projeto:** Assistente Ranny V3  
**Versão:** 3.1.0 (com keep-alive)  
**Status:** ✅ Pronto para deploy  
**Data:** 02/02/2026  

---

## 🚀 Comece Agora!

**Guia recomendado:** `DEPLOY_RENDER_RAPIDO.md`

**Tempo estimado:** 5 minutos

**Dificuldade:** ⭐ Fácil

**Vamos lá!** 🎯
