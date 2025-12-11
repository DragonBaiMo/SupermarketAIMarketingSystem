@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 超市AI营销分析系统 - 环境重置脚本
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python,请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [提示] 检测到 Python 环境正常
echo.

:: 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js,请先安装 Node.js 16+
    pause
    exit /b 1
)

echo [提示] 检测到 Node.js 环境正常
echo.

:: 询问用户是否继续
set /p confirm="是否继续重置虚拟环境? 这将删除现有的所有依赖 (Y/N): "
if /i not "%confirm%"=="Y" (
    echo [取消] 用户取消操作
    pause
    exit /b 0
)

echo.
echo ========================================
echo 第一步: 清理现有环境
echo ========================================
echo.

:: 删除后端虚拟环境
if exist ".venv" (
    echo [清理] 正在删除 Python 虚拟环境...
    rmdir /s /q ".venv"
    echo [完成] Python 虚拟环境已删除
) else (
    echo [跳过] Python 虚拟环境不存在
)

:: 删除 Python 缓存
if exist "__pycache__" (
    echo [清理] 正在删除 Python 缓存...
    for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    echo [完成] Python 缓存已清理
)

if exist "*.pyc" (
    echo [清理] 正在删除 .pyc 文件...
    del /s /q *.pyc >nul 2>&1
    echo [完成] .pyc 文件已清理
)

:: 清理前端 node_modules
echo.
echo [清理] 正在检查前端依赖...
cd frontend
if exist "node_modules" (
    echo [清理] 正在删除 node_modules...
    rmdir /s /q "node_modules"
    echo [完成] node_modules 已删除
) else (
    echo [跳过] node_modules 不存在
)

cd ..

echo.
echo ========================================
echo 第二步: 创建 Python 虚拟环境
echo ========================================
echo.

echo [创建] 正在创建 Python 虚拟环境...
python -m venv .venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)
echo [完成] Python 虚拟环境创建成功

echo.
echo ========================================
echo 第三步: 安装后端依赖
echo ========================================
echo.

echo [升级] 正在升级 pip...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo [警告] pip 升级失败,但将继续安装依赖
)

echo [安装] 正在安装项目依赖...
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [完成] 后端依赖安装成功

echo.
echo ========================================
echo 第四步: 安装前端依赖
echo ========================================
echo.

cd frontend
echo [安装] 正在安装前端依赖...
call npm install
if errorlevel 1 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)
echo [完成] 前端依赖安装成功
cd ..

echo.
echo ========================================
echo 环境重置完成!
echo ========================================
echo.
echo [成功] 环境已重置完成,可以使用 start.bat 启动应用
echo.
echo 启动说明:
echo   1. 运行 start.bat 启动前后端应用
echo   2. 后端 API 将运行在: http://127.0.0.1:8000
echo   3. 前端将运行在: http://127.0.0.1:5173
echo   4. 数据文件路径: .\data\
echo.
echo 功能模块:
echo   - 数据管理: 上传/加载销售数据 CSV
echo   - 聚类分析: 客户分群与行为分析
echo   - 销售预测: 时间序列预测
echo   - 商品推荐: 智能推荐算法
echo   - 促销规则: 营销策略优化
echo.

pause
