@echo off
chcp 65001 >nul
title Video2Text - 本地音视频转文字工具
echo.
echo ========================================
echo   Video2Text - 本地音视频转文字工具
echo ========================================
echo.

cd /d "%~dp0"

:: 自动查找 Python
set PYTHON_EXE=
for %%A in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%USERPROFILE%\python-sdk\python3.13.2\python.exe"
    "%USERPROFILE%\python-sdk\python3.12\python.exe"
    "%USERPROFILE%\python-sdk\python3.11\python.exe"
    "%USERPROFILE%\python-sdk\python3.10\python.exe"
) do (
    if exist %%A set "PYTHON_EXE=%%~A"
)

:: 如果没找到，尝试 PATH 中的 python
if "%PYTHON_EXE%"=="" (
    where python >nul 2>&1
    if %errorlevel%==0 (
        for /f "delims=" %%B in ('where python') do (
            set "PYTHON_EXE=%%B"
            goto :found
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [错误] 未找到 Python！
    echo.
    echo 请先安装 Python 3.10 或以上版本：
    echo https://www.python.org/downloads/
    echo.
    echo 安装时务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:found
echo [OK] 找到 Python: %PYTHON_EXE%
echo.

:: 检查并安装依赖
echo [1/3] 检查依赖...
%PYTHON_EXE% -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] 正在安装依赖包，请稍候...
    %PYTHON_EXE% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
) else (
    echo [OK] 依赖已就绪
)

:: 检查 ffmpeg
echo [3/3] 检查 ffmpeg...
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未找到 ffmpeg，视频文件处理可能受限
    echo 可通过 winget install ffmpeg 或 https://ffmpeg.org 安装
)

:: 创建必要目录
if not exist "uploads" mkdir uploads
if not exist "models" mkdir models

echo.
echo ========================================
echo   启动中...
echo ========================================
echo.
echo   访问地址: http://127.0.0.1:8000
echo   按 Ctrl+C 停止服务
echo.
echo   首次使用会自动下载 Whisper 模型
echo ========================================
echo.

%PYTHON_EXE% app_simple.py
pause
