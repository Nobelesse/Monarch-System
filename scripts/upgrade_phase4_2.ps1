$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) { throw 'Missing virtual environment. Preserve your local environment.' }
if (-not (Test-Path 'backend\config.local.json')) { throw 'Missing local database configuration; do not reset it.' }
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
& $python backend/manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check failed.' }
& $python backend/manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Database migration check failed.' }
& $python backend/manage.py migrate --noinput --settings=config.admin_settings
if ($LASTEXITCODE -ne 0) { throw 'Admin database migration check failed.' }
Write-Host 'v0.4.2 code/configuration update complete. No new migrations introduced.'
Write-Host 'Run scripts\test.ps1, then start backend and frontend in separate VS Code terminals.'
