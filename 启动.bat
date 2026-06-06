@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

title Video2Text - 本地音视频转文字工具

echo ========================================
echo  Video2Text - 本地音视频转文字工具
echo ========================================
echo.

:: 先查已知路径
set "PY_PATH=%USERPROFILE%\python-sdk\python3.13.2\python.exe"
if exist "%PY_PATH%" goto found_py

:: 查其他常见安装路径
set "FALLBACKS=%LOCALAPPDATA%\Programs\Python\Python313\python.exe %LOCALAPPDATA%\Programs\Python\Python312\python.exe %LOCALAPPDATA%\Programs\Python\Python311\python.exe %LOCALAPPDATA%\Programs\Python\Python310\python.exe %USERPROFILE%\python-sdk\python3.13.2\python.exe %USERPROFILE%\python-sdk\python3.12\python.exe %USERPROFILE%\python-sdk\python3.11\python.exe %USERPROFILE%\python-sdk\python3.10\python.exe"
for %%P in (%FALLBACKS%) do (
    if exist "%%P" (
        set "PY_PATH=%%P"
        goto found_py
    )
)

:: 尝试 py 启动器
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_PATH=py"
    goto found_py
)

:: 最后试 PATH 中的 python（排除 WindowsApps）
where python 2>nul | findstr /V /I "WindowsApps" >nul
if %errorlevel% equ 0 (
    for /f "delims=" %%X in ('where python 2^>nul ^| findstr /V /I "WindowsApps"') do (
        set "PY_PATH=%%X"
        goto found_py
    )
)

echo [错误] 找不到 Python！
echo 请先安装 Python 3.10+：https://www.python.org/downloads/
pause
exit /b 1

:found_py
echo [OK] Python: %PY_PATH%
"%PY_PATH%" --version
echo.

:: 检查依赖
echo [1/3] 检查依赖...
"%PY_PATH%" -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] 安装依赖...
    "%PY_PATH%" -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络
        pause
        exit /b 1
    )
) else (
    echo [OK] 依赖已就绪
)

echo [3/3] 检查 ffmpeg...
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未找到 ffmpeg（视频处理可能受限）
    echo        可安装: https://ffmpeg.org/download.html
)

if not exist "uploads" mkdir uploads

echo.
echo ========================================
echo  启动成功！
echo  访问地址: http://127.0.0.1:8000
echo  关闭此窗口即可停止服务
echo ========================================
echo.

"%PY_PATH%" app.py
pause
