$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$previous = $env:MONARCH_TEST_MODE
try {
    $env:MONARCH_TEST_MODE = '1'
    & .\.venv\Scripts\python.exe backend/manage.py test core
    if ($LASTEXITCODE -ne 0) { throw 'Backend tests failed.' }
} finally { $env:MONARCH_TEST_MODE = $previous }
Push-Location frontend
try {
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} finally { Pop-Location }
