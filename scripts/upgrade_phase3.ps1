$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    throw 'Existing virtual environment not found. Use scripts/setup.ps1 for first-time installation.'
}
if (-not (Test-Path 'backend\config.local.json')) {
    throw 'Local configuration not found. Do not overwrite it; check your Phase 2 installation.'
}
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
& $python backend/manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check failed.' }
& $python backend/manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL migration failed. Do not delete your database.' }
& $python backend/manage.py migrate --noinput --settings=config.admin_settings
if ($LASTEXITCODE -ne 0) { throw 'Admin migration check failed.' }
Write-Host 'Phase 3 migrations applied. Next run scripts/test.ps1 (backend tests + frontend build).'
