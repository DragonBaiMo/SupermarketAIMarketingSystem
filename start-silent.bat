@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 超市AI营销分析系统 - 静默启动脚本
echo ========================================
echo.

:: 检查后端虚拟环境是否存在
if not exist ".venv" (
    echo [错误] Python 虚拟环境不存在
    echo [提示] 请先运行 reset-env.bat 初始化环境
    pause
    exit /b 1
)

:: 检查前端依赖是否已安装
if not exist "frontend\node_modules" (
    echo [错误] 前端依赖未安装
    echo [提示] 请先运行 reset-env.bat 初始化环境
    pause
    exit /b 1
)

echo [静默启动] 正在启动超市AI营销分析系统...
echo.
echo 访问地址:
echo   - 前端应用: http://127.0.0.1:5173
echo   - 后端 API: http://127.0.0.1:8000
echo   - API 文档: http://127.0.0.1:8000/docs
echo.
echo 操作说明:
echo   - 首次使用请在数据管理中上传销售数据
echo   - 或加载默认数据: .\data\商城详细销售数据.csv
echo.
echo [提示] 日志将保存到 logs 目录,运行 view-logs.bat 实时查看
echo [提示] 启动需要一些时间,请稍候...
echo.

:: 创建启动日志目录
if not exist "logs" mkdir "logs"

:: 启动后端服务到后台
echo [后端] 正在启动 FastAPI 服务...
cd /d "%~dp0"
start ".venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > logs\backend.log 2>&1"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端服务到后台
echo [前端] 正在启动 Vite 开发服务器...
cd frontend
start "npm run dev > ..\logs\frontend.log 2>&1"
cd ..

:: 等待前端启动
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 启动完成! 请访问: http://127.0.0.1:5173
echo ========================================
echo.
echo [成功] 系统已在后台运行
echo.
echo 查看运行状态:
echo   - 运行 view-logs.bat 实时查看日志
echo   - 查看日志: .\logs\backend.log
echo   - 查看日志: .\logs\frontend.log
echo.
echo 停止服务:
echo   - 按任意键停止服务 (关闭所有窗口)
echo.

:: 保持窗口打开，按任意键停止服务
pause >nul

echo.
echo [停止] 正在关闭服务...
taskkill /F /FI "WINDOWTITLE eq python.exe" 2>nul
taskkill /F /FI "WINDOWTITLE eq node.exe" 2>nul
echo [完成] 服务已停止
