@echo off
:: 1. 查找占用 8000 端口的进程 PID
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 正在尝试结束占用 8000 端口的进程，PID: %%a ...
    :: 2. 强制结束该进程
    taskkill /PID %%a /F
)
pause