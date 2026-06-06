@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Video2Text
cd /d "%~dp0"

echo ========================================
echo  Video2Text - 一键启动
echo ========================================
echo.

:: 1) 查找已知安装路径中的 Python（跳过 WindowsApps 的假 Python）
set PYTHON_CMD=
set "KNOWN_PATHS=%LOCALAPPDATA%\Programs\Python\Python313\python.exe;%LOCALAPPDATA%\Programs\Python\Python312\python.exe;%LOCALAPPDATA%\Programs\Python\Python311\python.exe;%USERPROFILE%\python-sdk\python3.13.2\python.exe;%USERPROFILE%\python-sdk\python3.12\python.exe;C:\Python313\python.exe;C:\Python312\python.exe"

for %%P in (%KNOWN_PATHS%) do (
    if exist %%P (
        set "PYTHON_CMD=%%P"
        goto found_py
    )
)

:: 2) 没找到已知路径，尝试 PATH 中的 python（排除 WindowsApps）
where python 2>nul | findstr /V /I "WindowsApps" >nul
if %errorlevel% equ 0 (
    for /f "delims=" %%X in ('where python 2^>nul ^| findstr /V /I "WindowsApps"') do (
        set "PYTHON_CMD=%%X"
        goto found_py
    )
)

:: 3) 尝试 py 启动器
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

:: 检查依赖
"!PYTHON_CMD!" -c "import fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo [安装] 正在安装依赖...
    "!PYTHON_CMD!" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [错误] 安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo [OK] 依赖安装完成
)

:: 检查 ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未找到 ffmpeg（视频文件处理可能受限）
    echo        可通过 https://ffmpeg.org/download.html 安装
)

:: 创建上传目录
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
