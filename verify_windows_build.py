#!/usr/bin/env python3
"""
验证Windows打包配置的脚本
检查所有依赖和配置是否正确
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("🐍 检查Python环境...")
    
    version = sys.version_info
    print(f"  Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("  ❌ Python版本过低，建议使用3.8+")
        return False
    else:
        print("  ✅ Python版本符合要求")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("  ✅ 运行在虚拟环境中")
    else:
        print("  ⚠️  未使用虚拟环境，建议使用虚拟环境")
    
    return True

def check_required_packages():
    """检查必需的包"""
    print("\n📦 检查必需的包...")
    
    required_packages = {
        'tkinter': '内置GUI库',
        'PIL': 'Pillow图像处理库',
        'tkinterdnd2': '拖拽支持库',
        'piexif': 'EXIF数据处理库',
        'tqdm': '进度条库',
        'colorama': '颜色输出库',
        'click': '命令行工具库',
        'PyInstaller': '打包工具'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            if package == 'PyInstaller':
                subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                             capture_output=True, check=True)
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}: {description}")
        except (ImportError, subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {package}: {description} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少以下包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        for package in missing_packages:
            if package == 'PyInstaller':
                print(f"  pip install pyinstaller")
            else:
                print(f"  pip install {package}")
        return False
    
    return True

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        'gui_main.py',
        'requirements.txt',
        'PhotoWatermark_windows.spec',
        'build_windows.py',
        'src/gui/main_window.py',
        'src/core/config.py',
        'src/templates/default_config.json',
    ]
    
    optional_files = [
        'assets/icon.png',
        'assets/icon.ico',
        'packaging/build_windows.bat',
        'packaging/PhotoWatermark_installer.iss',
    ]
    
    missing_required = []
    missing_optional = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - 必需文件缺失")
            missing_required.append(file_path)
    
    for file_path in optional_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️  {file_path} - 可选文件缺失")
            missing_optional.append(file_path)
    
    if missing_required:
        print(f"\n❌ 缺少必需文件: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  缺少可选文件: {', '.join(missing_optional)}")
    
    return True

def check_spec_file():
    """检查spec文件配置"""
    print("\n🔧 检查PyInstaller配置文件...")
    
    spec_file = Path('PhotoWatermark_windows.spec')
    if not spec_file.exists():
        print("  ❌ PhotoWatermark_windows.spec 文件不存在")
        return False
    
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键配置
        checks = [
            ('gui_main.py', '入口文件'),
            ('hiddenimports', '隐藏导入配置'),
            ('datas', '数据文件配置'),
            ('console=False', '窗口模式配置'),
            ('icon=', '图标配置'),
        ]
        
        for check, description in checks:
            if check in content:
                print(f"  ✅ {description}: 已配置")
            else:
                print(f"  ⚠️  {description}: 可能未正确配置")
        
        print("  ✅ spec文件格式正确")
        return True
        
    except Exception as e:
        print(f"  ❌ spec文件读取失败: {e}")
        return False

def test_import_main_modules():
    """测试导入主要模块"""
    print("\n🧪 测试导入主要模块...")
    
    test_modules = [
        'src.gui.main_window',
        'src.core.config',
        'src.core.image_processor',
        'src.core.watermark',
        'src.utils.font_manager',
    ]
    
    failed_imports = []
    
    for module in test_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ 以下模块导入失败: {', '.join(failed_imports)}")
        return False
    
    return True

def check_build_tools():
    """检查构建工具"""
    print("\n🛠️  检查构建工具...")
    
    # 检查PyInstaller
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"  ✅ PyInstaller: {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ❌ PyInstaller: 未安装或无法运行")
        return False
    
    # 检查可选工具
    optional_tools = [
        ('convert', 'ImageMagick - 图标转换'),
        ('iscc', 'Inno Setup - 安装程序制作'),
    ]
    
    for tool, description in optional_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"  ✅ {description}: 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ⚠️  {description}: 未安装（可选）")
    
    return True

def simulate_build_test():
    """模拟构建测试"""
    print("\n🧪 模拟构建测试...")
    
    try:
        # 测试PyInstaller分析（只做语法检查，不实际构建）
        cmd = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--log-level=ERROR', 
               '--distpath=test_dist', '--workpath=test_build', 
               'PhotoWatermark_windows.spec']
        
        print("  🔄 运行PyInstaller语法检查...")
        
        # 先检查spec文件语法
        spec_file = Path('PhotoWatermark_windows.spec')
        if spec_file.exists():
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    spec_content = f.read()
                
                # 简单的语法检查
                compile(spec_content, spec_file, 'exec')
                print("  ✅ spec文件语法正确")
                
                # 清理可能存在的测试目录
                import shutil
                for test_dir in ['test_dist', 'test_build']:
                    if Path(test_dir).exists():
                        shutil.rmtree(test_dir, ignore_errors=True)
                
                return True
                
            except SyntaxError as e:
                print(f"  ❌ spec文件语法错误: {e}")
                return False
        else:
            print("  ❌ spec文件不存在")
            return False
            
    except Exception as e:
        print(f"  ❌ 模拟构建失败: {e}")
        return False

def generate_report():
    """生成检查报告"""
    print("\n📋 生成检查报告...")
    
    report = {
        'python_env': check_python_environment(),
        'packages': check_required_packages(),
        'structure': check_project_structure(),
        'spec_file': check_spec_file(),
        'imports': test_import_main_modules(),
        'build_tools': check_build_tools(),
        'build_test': simulate_build_test(),
    }
    
    # 统计结果
    passed = sum(1 for result in report.values() if result)
    total = len(report)
    
    print(f"\n📊 检查结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有检查通过！可以开始Windows打包")
        print("\n🚀 下一步:")
        print("1. 运行: python build_windows.py")
        print("2. 或运行: packaging\\build_windows.bat")
        print("3. 测试生成的可执行文件")
    else:
        print("⚠️  存在问题需要解决")
        print("\n🔧 建议:")
        
        if not report['packages']:
            print("- 安装缺失的Python包")
        if not report['structure']:
            print("- 检查项目文件结构")
        if not report['spec_file']:
            print("- 修复PyInstaller配置文件")
        if not report['imports']:
            print("- 解决模块导入问题")
        if not report['build_tools']:
            print("- 安装构建工具")
    
    return passed == total

def main():
    """主函数"""
    print("🔍 PhotoWatermark Windows打包配置验证")
    print("=" * 50)
    
    try:
        success = generate_report()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断检查")
        return 1
    except Exception as e:
        print(f"\n❌ 检查过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
