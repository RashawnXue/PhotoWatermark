#!/usr/bin/env python3
"""
PhotoWatermark 通用单文件打包脚本
自动检测平台并使用相应的单文件打包配置
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_platform():
    """获取当前平台"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'mac'
    elif system == 'windows':
        return 'win'
    else:
        return 'linux'

def get_spec_file(platform_type):
    """获取对应平台的spec文件"""
    spec_files = {
        'mac': 'PhotoWatermark_mac_onefile.spec',
        'win': 'PhotoWatermark_onefile.spec',
        'linux': 'PhotoWatermark_onefile.spec'  # Linux使用Windows配置
    }
    return spec_files.get(platform_type)

def main():
    """主函数"""
    current_platform = get_platform()
    spec_file = get_spec_file(current_platform)
    
    print(f"🎯 检测到平台: {current_platform}")
    print(f"📄 使用配置文件: {spec_file}")
    
    if not Path(spec_file).exists():
        print(f"❌ 配置文件不存在: {spec_file}")
        return 1
    
    # 根据平台调用相应的构建脚本
    if current_platform == 'mac':
        return subprocess.call([sys.executable, 'build_mac.py'])
    elif current_platform == 'win':
        return subprocess.call([sys.executable, 'build_windows.py'])
    else:
        # Linux使用PyInstaller直接打包
        print("🐧 Linux平台直接使用PyInstaller...")
        return subprocess.call([sys.executable, '-m', 'PyInstaller', spec_file])

if __name__ == '__main__':
    sys.exit(main())
