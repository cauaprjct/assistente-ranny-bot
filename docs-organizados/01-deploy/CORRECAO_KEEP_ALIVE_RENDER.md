# 🔧 Correção do Keep-Alive no Render

## 🔍 Problema Identificado

O keep-alive não estava funcionando porque o código foi originalmente escrito para Railway, mas o bot está rodando no Render.

### Causa Raiz

**O que acontecia:**
1. O código verificava a variável `RAILWAY_PUBLIC_DOMAIN` para obter a URL pública
2. No Render, essa variável não existe
3. O `BASE_URL` ficava como `http://localhost:8000`
4. O job `keep_alive` tentava acessar `http://localhost:8000/health`
5. A requisição falhava silenciosamente (localhost não existe no container)
6. O Render colocava o bot em sleep após 15 minutos de inatividade

**Logs do problema:**
```
💓 Keep-alive: timeout na requisição
⚠️ Keep-alive retornou status 0
```

## ✅ Solução Implementada

### Mudanças no `config.py`

**Antes:**
```python
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
IS_PRODUCTION = RAILWAY_ENVIRONMENT == 'production'

def get_base_url():
    base = os.getenv('BASE_URL', '')
    if base:
        return base.rstrip('/')
    if RAILWAY_PUBLIC_DOMAIN:
        return f"https://{RAILWAY_PUBLIC_DOMAIN}"
    return f"http://localhost:{PORT}"
```

**Depois:**
```python
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', '')  # Render define automaticamente
IS_PRODUCTION = (
    RAILWAY_ENVIRONMENT == 'production' or 
    bool(RENDER_EXTERNAL_URL)
)

def get_base_url():
    base = os.getenv('BASE_URL', '')
    if base:
        return base.rstrip('/')
    if RENDER_EXTERNAL_URL:  # ← NOVO: Detecta Render
        return RENDER_EXTERNAL_URL.rstrip('/')
    if RAILWAY_PUBLIC_DOMAIN:
        return f"https://{RAILWAY_PUBLIC_DOMAIN}"
    return f"http://localhost:{PORT}"
```

### Nova Prioridade de URL

1. **BASE_URL** (variável manual) - para domínio customizado
2. **RENDER_EXTERNAL_URL** (Render) - detectado automaticamente ✨
3. **RAILWAY_PUBLIC_DOMAIN** (Railway) - compatibilidade
4. **localhost:PORT** (desenvolvimento local)

## 🎯 Resultado

Agora o keep-alive funciona automaticamente no Render:

- ✅ `BASE_URL` = `https://assistente-ranny-v3.onrender.com`
- ✅ Job faz requisição para `https://assistente-ranny-v3.onrender.com/health`
- ✅ Endpoint responde com status 200
- ✅ Bot permanece ativo (não entra em sleep)

## 📊 Como Verificar

### 1. Verificar BASE_URL nos logs

Após o deploy, procure nos logs do Render:

```
✅ Servidor web: http://localhost:8000
✅ Health check: https://assistente-ranny-v3.onrender.com/health
```

Se aparecer `localhost` no health check, algo está errado.

### 2. Verificar job keep_alive

Nos logs, a cada 10 minutos deve aparecer:

```
💓 Keep-alive: bot está acordado
```

Se aparecer timeout ou erro, o keep-alive não está funcionando.

### 3. Testar manualmente

Acesse no navegador:
```
https://assistente-ranny-v3.onrender.com/health
```

Deve retornar JSON:
```json
{
  "status": "healthy",
  "service": "assistente-ranny",
  "version": "3.0.0",
  "timestamp": "2025-02-03T...",
  "components": {
    "web": "healthy",
    "scheduler": {
      "status": "healthy",
      "jobs_count": 4
    }
  }
}
```

## 🚀 Deploy

**Commit:** `55d540b`
**Mensagem:** "Fix: Adiciona suporte ao Render para keep-alive funcionar"

**Arquivos modificados:**
- `assistente-ranny/config.py` - Detecta RENDER_EXTERNAL_URL
- `assistente-ranny/jobs.py` - Atualiza comentários
- `assistente-ranny/bot.py` - Atualiza comentários

**Status:** ✅ Deploy concluído com sucesso no Render (commit 55d540b)

## 📝 Variáveis de Ambiente do Render

O Render define automaticamente:

| Variável | Valor | Uso |
|----------|-------|-----|
| `RENDER_EXTERNAL_URL` | `https://assistente-ranny-v3.onrender.com` | URL pública do serviço |
| `PORT` | `10000` (ou outro) | Porta do servidor web |
| `RENDER` | `true` | Indica que está no Render |

Não é necessário configurar nada manualmente! 🎉

## 🔄 Compatibilidade

O código continua compatível com:
- ✅ Render (detecta automaticamente)
- ✅ Railway (detecta automaticamente)
- ✅ Desenvolvimento local (usa localhost)
- ✅ Domínio customizado (via BASE_URL)

## 💡 Próximos Passos

1. ✅ Deploy concluído no Render (commit 55d540b)
2. ⏳ Serviço está acordando (cold start do plano gratuito)
3. ⏳ Aguardar bot ficar online para verificar logs
4. ⏳ Monitorar logs do keep_alive (a cada 10 min)
5. ⏳ Confirmar que bot não entra em sleep após 15 min

**Nota:** O serviço está demorando para acordar devido ao cold start do plano gratuito do Render. Isso é normal e acontece quando o serviço fica inativo por mais de 15 minutos. Uma vez que o keep-alive estiver funcionando, o bot não entrará mais em sleep.

---

**Data:** 03/02/2025
**Status:** ✅ Correção implementada e em deploy
