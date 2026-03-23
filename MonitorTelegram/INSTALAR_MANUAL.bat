@echo off
chcp 65001 >nul
color 0B
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo   📝 INSTALAÇÃO MANUAL - Passo a Passo
echo ═══════════════════════════════════════════════════════════════
echo.
echo Se o instalador automático não funcionou, siga estes passos:
echo.
echo ═══════════════════════════════════════════════════════════════
echo   PASSO 1: Abrir Prompt de Comando
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. Aperte as teclas: Win + R
echo 2. Digite: cmd
echo 3. Aperte Enter
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════════
echo   PASSO 2: Testar se Python está instalado
echo ═══════════════════════════════════════════════════════════════
echo.
echo No Prompt de Comando que abriu, digite:
echo.
echo    python --version
echo.
echo E aperte Enter.
echo.
echo O que apareceu?
echo.
echo A) Python 3.x.x (algum número)
echo B) Erro ou "não é reconhecido"
echo.
set /p resposta="Digite A ou B: "

if /i "%resposta%"=="B" (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ❌ Python não está no PATH
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo SOLUÇÃO: Reinstalar o Python
    echo.
    echo 1. Desinstale o Python atual:
    echo    - Painel de Controle ^> Programas ^> Desinstalar
    echo    - Procure "Python" e desinstale
    echo.
    echo 2. Baixe novamente:
    echo    - Acesse: https://www.python.org/downloads/
    echo    - Clique em "Download Python"
    echo.
    echo 3. Na instalação:
    echo    - ⚠️  MARQUE "Add Python to PATH" (caixinha embaixo)
    echo    - Clique em "Install Now"
    echo.
    echo 4. Rode este script novamente
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   PASSO 3: Instalar bibliotecas
echo ═══════════════════════════════════════════════════════════════
echo.
echo No mesmo Prompt de Comando, digite:
echo.
echo    pip install python-telegram-bot python-dotenv
echo.
echo E aperte Enter.
echo.
echo Aguarde instalar (pode demorar 1-2 minutos).
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════════
echo   PASSO 4: Configurar inicialização automática
echo ═══════════════════════════════════════════════════════════════
echo.
echo No mesmo Prompt de Comando, digite:
echo.
echo    cd "%~dp0"
echo    python instalar_monitor_simples.py
echo.
echo E aperte Enter.
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════════
echo   PASSO 5: Testar
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. Edite o arquivo .env e coloque o token real
echo 2. Clique duas vezes em: iniciar_monitor_simples.py
echo 3. Salve um arquivo Word no Desktop
echo 4. Veja se aparece no Telegram em 30 segundos
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
