# deploy_mods.ps1 - Automated C&C Accessibility Mod Deployment
# Dynamically resolves Documents directory (including OneDrive redirections)

$ErrorActionPreference = "Stop"

$docsPath = [Environment]::GetFolderPath("MyDocuments")
Write-Host "Resolved Documents folder: $docsPath" -ForegroundColor Cyan

$cncSourceDir = "F:\SteamLibrary\steamapps\common\CnCRemastered\SOURCECODE"
$openRaDir = "C:\Users\vegas\OneDrive\Desktop\Games\OpenRA-RA2"
$repoDir = $PSScriptRoot

# 1. Deploy Red Alert 1 Remastered Mod
$raTargetData = Join-Path $docsPath "CnCRemastered\Mods\Red_Alert\AccessMod\Data"
$raModDir = Join-Path $docsPath "CnCRemastered\Mods\Red_Alert\AccessMod"
New-Item -ItemType Directory -Path $raTargetData -Force | Out-Null

$raJson = @'
{
  "name": "AccessMod",
  "description": "Screen reader accessibility layer for Red Alert Remastered",
  "author": "Orlando Johnson",
  "load_order": 1,
  "version_low": 0,
  "version_high": 999999999,
  "game_type": "RA"
}
'@
Set-Content -Path (Join-Path $raModDir "ccmod.json") -Value $raJson -Force

$raDll = Join-Path $cncSourceDir "bin\Win32\RedAlert.dll"
if (Test-Path $raDll) {
    Copy-Item -Path $raDll -Destination (Join-Path $raTargetData "RedAlert.dll") -Force
    Write-Host "Deployed RedAlert.dll to $raTargetData" -ForegroundColor Green
}

$raTolkDir = Join-Path $cncSourceDir "REDALERT\AccessMod\ThirdParty\Tolk"
if (Test-Path $raTolkDir) {
    Copy-Item -Path "$raTolkDir\*" -Destination "$raTargetData\" -Force
    Write-Host "Deployed RA1 Tolk dependencies to $raTargetData" -ForegroundColor Green
}

# 2. Deploy Tiberian Dawn Remastered Mod
$tdTargetData = Join-Path $docsPath "CnCRemastered\Mods\Tiberian_Dawn\AccessMod\Data"
$tdModDir = Join-Path $docsPath "CnCRemastered\Mods\Tiberian_Dawn\AccessMod"
New-Item -ItemType Directory -Path $tdTargetData -Force | Out-Null

$tdJson = @'
{
  "name": "AccessMod",
  "description": "Screen reader accessibility layer for Tiberian Dawn Remastered",
  "author": "Orlando Johnson",
  "load_order": 1,
  "version_low": 0,
  "version_high": 999999999,
  "game_type": "TD"
}
'@
Set-Content -Path (Join-Path $tdModDir "ccmod.json") -Value $tdJson -Force

$tdDll = Join-Path $cncSourceDir "bin\Win32\TiberianDawn.dll"
if (Test-Path $tdDll) {
    Copy-Item -Path $tdDll -Destination (Join-Path $tdTargetData "TiberianDawn.dll") -Force
    Write-Host "Deployed TiberianDawn.dll to $tdTargetData" -ForegroundColor Green
}

$tdTolkDir = Join-Path $cncSourceDir "TIBERIANDAWN\AccessMod\ThirdParty\Tolk"
if (Test-Path $tdTolkDir) {
    Copy-Item -Path "$tdTolkDir\*" -Destination "$tdTargetData\" -Force
    Write-Host "Deployed Tiberian Dawn Tolk dependencies to $tdTargetData" -ForegroundColor Green
}

# 3. Deploy OpenRA-RA2 Native Dependencies
$openRaBin = Join-Path $openRaDir "engine\bin"
if (Test-Path $openRaBin) {
    $nvdaClientDll = Join-Path $repoDir "vendor\NVDAControllerClient\x64\nvdaControllerClient.dll"
    if (Test-Path $nvdaClientDll) {
        Copy-Item -Path $nvdaClientDll -Destination (Join-Path $openRaBin "nvdaControllerClient.dll") -Force
        Copy-Item -Path $nvdaClientDll -Destination (Join-Path $openRaBin "nvdaControllerClient64.dll") -Force
        Write-Host "Deployed nvdaControllerClient (x64) to $openRaBin" -ForegroundColor Green
    }
}

Write-Host "All accessibility mod deployments completed successfully!" -ForegroundColor Cyan
