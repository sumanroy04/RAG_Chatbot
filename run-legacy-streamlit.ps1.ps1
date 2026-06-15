# Run the Mental Health Chatbot (Windows PowerShell)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\streamlit.exe")) {
    Write-Host "Virtual environment not found. Install dependencies first:"
    Write-Host "  python -m venv .venv"
    Write-Host "  .\.venv\Scripts\pip.exe install -r requirements-py314.txt"
    exit 1
}

if (-not (Test-Path ".\config.json")) {
    Copy-Item ".\config.example.json" ".\config.json"
    Write-Host "Created config.json from config.example.json — add your Groq API key before chatting."
}

.\.venv\Scripts\streamlit.exe run streamlit_app.py
