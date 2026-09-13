@echo off
echo.
echo  ========================================
echo   AI BRAIN - Leve e Bonita v1.0
echo   GOD Cerebro Core
echo  ========================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instala Python 3.11+ de https://python.org
    pause
    exit /b 1
)

REM Cria venv se nao existir
if not exist ".venv" (
    echo [1/4] Criando ambiente virtual...
    python -m venv .venv
)

echo [2/4] Ativando ambiente...
call .venv\Scripts\activate.bat

echo [3/4] Instalando dependencias leves...
pip install -q -r requirements.txt

echo [4/4] Iniciando AI Brain...
echo.
echo  Dashboard vai abrir automaticamente em:
echo  http://127.0.0.1:8000/dashboard
echo.
echo  Deixa esta janela aberta. Ctrl+C para parar.
echo.

python run_app.py

pause
