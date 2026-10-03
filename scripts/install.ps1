$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
function Assert-Success { if ($LASTEXITCODE -ne 0) { throw "El comando anterior falló ($LASTEXITCODE)" } }
py -3.12 -m venv backend/.venv
Assert-Success
& backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
Assert-Success
& backend/.venv/Scripts/python.exe backend/manage.py migrate --noinput
Assert-Success
& backend/.venv/Scripts/python.exe backend/manage.py seed_history
Assert-Success
Push-Location frontend
try {
    npm.cmd ci --no-audit --no-fund
    Assert-Success
    npm.cmd run build
    Assert-Success
} finally { Pop-Location }
