$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python 3.12 environment.' }
}
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
& $python scripts/check_versions.py
if ($LASTEXITCODE -ne 0) { throw 'Version check failed.' }
& $python -m pip install -r backend/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
& $python -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Python dependency conflict.' }
& $python scripts/configure.py
if ($LASTEXITCODE -ne 0) { throw 'Configuration failed.' }
& $python backend/manage.py check --database default
if ($LASTEXITCODE -ne 0) { throw 'Django checks failed.' }
& $python backend/manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed. Check PostgreSQL service and credentials.' }
& $python backend/manage.py migrate --noinput --settings=config.admin_settings
if ($LASTEXITCODE -ne 0) { throw 'Separate admin schema migrations failed.' }
Push-Location frontend
try {
    npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend install failed.' }
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} finally { Pop-Location }
Write-Host 'Setup complete. Use scripts/backend.ps1 and scripts/frontend.ps1 in separate terminals.'
