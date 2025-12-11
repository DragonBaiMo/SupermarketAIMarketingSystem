@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 超市AI营销分析系统 - 日志查看工具
echo ========================================
echo.

:menu
echo 请选择查看哪类日志：
echo 1) 查看后端日志 (后端 API:8000)
echo 2) 查看前端日志 (前端应用:5173)
echo 3) 同时查看前后端日志
echo 0) 退出
echo.
set /p choice="请输入选项 (0-3): "

if "!choice!"=="1" goto view_backend
if "!choice!"=="2" goto view_frontend
if "!choice!"=="3" goto view_both
if "!choice!"=="0" goto end

echo [错误] 无效选项
echo.
goto menu

:view_backend
if not exist "logs\backend.log" (
    echo [错误] 后端日志文件不存在
echo [提示] 请确保 start.bat 或 start-silent.bat 已经运行
echo.
    goto menu
)
echo.
echo ========================================
echo 正在监视后端日志 - 按 Ctrl+C 停止
echo ========================================
echo.
more /c +1 < "logs\backend.log"
type "logs\backend.log"
echo [等待新日志...]
echo.
goto menu

:view_frontend
if not exist "logs\frontend.log" (
    echo [错误] 前端日志文件不存在
    echo [提示] 请确保 start.bat 或 start-silent.bat 已经运行
    echo.
    goto menu
)
echo.
echo ========================================
echo 正在监视前端日志 - 按 Ctrl+C 停止
echo ========================================
echo.
type "logs\frontend.log"
echo [等待新日志...]
echo.
goto menu

:view_both
echo.
echo ========================================
echo 查看前后端日志
echo ========================================
echo.
if exist "logs\backend.log" (
    echo --- 后端日志 (*.\logs\backend.log) ---
    echo.
    type "logs\backend.log"
    echo.
) else (
    echo [提示] 后端日志文件不存在
)

if exist "logs\frontend.log" (
    echo --- 前端日志 (*.\logs\frontend.log) ---
    echo.
    type "logs\frontend.log"
    echo.
) else (
    echo [提示] 前端日志文件不存在
)
echo [按任意键返回主菜单]
pause >nul
goto menu

:end
echo.
echo 退出日志查看工具
