@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ▶️  INICIANDO MONITOR DE ARQUIVOS
echo ═══════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

:: Verificar se já está rodando
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul
if %errorlevel%==0 (
    echo ⚠️  O monitor já está rodando!
    echo.
    echo Para parar, execute: PARAR.bat
    echo.
    timeout /t 3
    exit /b 0
)

echo Iniciando monitor em segundo plano (invisível)...
echo.

:: Tentar iniciar com pythonw
start /B pythonw.exe monitor_simples.py >nul 2>&1

if %errorlevel% NEQ 0 (
    echo ⚠️  pythonw não encontrado, tentando com python...
    start /B python.exe monitor_simples.py >nul 2>&1
)

timeout /t 2 >nul

:: Verificar se iniciou
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul
if %errorlevel%==0 (
    echo ✅ Monitor iniciado com sucesso!
    echo.
    echo 📋 O monitor está rodando em segundo plano.
    echo    Ele vai enviar arquivos automaticamente para o Telegram.
    echo.
    echo 🔧 Para parar: execute PARAR.bat
    echo 📊 Para ver status: execute STATUS.bat
) else (
    echo ❌ Erro ao iniciar o monitor!
    echo.
    echo Tente executar manualmente:
    echo    python monitor_simples.py
    echo.
    echo E veja o erro no arquivo: monitor_simples.log
)

echo.
timeout /t 3
