@echo off
chcp 65001 >nul
title Video2Text - 本地音视频转文字工具
cd /d "%~dp0"

echo ========================================
echo  Video2Text - 本地音视频转文字工具
echo ========================================
echo.

:: 自动找 Python
set PYTHON_CMD=
for %%A in (python py python3) do (
    %%A --version >nul 2>&1 && set PYTHON_CMD=%%A && goto found_py
)

echo [错误] 找不到 Python，请先安装 https://python.org
pause
exit /b 1

:found_py
echo [OK] 使用: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

:: 检查并安装依赖
echo [1/3] 检查依赖...
%PYTHON_CMD% -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] 正在安装依赖...
    %PYTHON_CMD% -m pip install -r requirements.txt
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
    echo [提示] 未找到 ffmpeg，视频文件处理可能受限
    echo        可通过 https://ffmpeg.org 下载安装
)

:: 创建必要目录
if not exist "uploads" mkdir uploads

echo.
echo ========================================
echo  服务已启动
echo  访问地址: http://127.0.0.1:8000
echo  关闭此窗口即可停止服务
echo ========================================
echo.

python app.py
