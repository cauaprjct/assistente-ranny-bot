# 🧪 Guia de Teste do Monitor - Passo a Passo

## 📋 Pré-requisitos

Antes de começar, verifique:
- [ ] Python instalado
- [ ] Arquivo `.env` configurado com BOT_TOKEN e CHAT_ID
- [ ] Bot adicionado no grupo do Telegram

---

## 🔍 FASE 1: Teste Manual (SEM inicialização automática)

### Passo 1: Verificar Python
```cmd
python --version
```
**Esperado:** `Python 3.x.x`  
**Se der erro:** Instale Python de https://www.python.org/downloads/

---

### Passo 2: Instalar Dependências
```cmd
pip install watchdog python-telegram-bot python-dotenv
```
**Esperado:** Instalação sem erros  
**Se der erro:** Copie e cole o erro aqui

---

### Passo 3: Verificar .env
```cmd
type .env
```
**Esperado:** Ver BOT_TOKEN e CHAT_ID preenchidos  
**Se não existir:** Copie `.env.monitor` para `.env` e edite

---

### Passo 4: Testar Script Manualmente (COM janela visível)
```cmd
python monitor_arquivos_local.py
```

**O que deve aparecer:**
```
============================================================
🚀 Iniciando Monitor de Arquivos Local
============================================================
✅ Configuração OK
📁 Pastas monitoradas: [...]
📄 Extensões: {'.docx', '.xlsx', '.pdf', ...}
👀 Monitorando: C:\Users\...
✅ Monitor iniciado! Pressione Ctrl+C para parar.
```

**Se aparecer erro:**
- Copie o erro completo
- Verifique se o .env está correto
- Verifique se as pastas em PASTAS_MONITORADAS existem

---

### Passo 5: Testar Envio de Arquivo

**Com o monitor rodando:**

1. Abra o Word/Excel
2. Crie um documento de teste
3. Salve em uma das pastas monitoradas (Desktop, Documentos, etc)
4. Observe o console do monitor

**Esperado no console:**
```
2026-02-03 16:30:15 - INFO - Arquivo criado: teste.docx (1234 bytes)
2026-02-03 16:30:17 - INFO - ✅ Arquivo enviado com sucesso: teste.docx
```

**Esperado no Telegram:**
- Arquivo aparece no grupo/tópico
- Com mensagem: "📄 Arquivo criado: teste.docx"

**Se não funcionar:**
- Verifique se o BOT_TOKEN está correto
- Verifique se o CHAT_ID está correto
- Verifique se o bot tem permissão no grupo
- Copie o erro do console

---

### Passo 6: Parar o Monitor
```
Pressione Ctrl+C no console
```

**Esperado:**
```
⏹️  Parando monitor...
✅ Monitor encerrado.
```

---

## ✅ FASE 2: Teste em Segundo Plano (SEM inicialização automática)

### Passo 7: Iniciar em Segundo Plano
```cmd
iniciar_monitor.bat
```

**Esperado:**
```
🚀 INICIANDO MONITOR DE ARQUIVOS
🔄 Iniciando monitor em segundo plano...
✅ Monitor iniciado com sucesso!
```

**Se der erro:** Copie a mensagem de erro

---

### Passo 8: Verificar Status
```cmd
status_monitor.bat
```

**Esperado:**
```
✅ STATUS: RODANDO
📋 Processos Python em segundo plano:
pythonw.exe    [PID]    ...
```

**Se mostrar PARADO:** O monitor não iniciou, volte ao Passo 4

---

### Passo 9: Testar Envio (em segundo plano)

1. Salve um arquivo Word/Excel/PDF
2. Verifique se aparece no Telegram
3. Abra o log: `ver_log.bat`

**Esperado no log:**
```
✅ Arquivo enviado com sucesso: teste.docx
```

---

### Passo 10: Parar o Monitor
```cmd
parar_monitor.bat
```

**Esperado:**
```
⏹️  PARANDO MONITOR DE ARQUIVOS
🔄 Parando monitor...
✅ Monitor parado com sucesso!
```

---

## 🚀 FASE 3: Teste de Inicialização Automática

### Passo 11: Instalar Inicialização Automática
```cmd
instalar_monitor_automatico.bat
```

**O que vai acontecer:**
1. Verificar Python ✅
2. Verificar script ✅
3. Verificar .env ✅
4. Instalar dependências ✅
5. Criar atalho na pasta Inicializar ✅

**Esperado:**
```
✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
O monitor de arquivos agora vai iniciar automaticamente
toda vez que o Windows iniciar.
```

**Se der erro em algum passo:** Copie o erro e me avise

---

### Passo 12: Verificar Atalho Criado

Abra a pasta Inicializar:
```cmd
explorer "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
```

**Esperado:**
- Ver atalho "Monitor de Arquivos.lnk"
- Ícone de pasta/documento

**Se não existir:** O instalador falhou, copie o erro

---

### Passo 13: Testar Inicialização Manual do Atalho

1. Clique duas vezes no atalho "Monitor de Arquivos.lnk"
2. Execute: `status_monitor.bat`

**Esperado:**
```
✅ STATUS: RODANDO
```

**Se não funcionar:**
- Clique com botão direito no atalho > Propriedades
- Copie o que está em "Destino:" e "Iniciar em:"
- Me envie essas informações

---

### Passo 14: Testar Reinicialização do Windows

**IMPORTANTE: Salve tudo antes!**

1. Reinicie o Windows
2. Após login, aguarde 30 segundos
3. Execute: `status_monitor.bat`

**Esperado:**
```
✅ STATUS: RODANDO
```

**Se mostrar PARADO:**
- O atalho não funcionou
- Vamos debugar juntos

---

### Passo 15: Testar Envio Após Reinicialização

1. Salve um arquivo Word/Excel/PDF
2. Verifique se aparece no Telegram
3. Verifique o log: `ver_log.bat`

**Esperado:**
- Arquivo aparece no Telegram
- Log mostra envio bem-sucedido

---

## 🐛 TROUBLESHOOTING - Comandos de Debug

### Ver processos Python rodando:
```cmd
tasklist | findstr python
```

### Ver últimas linhas do log:
```cmd
powershell -Command "Get-Content monitor_arquivos.log -Tail 20"
```

### Ver log em tempo real:
```cmd
powershell -Command "Get-Content monitor_arquivos.log -Wait -Tail 20"
```

### Testar manualmente com saída visível:
```cmd
python monitor_arquivos_local.py
```

### Verificar variáveis de ambiente:
```cmd
type .env
```

### Matar todos os processos Python:
```cmd
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
```

---

## 📊 Checklist de Sucesso

Marque conforme for testando:

### Fase 1 - Manual
- [ ] Python instalado e funcionando
- [ ] Dependências instaladas
- [ ] .env configurado
- [ ] Script roda manualmente (python monitor_arquivos_local.py)
- [ ] Arquivo enviado com sucesso para Telegram

### Fase 2 - Segundo Plano
- [ ] iniciar_monitor.bat funciona
- [ ] status_monitor.bat mostra RODANDO
- [ ] Arquivo enviado em segundo plano
- [ ] parar_monitor.bat funciona

### Fase 3 - Automático
- [ ] instalar_monitor_automatico.bat executou sem erros
- [ ] Atalho criado na pasta Inicializar
- [ ] Atalho funciona quando clicado
- [ ] Monitor inicia após reiniciar Windows
- [ ] Arquivo enviado após reinicialização

---

## 🆘 Se Algo Der Errado

**Me envie:**
1. Em qual passo deu erro
2. A mensagem de erro completa
3. Resultado de: `python --version`
4. Resultado de: `type .env` (sem mostrar o token completo)
5. Conteúdo do log: últimas 20 linhas

**Comandos para coletar info:**
```cmd
echo === VERSAO PYTHON === > debug.txt
python --version >> debug.txt
echo. >> debug.txt
echo === STATUS === >> debug.txt
tasklist | findstr python >> debug.txt
echo. >> debug.txt
echo === ULTIMAS LINHAS LOG === >> debug.txt
powershell -Command "Get-Content monitor_arquivos.log -Tail 20" >> debug.txt
notepad debug.txt
```

---

## ✅ Sucesso Total!

Se todos os checkboxes estiverem marcados:

🎉 **PARABÉNS!** O monitor está funcionando perfeitamente!

Agora a Ranny pode:
- Salvar arquivos normalmente
- Eles aparecem automaticamente no Telegram
- Funciona mesmo após reiniciar o PC
- Roda invisível em segundo plano

---

**Comece pelo Passo 1 e me avise em qual passo está e se deu algum erro!**
