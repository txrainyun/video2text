
@echo off
echo ========================================
echo Video2Text - Install Dependencies
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

echo Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements_simple.txt

echo.
echo ========================================
if %errorlevel% equ 0 (
    echo Success! Dependencies installed.
    echo ========================================
    echo.
    echo Now you can run "start.bat"
    echo.
) else (
    echo Failed to install dependencies
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)
pause
