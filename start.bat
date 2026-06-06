
@echo off
echo ========================================
echo Video2Text - Start Application
echo ========================================
echo.

cd /d "%~dp0"
echo Looking for Python...

set PYTHON_CMD=

REM Try different Python commands
echo Checking "python"...
python --version &gt;nul 2&gt;&amp;1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto found
)

echo Checking "py"...
py --version &gt;nul 2&gt;&amp;1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto found
)

echo Checking "python3"...
python3 --version &gt;nul 2&gt;&amp;1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto found
)

echo.
echo ERROR: Python is not found!
echo Please install Python first from https://python.org
echo.
pause
exit /b 1

:found
echo.
echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo Checking dependencies...
%PYTHON_CMD% -c "import fastapi" 2&gt;nul
if %errorlevel% neq 0 (
    echo Installing dependencies first...
    %PYTHON_CMD% -m pip install -r requirements_simple.txt
)

echo.
echo Starting Video2Text (Minimal version)...
echo.
echo Open your browser and go to: http://127.0.0.1:8000
echo.
echo This version simulates transcription for testing.
echo.
%PYTHON_CMD% app_minimal.py
pause
