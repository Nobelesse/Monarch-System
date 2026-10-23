$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$configPath = 'backend\config.local.json'
$pgDump = 'C:\Program Files\PostgreSQL\17\bin\pg_dump.exe'
$pgRestore = 'C:\Program Files\PostgreSQL\17\bin\pg_restore.exe'
if (!(Test-Path $configPath)) { throw 'Local database config missing. Do not reconfigure a working database.' }
if (!(Test-Path $pgDump) -or !(Test-Path $pgRestore)) { throw 'PostgreSQL 17 tools missing. Verify installation location.' }
$config = Get-Content $configPath -Raw | ConvertFrom-Json
if (-not $config.database_password) { throw 'Database password missing from ignored config.local.json.' }
$target = "E:\Projects\Monarch-System-PrePhase4-$(Get-Date -Format 'yyyyMMdd-HHmmss').backup"
try {
    $env:PGPASSWORD = [string]$config.database_password
    & $pgDump -h 127.0.0.1 -p 5432 -U monarch_app -F c -f $target monarch_system
    if ($LASTEXITCODE -ne 0) { throw 'Database dump failed. Do NOT proceed to migration.' }
    & $pgRestore --list $target | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Dump archive unreadable. Do NOT proceed to migration.' }
    if ((Get-Item -LiteralPath $target).Length -le 0) { throw 'Backup is empty. Do NOT proceed.' }
    Write-Host "Verified readable PostgreSQL archive: $target"
    Write-Host 'Archive listing validation passed. A full restore drill is still recommended.'
} finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    $config = $null
}
