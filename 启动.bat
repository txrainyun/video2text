@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Video2Text - 本地音视频转文字工具
cd /d "%~dp0"

echo ========================================
echo  Video2Text - 本地音视频转文字工具
echo ========================================
echo.

:: 1) 查找已知安装路径中的 Python
set PYTHON_CMD=
set "KNOWN_PATHS=%LOCALAPPDATA%\Programs\Python\Python313\python.exe;%LOCALAPPDATA%\Programs\Python\Python312\python.exe;%LOCALAPPDATA%\Programs\Python\Python311\python.exe;%LOCALAPPDATA%\Programs\Python\Python310\python.exe;%USERPROFILE%\python-sdk\python3.13.2\python.exe;%USERPROFILE%\python-sdk\python3.12\python.exe;%USERPROFILE%\python-sdk\python3.11\python.exe;%USERPROFILE%\python-sdk\python3.10\python.exe;C:\Python313\python.exe;C:\Python312\python.exe;C:\Python311\python.exe;C:\Python310\python.exe"

for %%P in (%KNOWN_PATHS%) do (
    if exist %%P (
        set "PYTHON_CMD=%%P"
        goto found_py
    )
)

:: 没找到已知路径，搜索 PATH 中的真 Python
where python 2>nul | findstr /V /I "WindowsApps" >nul
if %errorlevel% equ 0 (
    for /f "delims=" %%X in ('where python 2^>nul ^| findstr /V /I "WindowsApps"') do (
        set "PYTHON_CMD=%%X"
        goto found_py
    )
)

:: 尝试 py 启动器
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto found_py
)

echo [错误] 找不到 Python！
echo 请先安装 Python 3.10+：https://www.python.org/downloads/
echo 安装时务必勾选 "Add Python to PATH"
pause
exit /b 1

:found_py
echo [OK] Python: !PYTHON_CMD!
"!PYTHON_CMD!" --version
echo.

:: 检查安装依赖
echo [1/3] 检查依赖...
"!PYTHON_CMD!" -c "import fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo [2/3] 安装依赖...
    "!PYTHON_CMD!" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [错误] 依赖安装失败，请检查网络
        pause
        exit /b 1
    )
) else (
    echo [OK] 依赖已就绪
)

echo [3/3] 检查 ffmpeg...
where ffmpeg >nul 2>&1
if !errorlevel! neq 0 (
    echo [提示] 未找到 ffmpeg（视频文件处理可能受限）
    echo        可从 https://ffmpeg.org/download.html 下载
)

if not exist "uploads" mkdir uploads

echo.
echo ========================================
echo  启动成功！
echo  访问地址: http://127.0.0.1:8000
echo  关闭此窗口即可停止服务
echo ========================================
echo.

"!PYTHON_CMD!" app.py
pause
