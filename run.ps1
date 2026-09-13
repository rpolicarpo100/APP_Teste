Write-Host ""
Write-Host " ========================================" -ForegroundColor Magenta
Write-Host "  AI BRAIN - Leve e Bonita v1.0" -ForegroundColor White
Write-Host "  GOD Cerebro Core" -ForegroundColor Gray
Write-Host " ========================================" -ForegroundColor Magenta
Write-Host ""

# Verifica Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "✅ $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python não encontrado. Instala de https://python.org" -ForegroundColor Red
    Read-Host "Pressiona Enter"
    exit 1
}

# Cria venv
if (-not (Test-Path ".venv")) {
    Write-Host "[1/4] Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "[2/4] Ativando ambiente..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "[3/4] Instalando dependências leves..." -ForegroundColor Yellow
pip install -q -r requirements.txt

Write-Host "[4/4] Iniciando AI Brain..." -ForegroundColor Yellow
Write-Host ""
Write-Host " Dashboard vai abrir em: http://127.0.0.1:8000/dashboard" -ForegroundColor Cyan
Write-Host " Deixa esta janela aberta. Ctrl+C para parar." -ForegroundColor Gray
Write-Host ""

python run_app.py
