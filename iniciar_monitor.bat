@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 INICIANDO MONITOR DE ARQUIVOS
echo ============================================================
echo.

REM Obter o diretório atual
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%monitor_arquivos_local.py"

REM Verificar se já está rodando
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "pythonw.exe" >NUL
if not errorlevel 1 (
    echo ⚠️ O monitor já está rodando!
    echo.
    echo Para parar, execute: parar_monitor.bat
    echo Para ver logs, abra: monitor_arquivos.log
    echo.
    pause
    exit /b 0
)

REM Verificar se o script existe
if not exist "%SCRIPT_PATH%" (
    echo ❌ Script não encontrado: %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Iniciar o monitor em segundo plano (invisível)
echo 🔄 Iniciando monitor em segundo plano...
start "" pythonw.exe "%SCRIPT_PATH%"

REM Aguardar um pouco
timeout /t 2 >nul

REM Verificar se iniciou
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "pythonw.exe" >NUL
if not errorlevel 1 (
    echo ✅ Monitor iniciado com sucesso!
    echo.
    echo 📋 O monitor está rodando em segundo plano.
    echo    Ele vai enviar automaticamente arquivos para o Telegram.
    echo.
    echo 🔧 Comandos úteis:
    echo    - Parar: parar_monitor.bat
    echo    - Ver logs: monitor_arquivos.log
    echo    - Status: status_monitor.bat
) else (
    echo ❌ Erro ao iniciar o monitor
    echo.
    echo Tente executar manualmente para ver o erro:
    echo python "%SCRIPT_PATH%"
)

echo.
pause
