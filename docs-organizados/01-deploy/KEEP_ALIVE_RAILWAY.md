# 💓 Keep-Alive no Railway

## 🎯 Problema

O Railway (plano gratuito) coloca serviços em **sleep** após períodos de inatividade para economizar recursos. Isso significa que:

- ⏰ O bot para de responder
- 🔔 Jobs agendados não executam
- 📊 Lembretes não disparam
- ⚠️ Alertas não são enviados

## ✅ Solução Implementada

Adicionamos um **job de keep-alive** que:

1. **Executa a cada 10 minutos**
2. **Faz uma requisição HTTP** ao próprio endpoint `/health`
3. **Mantém o serviço ativo** no Railway
4. **Não consome recursos** significativos

### Como Funciona

```python
# jobs.py
async def keep_alive() -> bool:
    """Faz requisição ao health check a cada 10 minutos"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{BASE_URL}/health")
        return response.status_code == 200
```

```python
# bot.py (configuração do job)
add_interval_job(
    jobs.keep_alive,
    job_id='keep_alive',
    minutes=10  # A cada 10 minutos
)
```

## 📊 Impacto

### Antes (sem keep-alive)
- ❌ Bot dorme após ~15 minutos de inatividade
- ❌ Lembretes não disparam
- ❌ Alertas não funcionam
- ❌ Usuário precisa enviar mensagem para acordar

### Depois (com keep-alive)
- ✅ Bot sempre acordado
- ✅ Lembretes disparam no horário
- ✅ Alertas funcionam 24/7
- ✅ Experiência contínua

## 🔧 Configuração

### Variáveis de Ambiente

O keep-alive usa a variável `BASE_URL` do `config.py`:

```env
# Railway define automaticamente
RAILWAY_PUBLIC_DOMAIN=seu-app.up.railway.app

# Ou configure manualmente
BASE_URL=https://seu-app.up.railway.app
```

### Ajustar Intervalo

Se quiser mudar o intervalo (padrão: 10 minutos):

```python
# bot.py - linha ~XXX
add_interval_job(
    jobs.keep_alive,
    job_id='keep_alive',
    minutes=5  # Mude para 5, 15, 20, etc
)
```

**Recomendações:**
- ⚡ **5 minutos**: Mais seguro, mas mais requisições
- ✅ **10 minutos**: Balanceado (recomendado)
- ⏱️ **15 minutos**: Arriscado, pode dormir entre requisições

## 📈 Monitoramento

### Ver Logs do Keep-Alive

No Railway, vá em **Deployments > Logs** e filtre por:

```
💓 Keep-alive: bot está acordado
```

### Verificar Jobs Ativos

O endpoint `/health` mostra todos os jobs:

```bash
curl https://seu-app.up.railway.app/health
```

Resposta:
```json
{
  "status": "healthy",
  "components": {
    "scheduler": {
      "status": "healthy",
      "jobs_count": 4  // Inclui keep_alive
    }
  }
}
```

## 💰 Consumo de Recursos

### Plano Gratuito Railway
- **Limite**: 500 horas/mês (~20 dias)
- **Com keep-alive**: Usa ~720 horas/mês (30 dias)
- **Solução**: Upgrade para plano pago ($5/mês) ou usar outro serviço

### Alternativas

Se o plano gratuito não for suficiente:

1. **Render.com** (750 horas/mês grátis)
2. **Fly.io** (3 VMs grátis)
3. **Heroku** (550 horas/mês grátis com cartão)
4. **VPS barato** (Contabo, Hetzner ~€3/mês)

## 🔍 Troubleshooting

### Bot ainda dorme

**Possíveis causas:**

1. **BASE_URL incorreta**
   ```bash
   # Verifique no Railway
   echo $RAILWAY_PUBLIC_DOMAIN
   ```

2. **Job não está rodando**
   ```bash
   # Veja os logs
   railway logs
   ```

3. **Firewall/timeout**
   - Railway pode ter limite de requisições
   - Aumente o intervalo para 15 minutos

### Erro "Connection refused"

O keep-alive tenta se conectar antes do servidor web estar pronto.

**Solução**: Adicione delay inicial:

```python
# bot.py
import asyncio

# Após configurar jobs
await asyncio.sleep(30)  # Aguarda 30s antes do primeiro keep-alive
```

### Muitas requisições

Se os logs mostram muitas requisições:

```python
# jobs.py - mude o log level
logger.debug("💓 Keep-alive: bot está acordado")  # Só mostra em DEBUG
```

## 📝 Checklist de Deploy

Antes de fazer deploy no Railway:

- [ ] Variável `RAILWAY_PUBLIC_DOMAIN` configurada (automática)
- [ ] Job `keep_alive` adicionado no `bot.py`
- [ ] Função `keep_alive()` implementada no `jobs.py`
- [ ] Dependência `httpx` no `requirements.txt`
- [ ] Testado localmente com `python bot.py`
- [ ] Logs monitorados após deploy

## 🎉 Resultado Final

Com o keep-alive implementado:

✅ **Bot 24/7 online**  
✅ **Lembretes funcionam**  
✅ **Alertas disparam**  
✅ **Resumos semanais enviados**  
✅ **Experiência contínua para Ranny**

---

**Implementado em:** 02/02/2026  
**Versão:** 3.1.0  
**Status:** ✅ Funcionando
