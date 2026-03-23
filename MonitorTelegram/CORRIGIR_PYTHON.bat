@echo off
chcp 65001 >nul
color 0E
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🔧 CORRETOR DE PYTHON - Encontra e configura automaticamente
echo ═══════════════════════════════════════════════════════════════
echo.
echo Procurando Python instalado no seu PC...
echo.

:: Procurar Python em locais comuns
set PYTHON_FOUND=0

:: Local 1: AppData Local
if exist "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_PATH=%%i"
            set PYTHON_FOUND=1
            goto :found
        )
    )
)

:: Local 2: Program Files
if exist "C:\Program Files\Python*\python.exe" (
    for /d %%i in ("C:\Program Files\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_PATH=%%i"
            set PYTHON_FOUND=1
            goto :found
        )
    )
)

:: Local 3: Program Files (x86)
if exist "C:\Program Files (x86)\Python*\python.exe" (
    for /d %%i in ("C:\Program Files (x86)\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_PATH=%%i"
            set PYTHON_FOUND=1
            goto :found
        )
    )
)

:: Local 4: C:\Python
if exist "C:\Python*\python.exe" (
    for /d %%i in ("C:\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_PATH=%%i"
            set PYTHON_FOUND=1
            goto :found
        )
    )
)

:found
if %PYTHON_FOUND%==0 (
    echo ❌ Python não encontrado!
    echo.
    echo O Python não está instalado OU está em um local diferente.
    echo.
    echo 📥 REINSTALE O PYTHON:
    echo.
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe e execute o instalador
    echo 3. ⚠️  MARQUE "Add Python to PATH"
    echo 4. Clique em "Install Now"
    echo 5. Rode este script novamente
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado em:
echo    %PYTHON_PATH%
echo.

:: Testar se funciona
"%PYTHON_PATH%\python.exe" --version
if errorlevel 1 (
    echo ❌ Erro ao executar Python!
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   📦 Instalando bibliotecas...
echo ═══════════════════════════════════════════════════════════════
echo.

"%PYTHON_PATH%\python.exe" -m pip install python-telegram-bot python-dotenv --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo ⚠️  Erro ao instalar bibliotecas.
    echo    Tentando sem o --quiet...
    echo.
    "%PYTHON_PATH%\python.exe" -m pip install python-telegram-bot python-dotenv
)

echo.
echo ✅ Bibliotecas instaladas!
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ⚙️  Configurando inicialização automática...
echo ═══════════════════════════════════════════════════════════════
echo.

"%PYTHON_PATH%\python.exe" instalar_monitor_simples.py

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✅ CONFIGURAÇÃO CONCLUÍDA!
echo ═══════════════════════════════════════════════════════════════
echo.
echo Deseja iniciar o monitor agora? (S/N)
set /p resposta="> "

if /i "%resposta%"=="S" (
    echo.
    echo 🔄 Iniciando monitor...
    "%PYTHON_PATH%\python.exe" iniciar_monitor_simples.py
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   📋 PRÓXIMOS PASSOS:
echo ═══════════════════════════════════════════════════════════════
echo.
echo 1. Edite o arquivo .env e coloque o token real
echo 2. Salve um arquivo Word no Desktop para testar
echo 3. Veja se aparece no Telegram em 30 segundos
echo.
pause
