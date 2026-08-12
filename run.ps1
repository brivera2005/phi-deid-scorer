$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv\Scripts\python.exe")) {
  python -m venv .venv
  .\.venv\Scripts\pip install -r requirements.txt
}
Write-Host "PHI De-ID + Re-ID Risk Scorer → http://127.0.0.1:8093" -ForegroundColor Green
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8093 --reload
