#!/usr/bin/env python3
"""
PhotoWatermark Windows专用打包脚本
解决Windows平台DLL缺失和依赖问题
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def check_environment():
    """检查打包环境"""
    print("🔍 检查打包环境...")
    
    # 检查操作系统
    if platform.system() != 'Windows':
        print("⚠️  警告: 当前不是Windows系统，打包的程序可能无法在Windows上正常运行")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python版本过低，建议使用Python 3.8+")
        return False
    
    # 检查PyInstaller
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"🔧 PyInstaller版本: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller未安装，正在安装...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
            print("✅ PyInstaller安装完成")
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False
    
    return True

def install_dependencies():
    """安装依赖"""
    print("📦 安装项目依赖...")
    
    try:
        # 升级pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # 安装requirements.txt中的依赖
        if Path('requirements.txt').exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                          check=True, capture_output=True)
            print("✅ 项目依赖安装完成")
        else:
            print("⚠️  未找到requirements.txt文件")
            
        # 确保关键依赖已安装
        key_packages = ['pillow', 'tkinterdnd2', 'piexif', 'tqdm', 'colorama', 'click']
        for package in key_packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                              check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"⚠️  {package} 安装失败")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def create_version_info():
    """创建Windows版本信息文件"""
    print("📝 创建版本信息文件...")
    
    version_info = '''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'PhotoWatermark'),
          StringStruct(u'FileDescription', u'图片水印工具'),
          StringStruct(u'FileVersion', u'1.0.0.0'),
          StringStruct(u'InternalName', u'PhotoWatermark'),
          StringStruct(u'LegalCopyright', u'Copyright 2024'),
          StringStruct(u'OriginalFilename', u'PhotoWatermark.exe'),
          StringStruct(u'ProductName', u'PhotoWatermark'),
          StringStruct(u'ProductVersion', u'1.0.0.0')]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✅ 版本信息文件创建完成")

def clean_build():
    """清理构建文件"""
    print("🧹 清理之前的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name, ignore_errors=True)
            print(f"  清理目录: {dir_name}")
    
    # 清理spec文件（除了我们的专用文件）
    for spec_file in Path('.').glob('PhotoWatermark.spec'):
        if spec_file.name != 'PhotoWatermark_windows.spec':
            spec_file.unlink()
            print(f"  清理文件: {spec_file}")

def build_application():
    """构建应用程序"""
    print("🚀 开始构建Windows应用程序...")
    
    # 检查spec文件，优先使用简化版本
    spec_files = ['PhotoWatermark_windows_simple.spec', 'PhotoWatermark_windows.spec']
    spec_file = None
    
    for sf in spec_files:
        if Path(sf).exists():
            spec_file = sf
            print(f"📄 使用配置文件: {spec_file}")
            break
    
    if not spec_file:
        print(f"❌ 未找到配置文件: {spec_files}")
        return False
    
    try:
        # 运行PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', spec_file]
        print(f"🔧 执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ 构建成功完成！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stdout:
            print("标准输出:", e.stdout)
        if e.stderr:
            print("错误输出:", e.stderr)
        return False

def create_auxiliary_files():
    """创建辅助文件"""
    print("📝 创建辅助文件...")
    
    dist_dir = Path('dist/PhotoWatermark')
    if not dist_dir.exists():
        print("❌ 构建目录不存在")
        return
    
    # 创建启动脚本
    startup_script = dist_dir / '启动PhotoWatermark.bat'
    with open(startup_script, 'w', encoding='gbk') as f:
        f.write('@echo off\n')
        f.write('cd /d "%~dp0"\n')
        f.write('start "" "PhotoWatermark.exe"\n')
    
    # 创建使用说明
    readme_file = dist_dir / '使用说明.txt'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write('''PhotoWatermark - 图片水印工具
================================

使用方法:
1. 双击 PhotoWatermark.exe 启动程序
2. 或者双击 "启动PhotoWatermark.bat"

功能特点:
- 支持文本和图片水印
- 批量处理图片
- 多种水印位置选择
- 实时预览效果
- 支持多种图片格式

如果遇到问题:
- 确保系统已安装 Visual C++ Redistributable
- 检查防病毒软件是否阻止程序运行
- 以管理员身份运行程序
- 确保有足够的磁盘空间

系统要求:
- Windows 10 或更高版本
- 至少 4GB 内存
- 100MB 可用磁盘空间

技术支持:
如有问题请联系开发者或查看项目文档。
''')
    
    print("✅ 辅助文件创建完成")

def verify_build():
    """验证构建结果"""
    print("🔍 验证构建结果...")
    
    exe_path = Path('dist/PhotoWatermark/PhotoWatermark.exe')
    if exe_path.exists():
        size = exe_path.stat().st_size
        size_mb = size / (1024 * 1024)
        print(f"✅ 可执行文件: {exe_path}")
        print(f"📊 文件大小: {size_mb:.1f} MB")
        
        # 检查关键文件
        dist_dir = Path('dist/PhotoWatermark')
        important_files = []
        for file_path in dist_dir.rglob('*'):
            if file_path.is_file():
                important_files.append(file_path.name)
        
        print(f"📁 包含文件数量: {len(important_files)}")
        
        # 检查是否包含Python DLL
        python_dlls = [f for f in important_files if 'python' in f.lower() and f.endswith('.dll')]
        if python_dlls:
            print(f"✅ 包含Python DLL: {', '.join(python_dlls)}")
        else:
            print("⚠️  未找到Python DLL文件")
        
        return True
    else:
        print("❌ 未找到生成的可执行文件")
        return False

def main():
    """主函数"""
    print("🎯 PhotoWatermark Windows 专用打包工具")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败")
        return 1
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return 1
    
    # 创建版本信息
    create_version_info()
    
    # 清理构建
    clean_build()
    
    # 构建应用
    if not build_application():
        print("❌ 构建失败")
        return 1
    
    # 创建辅助文件
    create_auxiliary_files()
    
    # 验证构建
    if verify_build():
        print("\n🎉 Windows打包完成！")
        print("\n📋 下一步:")
        print("1. 测试 dist/PhotoWatermark/PhotoWatermark.exe")
        print("2. 在干净的Windows系统上测试")
        print("3. 检查所有功能是否正常工作")
        print("4. 如需要，可以使用Inno Setup创建安装程序")
        return 0
    else:
        print("❌ 构建验证失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
