<# Add a real exercise-specific demo (video or motion-captured 3D GLB) to the local Vite assets.
   Requires rights to distribute the file; excludes guessed exercise-to-animation mappings. #>
param(
 [Parameter(Mandatory=$true)][string]$Slug,
 [Parameter(Mandatory=$true)][string]$File,
 [string]$Credit='Provided by project owner',
 [switch]$IHaveRights
)
$ErrorActionPreference='Stop'
if (-not $IHaveRights) {throw 'Include -IHaveRights only when you own or have permission to distribute this footage/model.'}
if ($Slug -cnotmatch '^[a-z0-9]+(-[a-z0-9]+)*$') {throw 'Exercise slug must contain lowercase letters, digits and hyphens.'}
$ext=[IO.Path]::GetExtension($File).ToLowerInvariant()
if ($ext -notin @('.mp4','.webm','.glb')) {throw 'Only .mp4, .webm or animated .glb files are supported.'}
$source=Get-Item -LiteralPath $File -ErrorAction Stop
if ($source.Length -gt 200MB -or $source.Length -lt 1024) {throw 'Media file must be at least 1 KB and no larger than 200 MB.'}
$root=Split-Path -Parent $PSScriptRoot
$manifestPath=Join-Path $root 'frontend\public\human-demos\manifest.json'
$destination=Join-Path $root 'frontend\public\human-demos\media'
$catalogText=Get-Content (Join-Path $root 'backend\core\workout_catalog.py') -Raw
if ($catalogText -notmatch [regex]::Escape($Slug.Replace('-',' ')) -and $catalogText -notmatch [regex]::Escape($Slug)) {
  Write-Warning 'Confirm this exact slug exists in the Workout exercise library. Unknown slugs will not be shown.'
}
New-Item -ItemType Directory -Force -Path $destination | Out-Null
$name="$Slug$ext"
$existing=Join-Path $destination $name
if (Test-Path $existing) {throw 'This destination file already exists. Rename or remove it manually after reviewing.'}
Copy-Item -LiteralPath $source.FullName -Destination $existing
$manifest=Get-Content $manifestPath -Raw | ConvertFrom-Json
$existingEntries=@($manifest.demos | Where-Object {$_.slug -ne $Slug})
$newEntry=[PSCustomObject]@{slug=$Slug;filename=$name;kind=$(if($ext -eq '.glb'){'3d'}else{'video'});credit=$Credit;checked=$false}
$manifest=[PSCustomObject]@{version=1;demos=@($existingEntries)+@($newEntry)}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding utf8
Write-Host "Added $name. Reload the Workout page. Confirm the motion truly matches $Slug before relying on it."
Write-Host 'For .glb previews, the optional model-viewer loader currently requires an internet connection.'
