$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
Write-Host 'Admin is restricted to this PC: http://127.0.0.1:8001/admin/'
& .\.venv\Scripts\python.exe backend/manage.py runserver --insecure 127.0.0.1:8001 --settings=config.admin_settings
