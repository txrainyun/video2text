
@echo off
chcp 65001 >nul
echo ========================================
echo Video2Text - 依赖安装工具
echo ========================================
echo.

cd /d "%~dp0"
echo 正在安装 Python 依赖...
echo.

python -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 依赖安装成功！
    echo ========================================
    echo.
    echo 现在可以运行 "启动.bat" 来启动应用
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 依赖安装失败，请检查错误信息
    echo ========================================
    echo.
)
pause
