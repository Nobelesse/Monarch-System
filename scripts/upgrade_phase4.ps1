$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (!(Test-Path '.venv\Scripts\python.exe')) { throw 'Python virtual environment missing; restore it or use scripts/setup.ps1.' }
if (!(Test-Path 'backend\config.local.json')) { throw 'Your existing local configuration is missing. Stop; do not overwrite it.' }
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
& $python backend/manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check failed; no migration attempted.' }
& $python backend/manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL migration failed. Do not reset your data.' }
& $python backend/manage.py migrate --noinput --settings=config.admin_settings
if ($LASTEXITCODE -ne 0) { throw 'Local admin migration check failed.' }
& $python backend/manage.py shell -c "from core.models import WorkoutExercise; assert WorkoutExercise.objects.count() >= 25"
if ($LASTEXITCODE -ne 0) { throw 'Workout library verification failed.' }
Write-Host 'Workout exercise catalog seed verified.'
Write-Host 'Phase 4 migrations applied. Now run scripts/test.ps1.'
