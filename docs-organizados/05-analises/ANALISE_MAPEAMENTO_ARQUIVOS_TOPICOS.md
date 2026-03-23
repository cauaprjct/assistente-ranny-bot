# Análise: Mapeamento de Arquivos nos Tópicos do Telegram

## Problema Identificado

O bot não consegue mapear todos os arquivos de todos os tópicos do grupo Telegram. O usuário tentou implementar essa funcionalidade anteriormente mas não obteve sucesso e acabou desativando o código.

---

## Causa Raiz

### Limitação da API do Telegram Bot

A **Bot API do Telegram NÃO possui** endpoints para:
- Listar mensagens de um tópico específico
- Buscar mensagens por conteúdo
- Listar arquivos de um grupo

**O que a API oferece:**
- `send_document()` - envia arquivo e retorna `message_id`
- `copy_message()` - copia mensagem (precisa conhecer o `message_id`)
- `forward_message()` - encaminha mensagem (precisa conhecer o `message_id`)

### Código Desabilitado

No arquivo [`bot.py`](assistente-ranny/bot.py:573):
```python
# ===== BUSCA DE DOCUMENTOS ===== (DESABILITADO - grupo organizado)
# if await handle_busca_documentos(update, context, text):
#     return
```

A função [`buscar_documentos_telegram()`](assistente-ranny/bot.py:796) está incompleta e retorna lista vazia.

---

## Descoberta Importante

### O Relatório JÁ TEM TODOS OS DADOS!

O arquivo [`relatorio_upload_backup.json`](relatorio_upload_backup.json:1) contém:

```json
{
  "total_arquivos": 302,
  "arquivos": [
    {
      "nome": "GRN (1).pdf",
      "categoria": "EMPRESA",
      "topico": 3,
      "message_id": 1018,
      "file_id": "BQACAgEAAyEGAATSxu_gAAID-ml5..."
    }
  ]
}
```

**Dados disponíveis para cada arquivo:**
| Campo | Descrição | Uso |
|-------|-----------|-----|
| `message_id` | ID da mensagem no Telegram | Localizar mensagem |
| `file_id` | ID do arquivo no Telegram | Reenviar arquivo |
| `topico` | ID do tópico | Informar localização |
| `categoria` | Classificação | Busca semântica |
| `nome` | Nome do arquivo | Busca por nome |

---

## Por que não funciona atualmente?

### 1. Função `add_documento()` não salva message_id e topic_id

Em [`database_sqlite_compat.py`](assistente-ranny/database_sqlite_compat.py:175):
```python
def add_documento(tipo: str, descricao: str, file_id: str, categoria: str,
                  dados_extraidos: dict = None):
    # FALTAM: message_id e topic_id
    doc_id = adicionar_documento(
        nome_arquivo=descricao,
        tipo_documento=tipo,
        categoria=categoria_lower,
        file_id=file_id,
        resumo=resumo_completo,
        tags=[categoria_lower]
        # <- NÃO PASSA message_id nem topic_id
    )
```

### 2. Handlers do bot não capturam message_id

Em [`bot.py`](assistente-ranny/bot.py:448):
```python
# Salva no banco ANTES de enviar para o tópico
doc_record = db.add_documento(
    tipo=document.mime_type,
    descricao=dados.get('descricao', file_name),
    file_id=document.file_id,
    categoria=categoria,
    dados_extraidos=dados
    # FALTA: message_id e topic_id
)

# Envia DEPOIS (message_id não é capturado)
await context.bot.send_message(
    chat_id=config.GROUP_ID,
    text=resposta,
    message_thread_id=topic_id
)
```

### 3. Busca desabilitada

A função de busca está comentada e não há handler ativo.

---

## Solução Proposta

### Parte 1: Corrigir Estrutura de Dados

**Modificar [`database_sqlite_compat.py`](assistente-ranny/database_sqlite_compat.py:175):**

```python
def add_documento(tipo: str, descricao: str, file_id: str, categoria: str,
                  dados_extraidos: dict = None, message_id: int = None, topic_id: int = None):
    """Adiciona documento com localização no Telegram"""
    resumo_completo = descricao
    if dados_extraidos:
        import json
        resumo_completo = f"{descricao}\n\nDados: {json.dumps(dados_extraidos, ensure_ascii=False)}"
    
    categoria_lower = categoria.lower() if categoria else 'outros'
    
    doc_id = adicionar_documento(
        nome_arquivo=descricao or 'documento',
        tipo_documento=tipo,
        categoria=categoria_lower,
        file_id=file_id,
        resumo=resumo_completo,
        tags=[categoria_lower] if categoria_lower else None,
        message_id=message_id,  # NOVO
        topic_id=topic_id       # NOVO
    )
    
    return {'id': doc_id, 'descricao': descricao, 'categoria': categoria_lower}
```

### Parte 2: Re-indexar Arquivos Existentes

**Modificar [`indexar_do_relatorio.py`](assistente-ranny/indexar_do_relatorio.py:42):**

```python
# Passar message_id e topic_id do relatório
db.add_documento(
    tipo=extensao,
    descricao=nome,
    file_id=file_id,
    categoria=categoria,
    message_id=message_id,   # DO RELATÓRIO
    topic_id=topico_id,      # DO RELATÓRIO
    dados_extraidos={
        'caminho_original': caminho,
        'indexado_de': 'relatorio_upload_backup.json'
    }
)
```

### Parte 3: Reabilitar Busca no Bot

**Criar novo handler em [`bot.py`](assistente-ranny/bot.py):**

```python
async def handle_busca_documentos(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Busca e reenvia documentos do banco de dados"""
    
    # Detecta intenção de busca
    termo = detectar_busca_documento(text)
    if not termo:
        return False
    
    # Busca no banco
    docs = db.buscar_documentos(termo, limit=5)
    
    if not docs:
        await update.message.reply_text(
            f"Não encontrei nenhum arquivo com '{termo}'",
            parse_mode=ParseMode.MARKDOWN
        )
        return True
    
    # Mostra resultados
    resposta = f"Encontrei {len(docs)} arquivo(s):\n\n"
    for i, doc in enumerate(docs, 1):
        resposta += f"{i}. **{doc.get('descricao')}**\n"
        resposta += f"   Categoria: {doc.get('categoria', 'outros')}\n\n"
    
    resposta += "\nResponda com o número para receber o arquivo."
    
    # Salva resultados para reenvio
    user_search_results[update.effective_user.id] = docs
    
    await update.message.reply_text(resposta, parse_mode=ParseMode.MARKDOWN)
    return True


async def handle_reenvio_documento(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    """Reenvia documento usando file_id"""
    
    import re
    match = re.search(r'(?:manda|envia|me manda)\s+(?:o\s+)?(\d+)', text.lower())
    
    if not match:
        return False
    
    user_id = update.effective_user.id
    if user_id not in user_search_results:
        await update.message.reply_text("Faça uma busca primeiro. Ex: 'cadê o contrato?'")
        return True
    
    numero = int(match.group(1))
    docs = user_search_results[user_id]
    
    if numero < 1 or numero > len(docs):
        await update.message.reply_text(f"Número inválido. Escolha entre 1 e {len(docs)}")
        return True
    
    doc = docs[numero - 1]
    file_id = doc.get('file_id')
    
    if file_id:
        # Reenvia usando file_id (instantâneo)
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=file_id,
            caption=f"Here is: {doc.get('descricao')}"
        )
    else:
        # Informa localização
        topic_id = doc.get('topic_id')
        categoria = doc.get('categoria', 'outros')
        await update.message.reply_text(
            f"Encontrei no tópico **{categoria.title()}** (ID: {topic_id})",
            parse_mode=ParseMode.MARKDOWN
        )
    
    return True
```

---

## Fluxo Corrigido

### Para Arquivos Novos:

```
1. Usuário envia arquivo
2. Bot analisa com IA
3. Bot classifica categoria
4. Bot ENVIA arquivo para o tópico (captura message_id)
5. Bot SALVA no banco com file_id, message_id, topic_id
```

### Para Busca:

```
1. Usuário: "cadê o contrato?"
2. Bot busca no banco: db.buscar_documentos("contrato")
3. Bot mostra resultados
4. Usuário: "manda o 1"
5. Bot reenvia usando file_id (instantâneo)
```

---

## Impacto no Desempenho

| Operação | Tempo | Observação |
|----------|-------|------------|
| Indexação inicial | ~5 min | Script one-time |
| Busca no banco | <100ms | SQLite/PostgreSQL otimizado |
| Reenvio por file_id | ~1s | Sem download/upload |

---

## Viabilidade Técnica

| Aspecto | Status |
|---------|--------|
| Não requer API especial | OK |
| Usa dados existentes | OK |
| Compatível com arquivos novos | OK |
| Não quebra funcionalidades existentes | OK |

---

## Próximos Passos

1. **Modificar `database_sqlite_compat.py`** - Adicionar parâmetros message_id e topic_id
2. **Modificar handlers de documento/foto** - Capturar message_id após envio
3. **Re-rodar `indexar_do_relatorio.py`** - Popular banco com dados corretos
4. **Reabilitar busca no bot** - Implementar handlers de busca e reenvio
5. **Testar** - Verificar busca e reenvio funcionando

---

## Conclusão

O problema **NÃO é limitação da API do Telegram**, mas sim **implementação incompleta**:

1. Os dados já existem no relatório JSON
2. A estrutura do banco já suporta message_id e topic_id
3. A função de compatibilidade não passa esses parâmetros
4. A busca foi desabilitada em vez de corrigida

A solução é **simples e viável**, requerendo apenas:
- 3 pequenas modificações em código existente
- Re-executar script de indexação
- Testar funcionalidade