#!/usr/bin/env python3
"""
测试文件处理流程
"""

import sys
import os
import unittest

# 添加项目根路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.gui.file_manager import FileManager


class TestFileProcessing(unittest.TestCase):
    """文件处理集成测试"""
    
    def setUp(self):
        """测试设置"""
        self.file_manager = FileManager()
        # 使用fixtures中的测试图片
        self.test_images_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'fixtures', 'test_images'
        )
    
    def test_file_manager(self):
        """测试文件管理器基本功能"""
        # 测试图片文件检测
        test_files = [
            os.path.join(self.test_images_dir, "photo1.jpg"),
            os.path.join(self.test_images_dir, "landscape.jpg"), 
            os.path.join(self.test_images_dir, "portrait.jpg"),
        ]
        
        for file in test_files:
            if os.path.exists(file):
                is_supported = self.file_manager.is_supported_image(file)
                self.assertTrue(is_supported, f"图片文件 {file} 应该被支持")
    
    def test_directory_processing(self):
        """测试目录处理功能"""
        if os.path.exists(self.test_images_dir):
            dir_files = self.file_manager.get_images_from_directory(self.test_images_dir)
            self.assertGreater(len(dir_files), 0, "测试图片目录应该包含图片文件")
    
    def test_file_path_processing(self):
        """测试文件路径处理"""
        if os.path.exists(self.test_images_dir):
            test_paths = [self.test_images_dir]
            all_files = self.file_manager.get_image_files_from_paths(test_paths)
            self.assertGreater(len(all_files), 0, "应该能从路径获取到图片文件")


if __name__ == "__main__":
    unittest.main()
