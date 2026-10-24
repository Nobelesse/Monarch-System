$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path 'backend\config.local.json')) { throw 'Local configuration is missing. Do not reset your database.' }
if (-not (Test-Path '.venv\Scripts\python.exe')) { throw 'Existing Python virtual environment was not found.' }
foreach ($asset in @('frontend\src\assets\abyss-world.webp','frontend\src\assets\trainer-seated.webp','frontend\src\cinematic.css','frontend\src\vite-env.d.ts')) {
  if (-not (Test-Path $asset)) { throw "Missing upgraded frontend file: $asset" }
}
& '.\.venv\Scripts\python.exe' 'backend/manage.py' 'check'
if ($LASTEXITCODE -ne 0) { throw 'Backend configuration check failed.' }
Write-Host 'Monarch v0.4.3 assets and backend checked. No database migration or new npm dependencies.'
Write-Host 'Next: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1'
