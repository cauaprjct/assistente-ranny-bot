# 🚀 Guia de Migração para PostgreSQL

**Data:** 02/02/2026  
**Objetivo:** Migrar bot do SQLite (efêmero) para PostgreSQL (persistente)

---

## 📋 O QUE FOI IMPLEMENTADO

### 1. Novo Módulo PostgreSQL ✅
- `assistente-ranny/database_postgres.py`
- Todas as funções do SQLite adaptadas para PostgreSQL
- Usa `psycopg2` para conexão
- Índices otimizados para busca rápida

### 2. Adaptador Inteligente ✅
- `assistente-ranny/database_adapter.py` atualizado
- Detecta automaticamente qual banco usar:
  - Se `DATABASE_URL` existe → PostgreSQL
  - Se não → SQLite (fallback)

### 3. Script de Migração ✅
- `assistente-ranny/migrar_para_postgres.py`
- Lê `relatorio_upload_backup.json`
- Indexa todos os 300 arquivos no PostgreSQL
- Roda automaticamente no deploy (via Procfile)

### 4. Indexação Automática ✅
- Bot já indexa novos arquivos automaticamente
- Código em `bot.py` (linhas 150-250)
- Captura `message_id` e `file_id`

### 5. Dependências Atualizadas ✅
- `requirements.txt` com `psycopg2-binary`
- `Procfile` com comando `release`

---

## 🎯 COMO FAZER O DEPLOY

### Passo 1: Criar Banco PostgreSQL no Render

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name:** `assistente-ranny-db`
   - **Database:** `assistente_ranny`
   - **User:** (gerado automaticamente)
   - **Region:** `Oregon (US West)`
   - **Plan:** **Free** (suficiente para começar)
4. Clique em **"Create Database"**
5. Aguarde ~2 minutos para provisionar

### Passo 2: Copiar DATABASE_URL

1. No banco criado, vá em **"Info"**
2. Copie a **"Internal Database URL"** (começa com `postgres://`)
3. Exemplo:
   ```
   postgres://user:pass@dpg-xxxxx-a.oregon-postgres.render.com/assistente_ranny
   ```

### Passo 3: Configurar Variável no Web Service

1. Vá no seu Web Service (onde o bot está rodando)
2. Clique em **"Environment"**
3. Adicione nova variável:
   - **Key:** `DATABASE_URL`
   - **Value:** (cole a URL copiada)
4. Clique em **"Save Changes"**

### Passo 4: Upload do Relatório JSON

O script de migração precisa do arquivo `relatorio_upload_backup.json`.

**Opção A: Via Git (Recomendado)**
```bash
# Na raiz do projeto
git add relatorio_upload_backup.json
git commit -m "feat: adiciona relatório para migração"
git push
```

**Opção B: Via Render Shell**
1. No Web Service, vá em **"Shell"**
2. Execute:
   ```bash
   cat > relatorio_upload_backup.json << 'EOF'
   # Cole o conteúdo do arquivo aqui
   EOF
   ```

### Passo 5: Fazer Deploy

**Opção A: Deploy Automático (se conectado ao Git)**
```bash
cd assistente-ranny
git add .
git commit -m "feat: migração para PostgreSQL"
git push
```

O Render detecta o push e faz deploy automaticamente.

**Opção B: Deploy Manual**
1. No Render Dashboard, vá no Web Service
2. Clique em **"Manual Deploy"** → **"Deploy latest commit"**

### Passo 6: Acompanhar Migração

1. No Render, vá em **"Logs"**
2. Procure por:
   ```
   🔄 MIGRAÇÃO PARA POSTGRESQL
   ✅ Tabelas PostgreSQL criadas/verificadas
   📂 Carregando relatório de upload...
   ✅ Relatório carregado: 302 arquivos
   🔄 Indexando arquivos no PostgreSQL...
   ✅ 50 arquivos indexados...
   ✅ 100 arquivos indexados...
   ...
   ✅ MIGRAÇÃO CONCLUÍDA!
   ```

3. Verifique o resumo:
   ```
   Total de arquivos no relatório: 302
   ✅ Indexados com sucesso: 300
   ⚠️  Sem message_id: 2
   📈 Total no banco agora: 300
   ```

### Passo 7: Testar no Telegram

1. Abra o Telegram
2. Envie: `buscar boleto`
3. Deve retornar 10 boletos ✅

---

## 🔍 VERIFICAÇÃO

### Verificar Banco Está Sendo Usado

Nos logs do Render, procure por:
- ✅ `🟢 Usando PostgreSQL (banco persistente)`
- ❌ `🟡 Usando SQLite (banco local)` ← Se aparecer isso, DATABASE_URL não está configurada

### Verificar Migração Foi Bem-Sucedida

Execute no Render Shell:
```bash
python -c "import database_adapter as db; print(f'Total: {db.contar_documentos()}')"
```

Deve retornar: `Total: 300` (ou próximo disso)

### Verificar Busca Funciona

No Telegram:
```
buscar boleto
buscar nubank
buscar contrato
lista todos
```

Todos devem retornar resultados!

---

## 🐛 TROUBLESHOOTING

### Erro: "DATABASE_URL não configurada"

**Solução:**
1. Verifique se criou o banco PostgreSQL
2. Verifique se copiou a URL correta
3. Verifique se adicionou a variável no Web Service
4. Faça novo deploy

### Erro: "psycopg2 não instalado"

**Solução:**
1. Verifique se `requirements.txt` tem `psycopg2-binary>=2.9.9`
2. Faça novo deploy (Render instala automaticamente)

### Erro: "Relatório não encontrado"

**Solução:**
1. Verifique se `relatorio_upload_backup.json` está na raiz do projeto
2. Faça upload via Git ou Shell
3. Faça novo deploy

### Erro: "Tabela já existe"

**Não é erro!** Significa que a tabela já foi criada em deploy anterior.
A migração continua normalmente.

### Busca Não Retorna Resultados

**Diagnóstico:**
1. Verifique logs: `🟢 Usando PostgreSQL`?
2. Verifique migração: `✅ MIGRAÇÃO CONCLUÍDA`?
3. Verifique total: `📈 Total no banco agora: 300`?

**Solução:**
1. Se não migrou, rode manualmente no Shell:
   ```bash
   python migrar_para_postgres.py
   ```
2. Reinicie o serviço

---

## 📊 COMPARAÇÃO: ANTES vs DEPOIS

### ANTES (SQLite)
- ❌ Banco efêmero (perde dados a cada deploy)
- ❌ Busca não funciona no Render
- ❌ Dados só no computador local
- ⚠️ Precisa reindexar após cada deploy

### DEPOIS (PostgreSQL)
- ✅ Banco persistente (mantém dados)
- ✅ Busca funciona perfeitamente
- ✅ Dados acessíveis de qualquer lugar
- ✅ Indexação automática de novos arquivos
- ✅ Escalável e robusto

---

## 🎯 PRÓXIMOS PASSOS

### Após Deploy Bem-Sucedido

1. **Testar Todas as Funcionalidades**
   - Busca de documentos ✅
   - Upload de novos arquivos ✅
   - Lembretes ✅
   - Vencimentos ✅
   - Fechamentos ✅

2. **Monitorar Performance**
   - Tempo de resposta da busca
   - Uso de memória do banco
   - Logs de erro

3. **Backup Regular** (Opcional)
   - Render faz backup automático do PostgreSQL
   - Mas você pode exportar manualmente:
     ```bash
     pg_dump $DATABASE_URL > backup.sql
     ```

4. **Upgrade do Plano** (Se Necessário)
   - Free: 256 MB RAM, 1 GB storage
   - Starter ($7/mês): 1 GB RAM, 10 GB storage
   - Só upgrade se atingir limites

---

## 📝 ARQUIVOS MODIFICADOS

### Novos Arquivos
1. `assistente-ranny/database_postgres.py` - Módulo PostgreSQL
2. `assistente-ranny/migrar_para_postgres.py` - Script de migração
3. `GUIA_MIGRACAO_POSTGRES.md` - Este guia

### Arquivos Modificados
1. `assistente-ranny/database_adapter.py` - Detecção automática
2. `assistente-ranny/requirements.txt` - Adicionado psycopg2
3. `assistente-ranny/Procfile` - Adicionado comando release

### Arquivos Necessários (Já Existem)
1. `relatorio_upload_backup.json` - Relatório de upload
2. `assistente-ranny/bot.py` - Já indexa automaticamente

---

## ✅ CHECKLIST DE DEPLOY

- [ ] Criar banco PostgreSQL no Render
- [ ] Copiar DATABASE_URL
- [ ] Adicionar DATABASE_URL no Web Service
- [ ] Upload do relatorio_upload_backup.json
- [ ] Commit e push das mudanças
- [ ] Aguardar deploy automático
- [ ] Verificar logs: "🟢 Usando PostgreSQL"
- [ ] Verificar logs: "✅ MIGRAÇÃO CONCLUÍDA"
- [ ] Testar busca no Telegram: "buscar boleto"
- [ ] Confirmar 10 boletos retornados
- [ ] Testar upload de novo arquivo
- [ ] Confirmar arquivo foi indexado

---

## 🎉 RESULTADO ESPERADO

Após seguir este guia:

1. ✅ Bot usando PostgreSQL persistente
2. ✅ 300 arquivos indexados
3. ✅ Busca funcionando perfeitamente
4. ✅ Novos arquivos indexados automaticamente
5. ✅ Dados não são perdidos entre deploys
6. ✅ Sistema robusto e escalável

**Tempo estimado:** 15-20 minutos

---

## 📞 SUPORTE

Se encontrar problemas:

1. **Verifique os logs** no Render
2. **Consulte a seção Troubleshooting** acima
3. **Teste localmente** primeiro (opcional):
   ```bash
   export DATABASE_URL="postgresql://..."
   python assistente-ranny/migrar_para_postgres.py
   ```

---

**Boa sorte com o deploy!** 🚀
