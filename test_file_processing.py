#!/usr/bin/env python3
"""
测试文件处理流程
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from photo_watermark.gui.file_manager import FileManager

def test_file_manager():
    """测试文件管理器"""
    fm = FileManager()
    
    # 测试图片文件检测
    test_files = [
        "test_images/photo1.jpg",
        "test_images/landscape.jpg", 
        "test_images/portrait.jpg",
        "test_images/nonexistent.jpg",
        "test_images/"  # 目录
    ]
    
    print("=== 测试文件管理器 ===")
    for file in test_files:
        if os.path.exists(file):
            if os.path.isfile(file):
                is_supported = fm.is_supported_image(file)
                print(f"文件 {file}: 支持={is_supported}")
            elif os.path.isdir(file):
                dir_files = fm.get_images_from_directory(file)
                print(f"目录 {file}: 找到{len(dir_files)}个图片文件")
                for df in dir_files[:3]:  # 只显示前3个
                    print(f"  - {os.path.basename(df)}")
        else:
            print(f"文件 {file}: 不存在")
    
    print("\n=== 测试文件路径处理 ===")
    test_paths = ["test_images/photo1.jpg", "test_images/"]
    all_files = fm.get_image_files_from_paths(test_paths)
    print(f"从路径 {test_paths} 获取到 {len(all_files)} 个图片文件:")
    for f in all_files[:5]:  # 只显示前5个
        print(f"  - {f}")

if __name__ == "__main__":
    test_file_manager()
