@echo off
chcp 65001 >nul
echo ============================================================
echo 🗑️  DESINSTALAR MONITOR DE ARQUIVOS
echo ============================================================
echo.
echo Este script vai remover o monitor da inicialização automática.
echo O script não será deletado, apenas não iniciará mais automaticamente.
echo.
pause

REM Parar o monitor se estiver rodando
echo 🔄 Parando monitor...
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 1 >nul

REM Remover atalho da pasta Inicializar
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\Monitor de Arquivos.lnk"

if exist "%SHORTCUT_PATH%" (
    echo 🗑️  Removendo atalho da inicialização...
    del "%SHORTCUT_PATH%"
    echo ✅ Atalho removido!
) else (
    echo ℹ️ Atalho não encontrado na pasta Inicializar
)

echo.
echo ============================================================
echo ✅ DESINSTALAÇÃO CONCLUÍDA
echo ============================================================
echo.
echo O monitor não vai mais iniciar automaticamente com o Windows.
echo.
echo Para iniciar manualmente: iniciar_monitor.bat
echo Para reinstalar: instalar_monitor_automatico.bat
echo.
pause
