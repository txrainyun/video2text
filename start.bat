@echo off
chcp 65001 >nul
title Video2Text
cd /d "%~dp0"

echo ========================================
echo  Video2Text - 一键启动
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

:: 检查依赖
%PYTHON_CMD% -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo [安装] 正在安装依赖...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 安装失败，请检查网络
        pause
        exit /b 1
    )
    echo [OK] 依赖安装完成
)

:: 检查 ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未找到 ffmpeg，视频文件处理可能受限
    echo        可通过 winget install ffmpeg 或 https://ffmpeg.org 安装
)

echo.
echo ========================================
echo  启动完成！访问: http://127.0.0.1:8000
echo  关闭窗口即可停止服务
echo ========================================
echo.

python app.py
