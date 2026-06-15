# run.ps1 — Start Patronus AI (FastAPI backend + React/Vite frontend)
# Usage: .\run.ps1

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackendDir  = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

# Find Python virtual environment (root or backend)
$VenvDir = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path (Join-Path $VenvDir "Scripts\python.exe"))) {
    $VenvDir = Join-Path $BackendDir ".venv"
}

$VenvPython  = Join-Path $VenvDir "Scripts\python.exe"
$VenvUvicorn = Join-Path $VenvDir "Scripts\uvicorn.exe"

# ─── Pre-flight checks ──────────────────────────────────────────────────────
if (-not (Test-Path $VenvPython)) {
    Write-Host "❌  Python venv not found at root .venv or backend\.venv" -ForegroundColor Red
    Write-Host "    Create it with:" -ForegroundColor Yellow
    Write-Host "      python -m venv .venv" -ForegroundColor Yellow
    Write-Host "      .\.venv\Scripts\pip install -r requirements/dev.txt" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Host "📦  Installing frontend dependencies..." -ForegroundColor Cyan
    Push-Location $FrontendDir
    npm install
    Pop-Location
}

# Copy root .env key into backend folder if a backend .env doesn't already have it
$RootEnv    = Join-Path $ProjectRoot ".env"
$BackendEnv = Join-Path $BackendDir ".env"
if ((Test-Path $RootEnv) -and (-not (Test-Path $BackendEnv))) {
    Copy-Item $RootEnv $BackendEnv
    Write-Host "ℹ️   Copied root .env to backend\.env" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "🚀  Starting Patronus AI" -ForegroundColor Green
Write-Host "    Backend  → http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "    Frontend → http://localhost:5173" -ForegroundColor Cyan
Write-Host "    Press Ctrl+C in each window to stop." -ForegroundColor DarkGray
Write-Host ""

# ─── Launch backend in a new terminal window ─────────────────────────────────
$backendCmd = "Set-Location '$BackendDir'; & '$VenvUvicorn' main:app --reload --host 127.0.0.1 --port 8000; Read-Host 'Press Enter to close'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Start-Sleep -Seconds 2   # Give uvicorn a moment to bind the port

# ─── Launch frontend in a new terminal window ────────────────────────────────
$frontendCmd = "Set-Location '$FrontendDir'; npm run dev; Read-Host 'Press Enter to close'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-Host "✅  Both servers are starting in separate windows." -ForegroundColor Green
Write-Host "    Open http://localhost:5173 in your browser." -ForegroundColor Cyan

