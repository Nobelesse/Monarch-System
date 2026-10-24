$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$previous = $env:MONARCH_TEST_MODE
try {
    $env:MONARCH_TEST_MODE = '1'
    & .\.venv\Scripts\python.exe scripts/verify_offline_demos.py
    if ($LASTEXITCODE -ne 0) { throw 'Offline exercise animation coverage validation failed.' }
    node scripts/verify_offline_renderer.cjs
    if ($LASTEXITCODE -ne 0) { throw 'Offline 3D human renderer smoke test failed.' }
    & .\.venv\Scripts\python.exe backend/manage.py check
    if ($LASTEXITCODE -ne 0) { throw 'Django public system check failed.' }
    & .\.venv\Scripts\python.exe backend/manage.py check --settings=config.admin_settings
    if ($LASTEXITCODE -ne 0) { throw 'Django admin system check failed.' }
    & .\.venv\Scripts\python.exe backend/manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'Uncommitted model/migration changes.' }
    & .\.venv\Scripts\python.exe backend/manage.py test core
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally { $env:MONARCH_TEST_MODE = $previous }
Push-Location frontend
try {
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} finally { Pop-Location }
