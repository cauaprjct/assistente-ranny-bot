@echo off
chcp 65001 >nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🚀 INSTALADOR AUTOMÁTICO - MONITOR DE ARQUIVOS
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Este script vai fazer TUDO automaticamente:
echo.
echo   ✓ Verificar se Python está instalado
echo   ✓ Instalar bibliotecas necessárias
echo   ✓ Configurar para iniciar com o Windows
echo   ✓ Testar se está funcionando
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📋 PASSO 1/4 - Verificando Python...
echo ═══════════════════════════════════════════════════════════════
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python NÃO está instalado!
    echo.
    echo 📥 INSTALE O PYTHON PRIMEIRO:
    echo.
    echo 1. Abra o navegador
    echo 2. Acesse: https://www.python.org/downloads/
    echo 3. Clique em "Download Python"
    echo 4. Execute o instalador
    echo 5. ⚠️  IMPORTANTE: Marque "Add Python to PATH"
    echo 6. Clique em "Install Now"
    echo 7. Aguarde a instalação
    echo 8. Rode este script novamente
    echo.
    echo ═══════════════════════════════════════════════════════════════
    pause
    exit /b 1
)

python --version
echo.
echo ✅ Python está instalado!
timeout /t 2 >nul

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📦 PASSO 2/4 - Instalando bibliotecas...
echo ═══════════════════════════════════════════════════════════════
echo.
echo Isso pode demorar 1-2 minutos...
echo.

pip install python-telegram-bot python-dotenv --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo ❌ Erro ao instalar bibliotecas!
    echo.
    echo Tente manualmente:
    echo 1. Aperte Win + R
    echo 2. Digite: cmd
    echo 3. Digite: pip install python-telegram-bot python-dotenv
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Bibliotecas instaladas!
timeout /t 2 >nul

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   ⚙️  PASSO 3/4 - Configurando inicialização automática...
echo ═══════════════════════════════════════════════════════════════
echo.

python instalar_monitor_simples.py
if errorlevel 1 (
    echo.
    echo ⚠️  Houve algum problema na configuração.
    echo    Mas você pode iniciar manualmente!
    echo.
    pause
)

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🧪 PASSO 4/4 - Testando...
echo ═══════════════════════════════════════════════════════════════
echo.
echo Deseja iniciar o monitor agora para testar? (S/N)
set /p resposta="> "

if /i "%resposta%"=="S" (
    echo.
    echo 🔄 Iniciando monitor...
    python iniciar_monitor_simples.py
)

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🎉 O monitor está pronto para usar!
echo.
echo ═══════════════════════════════════════════════════════════════
echo   📋 PRÓXIMOS PASSOS:
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. ⚠️  IMPORTANTE: Abra o arquivo ".env" e coloque o token real
echo.
echo 2. 🧪 TESTE: Salve um arquivo Word no Desktop
echo.
echo 3. 📱 VERIFIQUE: O arquivo deve aparecer no Telegram em 30s
echo.
echo 4. ✅ PRONTO: Se funcionou, está tudo certo!
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🔧 COMANDOS ÚTEIS:
echo ═══════════════════════════════════════════════════════════════
echo.
echo • iniciar_monitor_simples.py  → Ligar o monitor
echo • parar_monitor_simples.py    → Desligar o monitor  
echo • status_monitor_simples.py   → Ver se está rodando
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
