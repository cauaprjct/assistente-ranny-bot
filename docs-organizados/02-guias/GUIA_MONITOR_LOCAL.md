# 📁 Monitor Local de Arquivos - Guia Completo

## O que faz?

Script Python que **monitora pastas no PC da Ranny** e **envia automaticamente** arquivos Word/Excel/PDF para o Telegram quando ela salvar.

## ✅ Vantagens

- **Zero custo** - sem Azure, sem APIs pagas
- **Funciona offline** - só precisa internet para enviar
- **Automático** - ela só salva normalmente
- **Simples** - um script Python rodando
- **Sem limitações** - acesso total aos arquivos locais

## 📋 Pré-requisitos

1. **Python 3.8+** instalado no PC da Ranny
2. **Acesso à internet** (para enviar ao Telegram)
3. **Token do bot** do Telegram
4. **Chat ID** do grupo/chat onde enviar

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install watchdog python-telegram-bot python-dotenv
```

### 2. Configurar o .env

Copie `.env.monitor` para `.env` e preencha:

```env
BOT_TOKEN=7924085949:AAH8xYourTokenHere
CHAT_ID=-1002468013579
TOPICO_DOCUMENTOS=123
TOPICO_PLANILHAS=456
TOPICO_PDF=789
```

**Como obter o CHAT_ID:**
1. Adicione o bot no grupo
2. Envie uma mensagem no grupo
3. Acesse: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Procure por `"chat":{"id":-1002468013579}`

**Como obter os IDs dos tópicos:**
1. Envie uma mensagem no tópico
2. Acesse: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Procure por `"message_thread_id":123`

### 3. Configurar pastas monitoradas

Edite o arquivo `monitor_arquivos_local.py` na linha 44:

```python
PASTAS_MONITORADAS = [
    r'C:\Users\Ranny\OneDrive\Documentos',
    r'C:\Users\Ranny\Documents',
    r'C:\Users\Ranny\Desktop',
    r'C:\Users\Ranny\Downloads',  # Adicione mais pastas aqui
]
```

## ▶️ Como usar

### Executar manualmente

```bash
python monitor_arquivos_local.py
```

O script ficará rodando e monitorando as pastas. Pressione `Ctrl+C` para parar.

### Executar automaticamente ao iniciar o Windows

#### Opção 1: Criar atalho na pasta Inicializar

1. Crie um arquivo `iniciar_monitor.bat`:

```batch
@echo off
cd /d "C:\caminho\para\o\script"
python monitor_arquivos_local.py
```

2. Pressione `Win+R` e digite: `shell:startup`
3. Copie o arquivo `.bat` para essa pasta

#### Opção 2: Criar serviço do Windows (mais avançado)

Use o NSSM (Non-Sucking Service Manager):

```bash
# Baixar NSSM: https://nssm.cc/download
nssm install MonitorArquivos "C:\Python\python.exe" "C:\caminho\monitor_arquivos_local.py"
nssm start MonitorArquivos
```

## 📊 Como funciona

```
┌─────────────────┐
│  PC da Ranny    │
│                 │
│  1. Salva       │
│     arquivo.docx│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Monitor Local  │
│  (Python)       │
│                 │
│  2. Detecta     │
│     mudança     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Telegram Bot   │
│                 │
│  3. Envia para  │
│     tópico      │
└─────────────────┘
```

## 🎯 Fluxo de trabalho

1. **Ranny salva** um arquivo Word/Excel/PDF
2. **Monitor detecta** a mudança na pasta
3. **Aguarda 2 segundos** (arquivo terminar de salvar)
4. **Classifica** por extensão (.docx → Documentos, .xlsx → Planilhas)
5. **Envia** para o tópico correto no Telegram
6. **Registra** no log

## 📝 Logs

O script gera logs em:
- **Console**: saída em tempo real
- **Arquivo**: `monitor_arquivos.log`

Exemplo de log:
```
2026-02-03 14:30:15 - INFO - 🚀 Iniciando Monitor de Arquivos Local
2026-02-03 14:30:15 - INFO - ✅ Configuração OK
2026-02-03 14:30:15 - INFO - 👀 Monitorando: C:\Users\Ranny\OneDrive\Documentos
2026-02-03 14:32:45 - INFO - Arquivo criado: relatorio.docx (45678 bytes)
2026-02-03 14:32:47 - INFO - ✅ Arquivo enviado com sucesso: relatorio.docx
```

## ⚙️ Configurações avançadas

### Adicionar mais extensões

Edite linha 49:

```python
EXTENSOES_MONITORADAS = {'.docx', '.xlsx', '.pdf', '.doc', '.xls', '.pptx', '.txt'}
```

### Ajustar tempo de cooldown

Edite linha 52 (evita enviar o mesmo arquivo múltiplas vezes):

```python
TEMPO_COOLDOWN = 10  # segundos
```

### Adicionar filtros por nome

Adicione na função `processar_arquivo`:

```python
# Ignorar arquivos temporários do Office
if nome_arquivo.startswith('~$'):
    return

# Ignorar arquivos de backup
if nome_arquivo.endswith('.bak'):
    return
```

## 🔧 Troubleshooting

### Erro: "BOT_TOKEN não configurado"
- Verifique se o arquivo `.env` existe
- Verifique se o token está correto

### Erro: "Nenhuma pasta monitorada existe"
- Verifique os caminhos em `PASTAS_MONITORADAS`
- Use caminhos absolutos: `r'C:\Users\Ranny\...'`

### Arquivos não são enviados
- Verifique se o bot tem permissão no grupo
- Verifique se o CHAT_ID está correto
- Verifique os logs em `monitor_arquivos.log`

### Arquivos enviados múltiplas vezes
- Aumente o `TEMPO_COOLDOWN`
- Verifique se não há múltiplas instâncias rodando

## 🎨 Personalizações

### Enviar notificação ao iniciar

Adicione no início da função `main()`:

```python
bot = Bot(token=BOT_TOKEN)
asyncio.run(bot.send_message(
    chat_id=CHAT_ID,
    text="🟢 Monitor de arquivos iniciado!"
))
```

### Adicionar preview de imagens

Para arquivos de imagem, use `send_photo` em vez de `send_document`.

### Comprimir arquivos grandes

Adicione compressão ZIP para arquivos >10MB antes de enviar.

## 📱 Comandos úteis

### Ver processos rodando
```bash
# Windows
tasklist | findstr python

# Matar processo
taskkill /F /PID <pid>
```

### Ver logs em tempo real
```bash
# Windows PowerShell
Get-Content monitor_arquivos.log -Wait -Tail 20
```

## 🔐 Segurança

- ✅ Token do bot fica no `.env` (não commitar no Git)
- ✅ Arquivos são enviados diretamente (sem armazenamento intermediário)
- ✅ Logs não contêm informações sensíveis
- ⚠️ Cuidado com arquivos confidenciais (o bot envia tudo automaticamente)

## 🆚 Comparação: Local vs Azure

| Aspecto | Monitor Local | Azure OneDrive |
|---------|---------------|----------------|
| **Custo** | Grátis | Requer cartão |
| **Setup** | 5 minutos | 30+ minutos |
| **Limitações** | Nenhuma | Quotas de API |
| **Offline** | Funciona | Não funciona |
| **Manutenção** | Simples | Complexa |
| **Dependências** | Python | Azure AD + Graph API |

## ✅ Próximos passos

1. ✅ Instalar dependências
2. ✅ Configurar `.env`
3. ✅ Testar manualmente
4. ✅ Configurar inicialização automática
5. ✅ Monitorar logs por alguns dias
6. ✅ Ajustar configurações conforme necessário

## 💡 Dicas

- **Teste primeiro** com uma pasta de teste
- **Monitore os logs** nos primeiros dias
- **Ajuste o cooldown** se houver duplicatas
- **Adicione filtros** para arquivos temporários
- **Faça backup** do `.env` em local seguro

---

**Pronto!** Agora a Ranny pode salvar arquivos normalmente e eles aparecerão automaticamente no Telegram! 🎉
