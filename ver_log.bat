@echo off
chcp 65001 >nul
echo ============================================================
echo 📋 VISUALIZADOR DE LOG DO MONITOR
echo ============================================================
echo.

if not exist "monitor_arquivos.log" (
    echo ❌ Arquivo de log não encontrado.
    echo.
    echo O log será criado quando o monitor for iniciado pela primeira vez.
    echo Execute: iniciar_monitor.bat
    echo.
    pause
    exit /b 1
)

echo Abrindo log no Bloco de Notas...
notepad monitor_arquivos.log

echo.
echo 💡 Dica: Para ver o log em tempo real, use:
echo    PowerShell: Get-Content monitor_arquivos.log -Wait -Tail 20
echo.
pause
