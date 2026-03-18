@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ╔══════════════════════════════════════════════╗
echo ║   吾爱八卦 - Windows EXE 一键打包工具       ║
echo ║   WuAiBaGua Windows Packager                 ║
echo ╚══════════════════════════════════════════════╝
echo.

REM 检查 Python
where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    echo.
    echo 请先安装 Python 3.10 或 3.11：
    echo https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [✓] Python 已安装
python --version
echo.

REM 检查是否在项目目录
if not exist "main.py" (
    echo [错误] 未找到 main.py，请在项目目录运行此脚本
    pause
    exit /b 1
)

echo [✓] 项目目录正确
echo.

echo ═══════════════════════════════════════════════
echo 步骤 1/4: 安装依赖
echo ═══════════════════════════════════════════════
echo.

echo 正在安装 Kivy...
pip install kivy kivy-deps.sdl2 kivy-deps.glew -q
if errorlevel 1 (
    echo [警告] Kivy 安装可能失败，继续尝试...
)

echo 正在安装 PyInstaller...
pip install pyinstaller pyinstaller-hooks-contrib -q

echo.
echo ═══════════════════════════════════════════════
echo 步骤 2/4: 检查文件
echo ═══════════════════════════════════════════════
echo.

if exist "data" (
    echo [✓] data 目录存在
    for %%f in (data\*.txt) do (
        set /a filecount+=1
    )
    echo     包含 !filecount! 个卦辞文件
) else (
    echo [✗] data 目录不存在
)

if exist "fonts" (
    echo [✓] fonts 目录存在
) else (
    echo [✗] fonts 目录不存在
)

echo.
echo ═══════════════════════════════════════════════
echo 步骤 3/4: 开始打包
echo ═══════════════════════════════════════════════
echo.
echo 这可能需要 5-10 分钟，请耐心等待...
echo.

REM 执行打包
pyinstaller --name="吾爱八卦" ^
    --windowed ^
    --onefile ^
    --icon=NONE ^
    --add-data="data;data" ^
    --add-data="fonts;fonts" ^
    --hidden-import=kivy ^
    --hidden-import=kivy.uix ^
    --hidden-import=kivy.core ^
    --hidden-import=kivy.graphics ^
    --noconfirm ^
    --clean ^
    main.py

if errorlevel 1 (
    echo.
    echo ╔══════════════════════════════════════════════╗
    echo ║   打包失败！                                  ║
    echo ║   请查看上方的错误信息                        ║
    echo ╚══════════════════════════════════════════════╝
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════
echo 步骤 4/4: 检查结果
echo ═══════════════════════════════════════════════
echo.

if exist "dist\吾爱八卦.exe" (
    for %%A in ("dist\吾爱八卦.exe") do set "size=%%~zA"
    set /a sizeMB=!size!/1024/1024
    
    echo ╔══════════════════════════════════════════════╗
    echo ║   ✓ 打包成功！                               ║
    echo ╚══════════════════════════════════════════════╝
    echo.
    echo 输出文件：dist\吾爱八卦.exe
    echo 文件大小：约 !sizeMB! MB
    echo.
    echo 下一步：
    echo   1. 测试运行：双击 dist\吾爱八卦.exe
    echo   2. 分发：将 exe 文件复制到其他电脑
    echo.
    
    REM 询问是否打开文件夹
    set /p open="是否打开输出文件夹？(Y/N): "
    if /i "!open!"=="Y" (
        start dist
    )
) else (
    echo ╔══════════════════════════════════════════════╗
    echo ║   [错误] 未找到输出文件                      ║
    echo ║   请查看上方的错误信息                        ║
    echo ╚══════════════════════════════════════════════╝
)

echo.
pause
