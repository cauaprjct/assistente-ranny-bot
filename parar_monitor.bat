@echo off
chcp 65001 >nul
echo ============================================================
echo ⏹️  PARANDO MONITOR DE ARQUIVOS
echo ============================================================
echo.

REM Verificar se está rodando
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "pythonw.exe" >NUL
if errorlevel 1 (
    echo ℹ️ O monitor não está rodando.
    echo.
    pause
    exit /b 0
)

echo 🔄 Parando monitor...

REM Parar todos os processos pythonw.exe
taskkill /F /IM pythonw.exe >nul 2>&1

REM Aguardar um pouco
timeout /t 1 >nul

REM Verificar se parou
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "pythonw.exe" >NUL
if errorlevel 1 (
    echo ✅ Monitor parado com sucesso!
) else (
    echo ⚠️ Alguns processos podem ainda estar rodando
    echo    Tente fechar manualmente pelo Gerenciador de Tarefas
)

echo.
pause
