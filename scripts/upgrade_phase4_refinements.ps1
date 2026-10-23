$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (!(Test-Path '.venv\Scripts\python.exe')) { throw 'Virtual environment missing. Do not reset existing data.' }
if (!(Test-Path 'backend\config.local.json')) { throw 'Local database configuration missing. Stop.' }
$python = (Resolve-Path '.venv\Scripts\python.exe').Path
& $python backend/manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django system check failed.' }
& $python backend/manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed; do not reset data.' }
& $python backend/manage.py migrate --noinput --settings=config.admin_settings
if ($LASTEXITCODE -ne 0) { throw 'Admin migrations failed.' }
& $python backend/manage.py shell -c 'from core.models import WorkoutExercise; assert WorkoutExercise.objects.filter(active=True).count() >= 60'
if ($LASTEXITCODE -ne 0) { throw 'Workout catalog validation failed.' }
Write-Host 'Phase 4 refinement migration and expanded exercise library verified.'
Write-Host 'Next: run scripts\test.ps1.'
