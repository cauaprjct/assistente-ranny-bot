@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 INSTALADOR DO MONITOR DE ARQUIVOS AUTOMÁTICO
echo ============================================================
echo.
echo Este script vai configurar o monitor para iniciar
echo automaticamente toda vez que o Windows iniciar.
echo.
pause

REM Obter o diretório atual
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%monitor_arquivos_local.py"
set "PYTHON_PATH=python"

echo.
echo ============================================================
echo 📋 VERIFICANDO INSTALAÇÃO
echo ============================================================
echo.

REM Verificar se Python está instalado
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo Por favor, instale o Python primeiro:
    echo https://www.python.org/downloads/
    echo.
    echo Marque a opção "Add Python to PATH" durante a instalação!
    pause
    exit /b 1
)
echo ✅ Python instalado

REM Verificar se o script existe
echo.
echo [2/4] Verificando script monitor_arquivos_local.py...
if not exist "%SCRIPT_PATH%" (
    echo ❌ Script não encontrado em: %SCRIPT_PATH%
    echo.
    echo Certifique-se de que este instalador está na mesma pasta
    echo que o arquivo monitor_arquivos_local.py
    pause
    exit /b 1
)
echo ✅ Script encontrado

REM Verificar se .env existe
echo.
echo [3/4] Verificando arquivo .env...
if not exist "%SCRIPT_DIR%.env" (
    echo ⚠️ Arquivo .env não encontrado!
    echo.
    echo Criando .env de exemplo...
    copy "%SCRIPT_DIR%.env.monitor" "%SCRIPT_DIR%.env" >nul 2>&1
    echo.
    echo ⚠️ IMPORTANTE: Você precisa editar o arquivo .env
    echo    e preencher com suas informações:
    echo    - BOT_TOKEN
    echo    - CHAT_ID
    echo.
    echo Pressione qualquer tecla para abrir o .env no Bloco de Notas...
    pause >nul
    notepad "%SCRIPT_DIR%.env"
    echo.
    echo Depois de preencher o .env, execute este instalador novamente.
    pause
    exit /b 1
)
echo ✅ Arquivo .env encontrado

REM Instalar dependências
echo.
echo [4/4] Instalando dependências Python...
echo (Isso pode demorar alguns minutos...)
echo.
pip install watchdog python-telegram-bot python-dotenv >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Erro ao instalar dependências
    echo Tentando novamente com saída visível...
    pip install watchdog python-telegram-bot python-dotenv
    pause
)
echo ✅ Dependências instaladas

echo.
echo ============================================================
echo 📁 CRIANDO ATALHO NA PASTA INICIALIZAR
echo ============================================================
echo.

REM Criar script VBS para criar atalho
set "VBS_PATH=%TEMP%\criar_atalho.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\Monitor de Arquivos.lnk"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_PATH%"
echo sLinkFile = "%SHORTCUT_PATH%" >> "%VBS_PATH%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_PATH%"
echo oLink.TargetPath = "pythonw.exe" >> "%VBS_PATH%"
echo oLink.Arguments = """%SCRIPT_PATH%""" >> "%VBS_PATH%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBS_PATH%"
echo oLink.Description = "Monitor de Arquivos - Envia automaticamente para Telegram" >> "%VBS_PATH%"
echo oLink.IconLocation = "shell32.dll,4" >> "%VBS_PATH%"
echo oLink.Save >> "%VBS_PATH%"

REM Executar VBS
cscript //nologo "%VBS_PATH%"
del "%VBS_PATH%"

if exist "%SHORTCUT_PATH%" (
    echo ✅ Atalho criado com sucesso!
    echo    Local: %STARTUP_FOLDER%
) else (
    echo ❌ Erro ao criar atalho
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ============================================================
echo.
echo O monitor de arquivos agora vai iniciar automaticamente
echo toda vez que o Windows iniciar.
echo.
echo 📋 O que acontece agora:
echo    1. O script roda em segundo plano (invisível)
echo    2. Monitora as pastas configuradas
echo    3. Envia arquivos automaticamente pro Telegram
echo.
echo 🔧 Para gerenciar:
echo    - Iniciar agora: execute iniciar_monitor.bat
echo    - Parar: execute parar_monitor.bat
echo    - Ver logs: abra monitor_arquivos.log
echo    - Remover: execute desinstalar_monitor.bat
echo.
echo 💡 Deseja iniciar o monitor agora? (s/n)
set /p INICIAR="👉 "

if /i "%INICIAR%"=="s" (
    echo.
    echo 🚀 Iniciando monitor...
    start "" pythonw.exe "%SCRIPT_PATH%"
    timeout /t 3 >nul
    echo ✅ Monitor iniciado em segundo plano!
    echo.
    echo Teste salvando um arquivo Word/Excel/PDF nas pastas monitoradas.
    echo O arquivo deve aparecer no Telegram automaticamente.
)

echo.
echo Pressione qualquer tecla para fechar...
pause >nul
