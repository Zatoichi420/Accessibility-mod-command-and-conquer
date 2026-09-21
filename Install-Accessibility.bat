@echo off
setlocal
title Command and Conquer Accessibility Mods Installer

echo ======================================================================
echo    COMMAND AND CONQUER ACCESSIBILITY MODS - 1-CLICK INSTALLER
echo ======================================================================
echo.
echo Installing accessibility mods for:
echo   1. C^&C Tiberian Dawn Remastered (Steam)
echo   2. C^&C Red Alert 1 Remastered (Steam)
echo   3. C^&C Red Alert 2 (OpenRA-RA2)
echo.

echo [1/4] Deploying mod files and native libraries...
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy_mods.ps1"
if %errorlevel% neq 0 (
    echo [ERROR] Mod deployment failed!
    pause
    exit /b %errorlevel%
)

echo.
echo [2/4] Configuring Direct-Load into Steam installation...
set STEAM_DIR=F:\SteamLibrary\steamapps\common\CnCRemastered
set SRC_DIR=F:\SteamLibrary\steamapps\common\CnCRemastered\SOURCECODE

if exist "%STEAM_DIR%" (
    if not exist "%STEAM_DIR%\RedAlert.dll.stock_backup" (
        copy /y "%STEAM_DIR%\RedAlert.dll" "%STEAM_DIR%\RedAlert.dll.stock_backup" >nul
    )
    if not exist "%STEAM_DIR%\TiberianDawn.dll.stock_backup" (
        copy /y "%STEAM_DIR%\TiberianDawn.dll" "%STEAM_DIR%\TiberianDawn.dll.stock_backup" >nul
    )
    copy /y "%SRC_DIR%\bin\Win32\RedAlert.dll" "%STEAM_DIR%\RedAlert.dll" >nul
    copy /y "%SRC_DIR%\bin\Win32\TiberianDawn.dll" "%STEAM_DIR%\TiberianDawn.dll" >nul
    copy /y "%SRC_DIR%\REDALERT\AccessMod\ThirdParty\Tolk\*" "%STEAM_DIR%\" >nul
    echo Direct-load binaries installed to Steam root successfully.
) else (
    echo [WARNING] Steam CnCRemastered directory not found at default location.
)

echo.
echo [3/4] Creating 1-Click Desktop Shortcuts...
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcuts.ps1"

echo.
echo [4/4] Running Automated Verification Test Suite...
python "%~dp0docs\run_accessibility_tests.py"

echo.
echo ======================================================================
echo    INSTALLATION COMPLETE!
echo ======================================================================
echo.
echo You can now launch the games directly from your Desktop:
echo   - "Play Accessible Red Alert 2 (OpenRA)"
echo   - "Play Accessible C^&C Remastered Collection"
echo.
pause
