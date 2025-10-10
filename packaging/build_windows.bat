@echo off
REM PhotoWatermark Windows专用打包脚本
REM 解决DLL缺失和依赖问题

setlocal enabledelayedexpansion

echo ========================================
echo PhotoWatermark Windows 专用打包工具
echo ========================================
echo.

REM 获取项目根目录
set "SCRIPT_DIR=%~dp0"
for %%i in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fi"
cd /d "%ROOT_DIR%"

set "APP_NAME=PhotoWatermark"
set "ICON_PNG=%ROOT_DIR%\assets\icon.png"
set "ICON_ICO=%ROOT_DIR%\assets\icon.ico"

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
python --version

REM 检查虚拟环境
set "PYTHON_CMD=python"
if defined VIRTUAL_ENV (
    set "PYTHON_CMD=%VIRTUAL_ENV%\Scripts\python.exe"
    echo ✅ 使用虚拟环境: %VIRTUAL_ENV%
) else if exist "%ROOT_DIR%\venv\Scripts\python.exe" (
    set "PYTHON_CMD=%ROOT_DIR%\venv\Scripts\python.exe"
    echo ✅ 使用项目虚拟环境: %ROOT_DIR%\venv
) else (
    echo ⚠️  未检测到虚拟环境，使用系统Python
)

echo 🐍 Python命令: %PYTHON_CMD%
echo.

REM 升级pip和安装依赖
echo 📦 检查和安装依赖...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt
%PYTHON_CMD% -m pip install pyinstaller

REM 检查PyInstaller版本
echo 🔧 PyInstaller版本:
%PYTHON_CMD% -m PyInstaller --version
echo.

REM 创建图标文件
if exist "%ICON_PNG%" (
    echo 🎨 处理应用图标...
    where convert >nul 2>&1
    if !errorlevel! equ 0 (
        echo   转换PNG到ICO格式...
        convert "%ICON_PNG%" -resize 256x256 "%ICON_ICO%" 2>nul || echo   ⚠️  图标转换失败，将使用PNG
    ) else (
        echo   ⚠️  ImageMagick未安装，跳过ICO转换
    )
) else (
    echo ⚠️  未找到图标文件: %ICON_PNG%
)

REM 清理之前的构建
echo 🧹 清理之前的构建文件...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "*.spec" del "*.spec" 2>nul

REM 创建版本信息文件
echo 📝 创建版本信息...
(
echo VSVersionInfo^(
echo   ffi=FixedFileInfo^(
echo     filevers=^(1,0,0,0^),
echo     prodvers=^(1,0,0,0^),
echo     mask=0x3f,
echo     flags=0x0,
echo     OS=0x40004,
echo     fileType=0x1,
echo     subtype=0x0,
echo     date=^(0, 0^)
echo   ^),
echo   kids=[
echo     StringFileInfo^(
echo       [
echo         StringTable^(
echo           u'040904B0',
echo           [StringStruct^(u'CompanyName', u'PhotoWatermark'^),
echo           StringStruct^(u'FileDescription', u'图片水印工具'^),
echo           StringStruct^(u'FileVersion', u'1.0.0.0'^),
echo           StringStruct^(u'InternalName', u'PhotoWatermark'^),
echo           StringStruct^(u'LegalCopyright', u'Copyright 2024'^),
echo           StringStruct^(u'OriginalFilename', u'PhotoWatermark.exe'^),
echo           StringStruct^(u'ProductName', u'PhotoWatermark'^),
echo           StringStruct^(u'ProductVersion', u'1.0.0.0'^)]
echo         ^)
echo       ]
echo     ^),
echo     VarFileInfo^([VarStruct^(u'Translation', [1033, 1200]^)]^)
echo   ]
echo ^)
) > version_info.txt

REM 使用专用的Windows spec文件进行打包
echo 🚀 开始打包...
echo   使用配置文件: PhotoWatermark_windows.spec

%PYTHON_CMD% -m PyInstaller PhotoWatermark_windows.spec

if %errorlevel% equ 0 (
    echo.
    echo ✅ 打包成功完成！
    echo.
    echo 📁 输出位置: dist\%APP_NAME%\
    echo 🚀 主程序: dist\%APP_NAME%\%APP_NAME%.exe
    echo.
    
    REM 检查输出文件
    if exist "dist\%APP_NAME%\%APP_NAME%.exe" (
        echo 📊 文件信息:
        dir "dist\%APP_NAME%\%APP_NAME%.exe" | findstr "%APP_NAME%.exe"
        echo.
        
        REM 创建启动脚本
        echo 📝 创建启动脚本...
        (
        echo @echo off
        echo cd /d "%%~dp0"
        echo start "" "%APP_NAME%.exe"
        ) > "dist\%APP_NAME%\启动 %APP_NAME%.bat"
        
        REM 创建说明文件
        (
        echo PhotoWatermark - 图片水印工具
        echo ================================
        echo.
        echo 使用方法:
        echo 1. 双击 %APP_NAME%.exe 启动程序
        echo 2. 或者双击 "启动 %APP_NAME%.bat"
        echo.
        echo 如果遇到问题:
        echo - 确保系统已安装 Visual C++ Redistributable
        echo - 检查防病毒软件是否阻止程序运行
        echo - 以管理员身份运行程序
        echo.
        echo 技术支持: 请联系开发者
        ) > "dist\%APP_NAME%\使用说明.txt"
        
        echo ✅ 辅助文件创建完成
    ) else (
        echo ❌ 警告: 未找到生成的可执行文件
    )
    
    echo.
    echo 🎯 下一步:
    echo 1. 测试 dist\%APP_NAME%\%APP_NAME%.exe
    echo 2. 在干净的Windows系统上测试
    echo 3. 如需要，可以使用Inno Setup创建安装程序
    
) else (
    echo.
    echo ❌ 打包失败，错误代码: %errorlevel%
    echo.
    echo 🔍 故障排除:
    echo 1. 检查Python和依赖是否正确安装
    echo 2. 查看上方的错误信息
    echo 3. 尝试在虚拟环境中重新打包
    echo 4. 检查防病毒软件是否干扰
)

echo.
pause
