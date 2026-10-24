$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
& .\.venv\Scripts\python.exe scripts/verify_offline_demos.py
if ($LASTEXITCODE -ne 0) { throw 'Offline movement mapping failed.' }
& .\.venv\Scripts\python.exe backend/manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django configuration check failed.' }
& .\.venv\Scripts\python.exe backend/manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Django migration check failed.' }
Write-Host 'v0.4.6 installed. No new migration or external video service. Run scripts/test.ps1.'
