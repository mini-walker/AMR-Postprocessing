@echo off
REM ---------------------------------------------
REM Automatically detect the Python script with 
REM "if __name__ == '__main__'" and build it to an EXE
REM Author: Shanqin Jin
REM Notice: You should run this script as an administrator
REM ---------------------------------------------

REM Create a temporary variable to store main script name
set "MAINFILE="
for %%f in (*.py) do (
    findstr /C:"if __name__ == \"__main__\"" "%%f" >nul 2>nul
    if %errorlevel%==0 (
        set "MAINFILE=%%~nf"
        goto found
    )
)

echo [ERROR] No Python script containing 'if __name__ == "__main__"' was found.
pause
exit /b

:found
echo [INFORMATION] Found main script: %MAINFILE%.py

REM Check if the script is already running and terminate it
echo [INFORMATION] Checking if %MAINFILE%.exe is running...
taskkill /f /im %MAINFILE%.exe >nul 2>nul
timeout /t 1 >nul


REM Clean previous build directories and spec file
rmdir /s /q build >nul 2>nul
rmdir /s /q dist >nul 2>nul
del /f /q %MAINFILE%.spec >nul 2>nul


rem REM Ensure PyInstaller is installed and up to date
rem echo [INFORMATION] Installing or upgrading PyInstaller...
rem python -m pip install --upgrade pip >nul
rem python -m pip install pyinstaller >nul


REM Build the script to a single .exe file
REM -W ignore no warnings
REM --onefile creates a single executable
REM --clean cleans up temporary files from previous builds
echo [INFORMATION] Building %MAINFILE%.py ...
REM python -W ignore -m PyInstaller --onefile --clean %MAINFILE%.py

REM Redirect stderr to stdout and filter out warnings
python -W ignore -m PyInstaller --onefile --collect-all yt --collect-all cmyt --clean %MAINFILE%.py 2>&1 | findstr /V /C:"WARNING"



REM Done!
echo ---------------------------------------------
echo  [INFORMATION] Build complete! Executable located at: dist\%MAINFILE%.exe
pause
