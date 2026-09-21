# create_desktop_shortcuts.ps1 - Creates 1-click accessible desktop launchers
$ErrorActionPreference = "Stop"

$desktop = [Environment]::GetFolderPath("Desktop")
Write-Host "Creating shortcuts on Desktop: $desktop" -ForegroundColor Cyan

$wsh = New-Object -ComObject WScript.Shell

# 1. Shortcut: Play Accessible Red Alert 2 (OpenRA)
$ra2Path = "C:\Users\vegas\OneDrive\Desktop\Games\OpenRA-RA2\PLAY Red Alert 2.cmd"
$ra2WorkingDir = "C:\Users\vegas\OneDrive\Desktop\Games\OpenRA-RA2"
$ra2Shortcut = $wsh.CreateShortcut("$desktop\Play Accessible Red Alert 2 (OpenRA).lnk")
$ra2Shortcut.TargetPath = $ra2Path
$ra2Shortcut.WorkingDirectory = $ra2WorkingDir
$ra2Shortcut.Description = "Launch Accessible Red Alert 2 with NVDA support and Tactical Cursor"
if (Test-Path "$ra2WorkingDir\ra2.ico") {
    $ra2Shortcut.IconLocation = "$ra2WorkingDir\ra2.ico"
}
$ra2Shortcut.Save()
Write-Host "Created: Play Accessible Red Alert 2 (OpenRA).lnk" -ForegroundColor Green

# 2. Shortcut: Play Accessible C&C Remastered (Steam)
$steamRemasteredShortcut = $wsh.CreateShortcut("$desktop\Play Accessible C&C Remastered Collection.lnk")
$steamRemasteredShortcut.TargetPath = "steam://rungameid/1213210"
$steamRemasteredShortcut.Description = "Launch Command & Conquer Remastered Collection with Direct Accessibility Mods"
$steamRemasteredShortcut.Save()
Write-Host "Created: Play Accessible C&C Remastered Collection.lnk" -ForegroundColor Green

# 3. Shortcut: Run Accessibility Verification Test Suite
$testRunnerScript = "C:\Users\vegas\OneDrive\Documentos\GitHub\Accessibility-mod-command-and-conquer\docs\run_accessibility_tests.py"
$testShortcut = $wsh.CreateShortcut("$desktop\Check Accessibility Mod Status.lnk")
$testShortcut.TargetPath = "python.exe"
$testShortcut.Arguments = "`"$testRunnerScript`""
$testShortcut.Description = "Run automated 20-point test suite for C&C accessibility mods"
$testShortcut.Save()
Write-Host "Created: Check Accessibility Mod Status.lnk" -ForegroundColor Green

Write-Host "All Desktop shortcuts created successfully!" -ForegroundColor Cyan
