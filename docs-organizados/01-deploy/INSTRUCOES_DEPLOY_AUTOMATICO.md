# 🤖 Deploy Automático - Instruções

## ✅ O Que o Script Faz

O script `deploy_automatico.py` automatiza **TODO** o processo de deploy:

1. ✅ Cria repositório no GitHub (via Playwright)
2. ✅ Faz push do código
3. ✅ Faz login no Render.com (via Playwright)
4. ✅ Cria novo serviço
5. ✅ Configura variáveis de ambiente
6. ✅ Inicia deploy
7. ✅ Verifica se funcionou

**Você só precisa fornecer as credenciais!**

---

## 🚀 Como Executar

### 1. Preparar Credenciais

Tenha em mãos:

- **Telegram:** Token do BotFather
- **Gemini:** Chave da API
- **GitHub:** Username e Password/Token
- **Render:** Email e Password

### 2. Executar Script

```bash
python deploy_automatico.py
```

### 3. Fornecer Credenciais

O script vai pedir:

```
🔐 CONFIGURAÇÃO DE CREDENCIAIS
============================================================

📱 TELEGRAM:
Token do BotFather: [cole aqui]

🤖 GEMINI AI:
Chave da API Gemini: [cole aqui]

🐙 GITHUB:
Username: [seu username]
Password/Token: [sua senha ou token]

🚀 RENDER.COM:
Você já tem conta no Render? (s/n): s
Email: [seu email]
Password: [sua senha]
```

### 4. Aguardar

O script vai:
- Abrir navegador automaticamente
- Fazer login no GitHub
- Criar repositório
- Fazer push do código
- Fazer login no Render
- Criar serviço
- Configurar tudo
- Fazer deploy

**Tempo estimado:** 5-10 minutos

### 5. Verificar

Ao final, o script mostra:

```
🎉 DEPLOY CONCLUÍDO COM SUCESSO!
============================================================

🌐 URL: https://assistente-ranny.onrender.com
📊 Health: https://assistente-ranny.onrender.com/health

✅ Próximos passos:
  1. Testar bot no Telegram
  2. Enviar mensagem: 'oi'
  3. Verificar logs no Render
  4. Aguardar 10 min e verificar keep-alive
```

---

## 📋 Pré-requisitos

### Contas Necessárias

- ✅ Conta no GitHub (grátis)
- ✅ Conta no Render.com (grátis)
- ✅ Token do Telegram (BotFather)
- ✅ Chave do Gemini AI

### Dependências Instaladas

```bash
✅ playwright
✅ httpx
✅ chromium (navegador)
```

Já instalei tudo para você! ✅

---

## 🎯 O Que Acontece Durante o Deploy

### Fase 1: GitHub (2 min)

```
🐙 CRIANDO REPOSITÓRIO NO GITHUB...
  → Acessando GitHub...
  → Fazendo login...
  ✅ Login realizado!
  → Criando repositório...
  ✅ Repositório criado: https://github.com/SEU_USER/assistente-ranny
```

### Fase 2: Push (1 min)

```
📤 ENVIANDO CÓDIGO PARA GITHUB...
  → Adicionando remote...
  → Renomeando branch para main...
  → Fazendo push...
  ✅ Código enviado com sucesso!
```

### Fase 3: Render (5 min)

```
🚀 FAZENDO DEPLOY NO RENDER.COM...
  → Acessando Render...
  → Fazendo login...
  ✅ Login realizado!
  → Criando novo serviço...
  → Conectando repositório...
  → Configurando serviço...
  → Adicionando variáveis de ambiente...
  → Iniciando deploy...
  ✅ Deploy iniciado!
  
⏳ Aguardando build (3-5 minutos)...
  ✅ Deploy concluído!
```

### Fase 4: Verificação (30 seg)

```
🔍 VERIFICANDO DEPLOY...
  ✅ Health check OK!
  📊 Status: healthy
  🤖 Serviço: assistente-ranny
  📦 Versão: 3.0.0
  ✅ Keep-alive configurado! (4 jobs)
```

---

## 🎬 Demonstração Visual

O script abre um navegador e você pode ver tudo acontecendo:

1. **GitHub:**
   - Login automático
   - Criação do repositório
   - Configuração

2. **Render:**
   - Login automático
   - Criação do serviço
   - Configuração de variáveis
   - Deploy iniciado

**Você não precisa fazer nada, só assistir!** 🍿

---

## ⚠️ Observações Importantes

### Segurança

- ⚠️ O script usa suas credenciais para fazer login
- ⚠️ As credenciais NÃO são salvas em lugar nenhum
- ⚠️ Tudo acontece localmente no seu computador
- ✅ Você pode ver o código em `deploy_automatico.py`

### Navegador

- O navegador abre em modo **não-headless** (você vê tudo)
- Isso é proposital para você acompanhar o processo
- Se quiser modo invisível, mude `headless=False` para `headless=True`

### Erros

Se algo der errado:
- O script mostra a mensagem de erro
- Você pode executar novamente
- Ou fazer manualmente seguindo os guias

---

## 🆘 Troubleshooting

### "Permission Denied" no GitHub

**Causa:** Senha incorreta ou 2FA ativado

**Solução:** 
1. Use um Personal Access Token em vez de senha
2. Crie em: https://github.com/settings/tokens
3. Permissões: `repo` (full control)

### "Login failed" no Render

**Causa:** Email/senha incorretos

**Solução:**
1. Verifique as credenciais
2. Tente fazer login manual primeiro
3. Execute o script novamente

### "Repository already exists"

**Causa:** Repositório já foi criado

**Solução:**
1. Delete o repositório no GitHub
2. Ou mude o nome no script
3. Execute novamente

### Script trava

**Causa:** Timeout ou elemento não encontrado

**Solução:**
1. Pressione Ctrl+C para cancelar
2. Verifique sua conexão
3. Execute novamente

---

## 💡 Dicas

### Primeira Vez

Se é sua primeira vez:
1. Execute o script
2. Acompanhe o processo
3. Veja como tudo funciona
4. Aprenda para próximas vezes

### Próximas Vezes

Para atualizar o bot:
1. Faça mudanças no código
2. Commit: `git commit -am "update"`
3. Push: `git push`
4. Render faz deploy automático!

### Monitoramento

Após o deploy:
1. Acesse: https://dashboard.render.com
2. Clique no seu serviço
3. Veja logs em tempo real
4. Monitore CPU/Memory

---

## 🎉 Resultado Final

Após executar o script, você terá:

✅ **Repositório no GitHub**
✅ **Código versionado**
✅ **Bot deployado no Render**
✅ **Online 24/7**
✅ **Keep-alive funcionando**
✅ **Custo: $0/mês**

**Tudo automático! Sem esforço manual!** 🚀

---

## 📞 Suporte

Se precisar de ajuda:

1. **Veja os logs** do script
2. **Consulte os guias** manuais (se preferir fazer manual)
3. **Execute novamente** (geralmente resolve)

---

**Pronto para começar?**

```bash
python deploy_automatico.py
```

**Boa sorte! 🍀**
