@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 超市AI营销分析系统 - 启动脚本
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

echo [启动] 正在准备启动超市AI营销分析系统...
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
echo 按 Ctrl+C 停止服务
echo.
echo ========================================
echo.
echo [提示] 启动需要一些时间,请稍候...
echo.

:: 创建启动日志目录
if not exist "logs" mkdir "logs"

:: 检查是否有静默模式参数
set silent_mode=0
if "%~1"=="silent" (
    set silent_mode=1
    echo [模式] 静默模式已启用，日志将保存到文件但不显示
    echo.
)

:: 启动后端服务
echo [后端] 正在启动 FastAPI 服务...
cd /d "%~dp0"
if !silent_mode! == 1 (
    start "后端 API" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > logs\backend.log 2>&1"
) else (
    start "后端 API" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
)

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端服务
echo [前端] 正在启动 Vite 开发服务器...
cd frontend
if !silent_mode! == 1 (
    start "前端应用" cmd /k "npm run dev > ..\logs\frontend.log 2>&1"
) else (
    start "前端应用" cmd /k "npm run dev"
)
cd ..

:: 等待前端启动
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 启动完成!
echo ========================================
echo.
echo [成功] 系统已启动,请通过浏览器访问: http://127.0.0.1:5173
echo.
echo 日志输出:
echo   - 查看后端日志: 切换到[后端 API]窗口
echo   - 查看前端日志: 切换到[前端应用]窗口
echo   - 停止服务: 关闭两个服务窗口再关闭此窗口
echo.

:: 保持窗口打开
echo [等待] 按任意键关闭本窗口 (服务会继续运行)
pause >nul
