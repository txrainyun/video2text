@echo off
cd /d "%~dp0"
title Video2Text

set PY_PATH=

:: check python-sdk first
if exist "%USERPROFILE%\python-sdk\python3.13.2\python.exe" set PY_PATH=%USERPROFILE%\python-sdk\python3.13.2\python.exe
if defined PY_PATH goto found_py

:: fallback paths
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PY_PATH=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if defined PY_PATH goto found_py
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PY_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if defined PY_PATH goto found_py
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set PY_PATH=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
if defined PY_PATH goto found_py

:: py launcher
where py >nul 2>&1
if %errorlevel% equ 0 set PY_PATH=py
if defined PY_PATH goto found_py

:: PATH python (skip WindowsApps)
where python 2>nul >"%TEMP%\pyfind.txt"
findstr /V /I "WindowsApps" "%TEMP%\pyfind.txt" >nul
if %errorlevel% equ 0 (
    for /f "delims=" %%X in ('type "%TEMP%\pyfind.txt" ^| findstr /V /I "WindowsApps"') do set PY_PATH=%%X
)
if defined PY_PATH goto found_py

echo [ERROR] Python not found!
echo Install from https://python.org
pause
exit /b 1

:found_py
echo [OK] Python: %PY_PATH%
"%PY_PATH%" --version
echo.

:: check & install deps
"%PY_PATH%" -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INSTALL] pip install -r requirements.txt...
    "%PY_PATH%" -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] install failed
        pause
        exit /b 1
    )
    echo [OK] deps installed
)

:: check ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] ffmpeg not found
    echo install: https://ffmpeg.org/download.html
)

if not exist "uploads" mkdir uploads

echo ========================================
echo  Ready! Open http://127.0.0.1:8000
echo  Close window to stop
echo ========================================
echo.

"%PY_PATH%" app.py
pause