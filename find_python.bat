
@echo off
echo Trying to find Python...
echo.

echo Checking "python"...
python --version
if %errorlevel% equ 0 goto found

echo.
echo Checking "py"...
py --version
if %errorlevel% equ 0 goto found

echo.
echo Checking "python3"...
python3 --version
if %errorlevel% equ 0 goto found

echo.
echo Checking "py -3...
py -3 --version
if %errorlevel% equ 0 goto found

echo.
echo Trying WindowsApps python...
"%LOCALAPPDATA%\Programs\Python\Python310\python.exe --version
if %errorlevel% equ 0 goto found

echo.
echo Could not find Python!
echo Please install Python first.
echo.
pause
exit /b 1

:found
echo.
echo ========================================
echo Python found!
echo ========================================
pause
