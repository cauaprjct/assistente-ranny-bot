# 🔑 Como Renovar a API Key do Gemini

**Problema Atual:** A API key do Gemini expirou  
**Erro:** `400 API key expired. Please renew the API key.`

---

## 🚀 Passo a Passo

### 1. Acesse o Google AI Studio
Abra no navegador: https://aistudio.google.com/app/apikey

### 2. Faça Login
Use a conta Google que você usou para criar a API key original.

### 3. Crie uma Nova API Key
- Clique em **"Create API Key"** ou **"Get API Key"**
- Escolha um projeto do Google Cloud (ou crie um novo)
- Copie a nova API key gerada

### 4. Atualize o Arquivo .env
Abra o arquivo `assistente-ranny/.env` e substitua a linha:

```env
# ANTES (API key expirada):
GEMINI_API_KEY=AIzaSyCxUdSoEnZWGq0l8_sMSZGKFjUoETNz8ps

# DEPOIS (nova API key):
GEMINI_API_KEY=SUA_NOVA_API_KEY_AQUI
```

### 5. Reinicie o Bot
Se o bot estiver rodando, reinicie-o para carregar a nova API key.

---

## 🧪 Teste a Nova API Key

Execute o teste de correção de planilhas:

```bash
python test_correcao_planilha.py
```

**Resultado esperado:**
```
✅ Todos os testes passaram! Sistema funcionando corretamente.
```

---

## 📋 Checklist

- [ ] Acessei https://aistudio.google.com/app/apikey
- [ ] Fiz login com minha conta Google
- [ ] Criei uma nova API key
- [ ] Copiei a nova API key
- [ ] Atualizei o arquivo `assistente-ranny/.env`
- [ ] Reiniciei o bot (se estava rodando)
- [ ] Executei o teste `python test_correcao_planilha.py`
- [ ] Todos os testes passaram ✅

---

## ⚠️ Importante

### Segurança da API Key
- ✅ **Nunca compartilhe** sua API key publicamente
- ✅ **Não commite** o arquivo `.env` no Git (já está no .gitignore)
- ✅ **Mantenha backup** da API key em local seguro

### Limites da API
O Gemini tem limites de uso gratuito:
- **Requisições por minuto:** 60
- **Requisições por dia:** 1,500
- **Tokens por minuto:** 32,000

Se ultrapassar, considere:
- Upgrade para plano pago
- Implementar cache de respostas
- Adicionar rate limiting

---

## 🆘 Problemas Comuns

### Erro: "API key not valid"
**Solução:** Verifique se copiou a API key completa, sem espaços extras.

### Erro: "Quota exceeded"
**Solução:** Aguarde alguns minutos ou upgrade para plano pago.

### Erro: "Permission denied"
**Solução:** Verifique se a API do Gemini está habilitada no projeto do Google Cloud.

---

## 📞 Suporte

Se tiver problemas, consulte:
- Documentação oficial: https://ai.google.dev/docs
- Status da API: https://status.cloud.google.com/

---

_Última atualização: 14/02/2026_
