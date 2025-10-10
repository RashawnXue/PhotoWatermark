#!/usr/bin/env python3
"""
PhotoWatermark macOS专用打包脚本
所有依赖打包到单个.app文件中
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def clean_build():
    """清理构建文件"""
    print("🧹 清理之前的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name, ignore_errors=True)
            print(f"  清理目录: {dir_name}")

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                      check=True, capture_output=True)
        print("✅ 依赖检查完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def build_app():
    """构建应用"""
    print("🚀 开始构建macOS应用...")
    
    spec_file = 'PhotoWatermark_mac_onefile.spec'
    if not Path(spec_file).exists():
        print(f"❌ 未找到配置文件: {spec_file}")
        return False
    
    start_time = time.time()
    
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', spec_file]
        print(f"🔧 执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        end_time = time.time()
        print(f"⏱️  构建耗时: {end_time - start_time:.1f} 秒")
        print("✅ 构建成功!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stdout:
            print("输出:", e.stdout)
        if e.stderr:
            print("错误:", e.stderr)
        return False

def verify_app():
    """验证应用"""
    print("🔍 验证构建结果...")
    
    app_path = Path('dist/PhotoWatermark.app')
    if app_path.exists():
        # 计算应用大小
        total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        
        print(f"✅ 应用路径: {app_path}")
        print(f"📊 应用大小: {size_mb:.1f} MB")
        
        # 检查可执行文件
        exe_path = app_path / 'Contents' / 'MacOS' / 'PhotoWatermark'
        if exe_path.exists():
            print(f"✅ 可执行文件: {exe_path}")
        else:
            print("❌ 可执行文件不存在")
            return False
        
        # 检查资源文件
        resources_path = app_path / 'Contents' / 'Resources'
        if resources_path.exists():
            resource_count = len(list(resources_path.rglob('*')))
            print(f"✅ 资源文件: {resource_count} 个")
        
        return True
    else:
        print("❌ 应用文件不存在")
        return False

def main():
    """主函数"""
    print("🍎 PhotoWatermark macOS 单文件打包工具")
    print("=" * 50)
    
    try:
        # 清理构建
        clean_build()
        
        # 检查依赖
        if not check_dependencies():
            return 1
        
        # 构建应用
        if not build_app():
            return 1
        
        # 验证应用
        if verify_app():
            print("\n🎉 macOS应用打包完成!")
            print("\n📋 使用说明:")
            print("1. 应用位置: dist/PhotoWatermark.app")
            print("2. 双击运行或拖拽到应用程序文件夹")
            print("3. 首次运行可能需要在系统偏好设置中允许")
            print("4. 所有依赖已打包在.app文件中")
            return 0
        else:
            print("\n❌ 应用验证失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断构建")
        return 1
    except Exception as e:
        print(f"\n❌ 构建失败: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
