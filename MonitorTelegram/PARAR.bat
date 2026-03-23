@echo off
chcp 65001 >nul
color 0C
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ⏹️  PARANDO MONITOR DE ARQUIVOS
echo ═══════════════════════════════════════════════════════════════
echo.

:: Verificar se está rodando
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul
if %errorlevel% NEQ 0 (
    echo ℹ️  O monitor não está rodando.
    echo.
    timeout /t 2
    exit /b 0
)

echo Parando monitor...
echo.

:: Parar todos os processos pythonw.exe
taskkill /F /IM pythonw.exe >nul 2>&1

timeout /t 1 >nul

:: Verificar se parou
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul
if %errorlevel% NEQ 0 (
    echo ✅ Monitor parado com sucesso!
) else (
    echo ⚠️  Alguns processos podem ainda estar rodando.
    echo    Tente fechar pelo Gerenciador de Tarefas.
)

echo.
timeout /t 2
