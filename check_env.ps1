# Quick check: which Python is used and whether PyQt6 is available.
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "=== Project venv ===" -ForegroundColor Cyan
if (Test-Path $venvPython) {
    & $venvPython -c "import sys; print('executable:', sys.executable); import PyQt6; print('PyQt6: OK')"
} else {
    Write-Host "ERROR: .venv not found. Run: py -3.12 -m venv .venv" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Command 'python' in this terminal ===" -ForegroundColor Cyan
python -c "import sys; print('executable:', sys.executable)" 2>&1
