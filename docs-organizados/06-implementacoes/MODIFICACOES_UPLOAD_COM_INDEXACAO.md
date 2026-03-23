# 📝 Modificações no Script de Upload com Indexação

## 🎯 Objetivo

Modificar o script `organizar_backup_telegram.py` para que os arquivos sejam **automaticamente indexados no banco de dados SQLite** durante o upload para o Telegram.

## ✅ O Que Foi Feito

### 1. Importação do Database Adapter

Adicionado import do módulo `database_adapter` para permitir indexação:

```python
# Importa database adapter para indexar arquivos
try:
    import database_adapter as db
    DB_DISPONIVEL = True
except ImportError as e:
    print(f"⚠️  Database adapter não disponível: {e}")
    DB_DISPONIVEL = False
```

### 2. Método para Determinar MIME Type

Criado método `_get_mime_type()` que retorna o tipo MIME correto baseado na extensão do arquivo:

```python
def _get_mime_type(self, extensao):
    """Retorna MIME type baseado na extensão"""
    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        # ... outros tipos
    }
    return mime_types.get(extensao.lower(), 'application/octet-stream')
```

### 3. Modificação do Método `fazer_upload()`

O método agora:

1. **Envia o arquivo** para o Telegram
2. **Captura** `message_id` e `file_id` do resultado
3. **Indexa no banco** usando `db.add_documento()`
4. **Salva metadados** no registro do arquivo

```python
# Faz upload
result = await self.bot.send_document(...)

# Salva IDs
arquivo['message_id'] = result.message_id
arquivo['file_id'] = result.document.file_id

# Indexa no banco
if DB_DISPONIVEL:
    db.add_documento(
        tipo=mime_type,
        descricao=arquivo['nome'],
        file_id=result.document.file_id,
        categoria=arquivo['categoria'],
        message_id=result.message_id,
        topic_id=topico_id,
        dados_extraidos={
            'file_name': arquivo['nome'],
            'caminho_relativo': arquivo['caminho_relativo'],
            'tamanho_mb': arquivo['tamanho_mb'],
            'extensao': arquivo['extensao']
        }
    )
```

### 4. Estatísticas Aprimoradas

O método agora mostra:
- ✅ Arquivos enviados com sucesso
- ❌ Erros durante upload
- 📊 **Quantidade de arquivos indexados no banco**

## 🧪 Como Testar

### Teste Rápido (3 arquivos)

```bash
python testar_upload_com_indexacao.py
```

Este script:
1. Verifica quantos documentos existem no banco ANTES
2. Faz upload de 3 arquivos
3. Verifica quantos documentos existem DEPOIS
4. Mostra a diferença (novos indexados)
5. Gera relatório em `relatorio_teste_indexacao.json`

### Upload Completo

```bash
python organizar_backup_telegram.py
```

Escolha a opção desejada:
- **Opção 1**: Upload de TODOS os arquivos (~300)
- **Opção 2**: Upload de 10 arquivos (teste)
- **Opção 3**: Simulação (dry run)

## 📊 Benefícios

### Antes ❌
- Arquivos enviados para Telegram
- **NÃO indexados** no banco
- Busca **NÃO funcionava** para arquivos antigos
- Ranny precisava navegar pelos tópicos manualmente

### Depois ✅
- Arquivos enviados para Telegram
- **Automaticamente indexados** no banco
- Busca **funciona** para todos os arquivos
- Ranny pode buscar com: "cadê o contrato?", "procura boleto", etc.

## 🔍 Verificação

Para verificar se os arquivos foram indexados:

```python
import sys
sys.path.insert(0, 'assistente-ranny')
import database_adapter as db

# Busca todos os documentos
docs = db.buscar_documentos('')
print(f"Total de documentos indexados: {len(docs)}")

# Busca específica
docs = db.buscar_documentos('boleto')
print(f"Boletos encontrados: {len(docs)}")
```

## 📝 Relatório JSON

O arquivo `relatorio_upload_backup.json` agora inclui:

```json
{
  "arquivos": [
    {
      "nome": "arquivo.pdf",
      "categoria": "FINANCEIRO",
      "message_id": 12345,
      "file_id": "BQACAgEAAxkBAAI..."
    }
  ]
}
```

## ⚠️ Observações Importantes

1. **Rate Limits**: O script tem delay de 2 segundos entre uploads para evitar bloqueio do Telegram
2. **Banco SQLite**: Os dados são salvos em `assistente-ranny/bot_database.db`
3. **Backup**: Sempre faça backup do banco antes de operações em massa
4. **Erros**: Se houver erro na indexação, o arquivo ainda é enviado (não bloqueia o upload)

## 🚀 Próximos Passos

Agora que o script está modificado:

1. ✅ **Teste com 3 arquivos** usando `testar_upload_com_indexacao.py`
2. ✅ **Verifique** se os arquivos foram indexados no banco
3. ✅ **Teste a busca** no bot: "cadê o arquivo X?"
4. ✅ **Upload completo** quando confirmar que está funcionando

## 💡 Dica para Ranny

Quando você enviar **novos arquivos** no futuro, o bot já indexa automaticamente! Mas para os **300 arquivos antigos** que já estão no Telegram, você tem 3 opções:

1. **Reenviar** usando este script modificado (recomendado para backups futuros)
2. **Indexar manualmente** usando `indexar_arquivos_telegram.py` (lento, rate limits)
3. **Deixar como está** e só buscar nos tópicos (funciona, mas menos prático)

---

**Data da Modificação**: 27/01/2026
**Versão**: 2.0 - Upload com Indexação Automática
