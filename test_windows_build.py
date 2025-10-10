#!/usr/bin/env python3
"""
测试Windows打包过程的脚本
在macOS上模拟Windows打包流程
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

def clean_previous_builds():
    """清理之前的构建"""
    print("🧹 清理之前的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['version_info.txt']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name, ignore_errors=True)
            print(f"  清理目录: {dir_name}")
    
    for file_name in files_to_clean:
        if Path(file_name).exists():
            Path(file_name).unlink()
            print(f"  清理文件: {file_name}")

def create_version_info():
    """创建版本信息文件"""
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

def run_pyinstaller():
    """运行PyInstaller"""
    print("🚀 运行PyInstaller...")
    
    start_time = time.time()
    
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', 'PhotoWatermark_windows.spec']
        print(f"🔧 执行命令: {' '.join(cmd)}")
        
        # 运行PyInstaller
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            universal_newlines=True
        )
        
        # 实时输出
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"  {output.strip()}")
                output_lines.append(output.strip())
        
        return_code = process.poll()
        end_time = time.time()
        
        print(f"\n⏱️  构建耗时: {end_time - start_time:.1f} 秒")
        
        if return_code == 0:
            print("✅ PyInstaller构建成功!")
            return True, output_lines
        else:
            print(f"❌ PyInstaller构建失败，返回码: {return_code}")
            return False, output_lines
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False, []

def verify_build_output():
    """验证构建输出"""
    print("\n🔍 验证构建输出...")
    
    dist_dir = Path('dist/PhotoWatermark')
    if not dist_dir.exists():
        print("❌ 构建目录不存在")
        return False
    
    # 检查主要文件
    exe_file = dist_dir / 'PhotoWatermark.exe'
    if exe_file.exists():
        size = exe_file.stat().st_size
        size_mb = size / (1024 * 1024)
        print(f"✅ 主程序: PhotoWatermark.exe ({size_mb:.1f} MB)")
    else:
        print("❌ 主程序文件不存在")
        return False
    
    # 检查重要的DLL和文件
    important_patterns = [
        '*python*.dll',
        '*tkinter*',
        '*PIL*',
        '_internal',
    ]
    
    found_files = []
    for pattern in important_patterns:
        matches = list(dist_dir.rglob(pattern))
        if matches:
            print(f"✅ 找到 {pattern}: {len(matches)} 个文件")
            found_files.extend(matches)
        else:
            print(f"⚠️  未找到 {pattern}")
    
    # 统计文件
    all_files = list(dist_dir.rglob('*'))
    file_count = len([f for f in all_files if f.is_file()])
    dir_count = len([f for f in all_files if f.is_dir()])
    
    print(f"📊 总计: {file_count} 个文件, {dir_count} 个目录")
    
    # 计算总大小
    total_size = sum(f.stat().st_size for f in all_files if f.is_file())
    total_size_mb = total_size / (1024 * 1024)
    print(f"💾 总大小: {total_size_mb:.1f} MB")
    
    return True

def create_test_files():
    """创建测试用的辅助文件"""
    print("\n📝 创建测试辅助文件...")
    
    dist_dir = Path('dist/PhotoWatermark')
    if not dist_dir.exists():
        return
    
    # 创建启动脚本
    startup_script = dist_dir / 'start_photowatermark.bat'
    with open(startup_script, 'w', encoding='gbk') as f:
        f.write('@echo off\n')
        f.write('echo Starting PhotoWatermark...\n')
        f.write('cd /d "%~dp0"\n')
        f.write('PhotoWatermark.exe\n')
        f.write('pause\n')
    
    # 创建测试说明
    test_readme = dist_dir / 'TEST_README.txt'
    with open(test_readme, 'w', encoding='utf-8') as f:
        f.write('''PhotoWatermark Windows 构建测试版本
=====================================

这是一个测试构建版本，用于验证Windows打包配置。

测试步骤:
1. 双击 PhotoWatermark.exe 启动程序
2. 或双击 start_photowatermark.bat（显示启动信息）
3. 测试以下功能:
   - 程序正常启动
   - GUI界面显示
   - 文件导入功能
   - 水印添加功能
   - 图片导出功能

如果遇到问题:
- 检查是否缺少Visual C++ Redistributable
- 查看控制台错误信息
- 确保有足够的权限和磁盘空间

构建信息:
- 构建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
- 构建平台: {sys.platform}
- Python版本: {sys.version}
'''.format(time=time, sys=sys))
    
    print("✅ 测试辅助文件创建完成")

def main():
    """主函数"""
    print("🧪 PhotoWatermark Windows 构建测试")
    print("=" * 50)
    
    try:
        # 清理之前的构建
        clean_previous_builds()
        
        # 创建版本信息
        create_version_info()
        
        # 运行PyInstaller
        success, output = run_pyinstaller()
        
        if success:
            # 验证构建输出
            if verify_build_output():
                # 创建测试文件
                create_test_files()
                
                print("\n🎉 Windows构建测试完成!")
                print("\n📋 测试结果:")
                print("✅ PyInstaller构建成功")
                print("✅ 输出文件验证通过")
                print("✅ 测试文件创建完成")
                
                print("\n🚀 下一步:")
                print("1. 将 dist/PhotoWatermark 目录复制到Windows机器")
                print("2. 在Windows上测试 PhotoWatermark.exe")
                print("3. 验证所有功能是否正常工作")
                print("4. 如有问题，检查构建日志和错误信息")
                
                return 0
            else:
                print("\n❌ 构建输出验证失败")
                return 1
        else:
            print("\n❌ PyInstaller构建失败")
            print("\n🔍 可能的解决方案:")
            print("1. 检查依赖是否完整安装")
            print("2. 查看上方的错误信息")
            print("3. 尝试在虚拟环境中构建")
            print("4. 检查spec文件配置")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断构建")
        return 1
    except Exception as e:
        print(f"\n❌ 构建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
