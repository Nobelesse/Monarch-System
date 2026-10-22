$ErrorActionPreference = 'Stop'
$locations = @(
  (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
  (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
  (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe')
)
$chrome = $locations | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($chrome) {
  Start-Process -FilePath $chrome -ArgumentList 'http://127.0.0.1:5173/'
} else {
  Write-Host 'Chrome not detected in standard locations. Open http://127.0.0.1:5173/ in Google Chrome manually.'
}
