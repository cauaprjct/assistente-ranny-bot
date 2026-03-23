@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo   📦 INSTALADOR AUTOMÁTICO - MONITOR DE ARQUIVOS
echo ═══════════════════════════════════════════════════════════════
echo.
echo Este script vai instalar tudo automaticamente!
echo.
pause
echo.

echo ═══════════════════════════════════════════════════════════════
echo   1/3 - Verificando Python...
echo ═══════════════════════════════════════════════════════════════
python --version
if errorlevel 1 (
    echo.
    echo ❌ Python não encontrado!
    echo.
    echo Por favor, instale o Python primeiro:
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe a versão mais recente
    echo 3. MARQUE "Add Python to PATH" na instalação
    echo 4. Rode este script novamente
    echo.
    pause
    exit
)
echo ✅ Python instalado!
echo.

echo ═══════════════════════════════════════════════════════════════
echo   2/3 - Instalando bibliotecas...
echo ═══════════════════════════════════════════════════════════════
pip install python-telegram-bot python-dotenv
if errorlevel 1 (
    echo.
    echo ❌ Erro ao instalar bibliotecas!
    echo.
    pause
    exit
)
echo ✅ Bibliotecas instaladas!
echo.

echo ═══════════════════════════════════════════════════════════════
echo   3/3 - Configurando inicialização automática...
echo ═══════════════════════════════════════════════════════════════
python instalar_monitor_simples.py
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ✅ INSTALAÇÃO CONCLUÍDA!
echo ═══════════════════════════════════════════════════════════════
echo.
echo O monitor está pronto para usar!
echo.
echo Próximos passos:
echo 1. Verifique se o arquivo .env está com o token correto
echo 2. Teste salvando um arquivo Word no Desktop
echo 3. Veja se aparece no Telegram em até 30 segundos
echo.
pause
