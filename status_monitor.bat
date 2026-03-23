@echo off
chcp 65001 >nul
echo ============================================================
echo 📊 STATUS DO MONITOR DE ARQUIVOS
echo ============================================================
echo.

REM Verificar se está rodando
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "pythonw.exe" >NUL
if not errorlevel 1 (
    echo ✅ STATUS: RODANDO
    echo.
    echo 📋 Processos Python em segundo plano:
    tasklist /FI "IMAGENAME eq pythonw.exe" /FO TABLE
) else (
    echo ⚠️ STATUS: PARADO
    echo.
    echo O monitor não está rodando.
    echo Para iniciar, execute: iniciar_monitor.bat
)

echo.
echo ============================================================
echo 📁 ÚLTIMAS LINHAS DO LOG
echo ============================================================
echo.

REM Mostrar últimas 15 linhas do log
if exist "monitor_arquivos.log" (
    powershell -Command "Get-Content monitor_arquivos.log -Tail 15"
) else (
    echo ℹ️ Arquivo de log não encontrado.
    echo O log será criado quando o monitor for iniciado.
)

echo.
echo ============================================================
echo 🔧 COMANDOS DISPONÍVEIS
echo ============================================================
echo.
echo - iniciar_monitor.bat      : Inicia o monitor
echo - parar_monitor.bat        : Para o monitor
echo - status_monitor.bat       : Mostra este status
echo - ver_log.bat              : Abre o log completo
echo - desinstalar_monitor.bat  : Remove da inicialização
echo.
pause
