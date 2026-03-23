@echo off
chcp 65001 >nul
color 0B
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo   📊 STATUS DO MONITOR DE ARQUIVOS
echo ═══════════════════════════════════════════════════════════════
echo.

:: Verificar se está rodando
tasklist /FI "IMAGENAME eq pythonw.exe" | find /I "pythonw.exe" >nul
if %errorlevel%==0 (
    echo ✅ Monitor está RODANDO
    echo.
    echo 📋 O monitor está ativo e monitorando:
    echo    • Desktop (Área de Trabalho)
    echo    • Documentos (Documents)
    echo.
    echo 📱 Arquivos .docx, .xlsx, .pdf modificados nas últimas 24h
    echo    serão enviados automaticamente para o Telegram.
    echo.
    echo 🔧 Para parar: execute PARAR.bat
) else (
    echo ❌ Monitor está PARADO
    echo.
    echo 🔧 Para iniciar: execute INICIAR.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   📝 ÚLTIMAS LINHAS DO LOG:
echo ═══════════════════════════════════════════════════════════════
echo.

if exist "%~dp0monitor_simples.log" (
    powershell -Command "Get-Content '%~dp0monitor_simples.log' -Tail 10 -Encoding UTF8"
) else (
    echo (Arquivo de log não encontrado)
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
