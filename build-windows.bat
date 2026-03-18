@echo off
chcp 65001 >nul
echo ========================================
echo   吾爱八卦 - Windows 打包脚本
echo   Build Windows EXE for WuAiBaGua
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [1/5] 创建虚拟环境...
if exist "win-venv" (
    rmdir /s /q win-venv
)
python -m venv win-venv

echo [2/5] 激活虚拟环境并安装依赖...
call win-venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -r requirements-win.txt -q

echo [3/5] 安装打包工具...
pip install pyinstaller pyinstaller-hooks-contrib -q

echo [4/5] 开始打包...
pyinstaller wuaibagua.spec --clean

echo [5/5] 检查输出...
if exist "dist\吾爱八卦.exe" (
    echo.
    echo ========================================
    echo   打包成功！
    echo   输出文件：dist\吾爱八卦.exe
    echo   大小：
    dir /B dist\吾爱八卦.exe
    echo ========================================
) else (
    echo.
    echo [错误] 打包失败，请查看日志
)

echo.
pause
