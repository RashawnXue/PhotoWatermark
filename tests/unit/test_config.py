"""
配置管理模块测试
"""

import unittest
import json
import tempfile
import os
from src.core.config import Config, WatermarkConfig, Position, DateFormat


class TestConfig(unittest.TestCase):
    """配置管理测试类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = WatermarkConfig()
        
        self.assertIsNone(config.font_size)
        self.assertEqual(config.font_color, "white")
        self.assertEqual(config.font_alpha, 0.8)
        self.assertEqual(config.position, Position.BOTTOM_RIGHT)
        self.assertEqual(config.margin, 20)
        self.assertEqual(config.date_format, DateFormat.YYYY_MM_DD)
        self.assertEqual(config.output_format, "JPEG")
        self.assertEqual(config.output_quality, 95)
        self.assertFalse(config.recursive)
        self.assertFalse(config.preview_mode)
        self.assertFalse(config.verbose)
    
    def test_config_to_dict(self):
        """测试配置转字典"""
        config = WatermarkConfig(
            font_size=24,
            font_color="red",
            position=Position.TOP_LEFT,
            date_format=DateFormat.DD_MM_YYYY
        )
        
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict['font_size'], 24)
        self.assertEqual(config_dict['font_color'], "red")
        self.assertEqual(config_dict['position'], "top-left")
        self.assertEqual(config_dict['date_format'], "DD-MM-YYYY")
    
    def test_config_from_dict(self):
        """测试从字典创建配置"""
        data = {
            'font_size': 32,
            'font_color': "blue",
            'position': "center",
            'date_format': "MMM DD, YYYY"
        }
        
        config = WatermarkConfig.from_dict(data)
        
        self.assertEqual(config.font_size, 32)
        self.assertEqual(config.font_color, "blue")
        self.assertEqual(config.position, Position.CENTER)
        self.assertEqual(config.date_format, DateFormat.MMM_DD_YYYY)
    
    def test_save_and_load_config(self):
        """测试配置文件保存和加载"""
        original_config = WatermarkConfig(
            font_size=28,
            font_color="green",
            font_alpha=0.9,
            position=Position.TOP_RIGHT,
            margin=15
        )
        
        config_manager = Config(original_config)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config_manager.save_to_file(temp_path)
            
            # 加载配置
            new_config_manager = Config()
            new_config_manager.load_from_file(temp_path)
            
            # 验证配置
            loaded_config = new_config_manager.config
            self.assertEqual(loaded_config.font_size, 28)
            self.assertEqual(loaded_config.font_color, "green")
            self.assertEqual(loaded_config.font_alpha, 0.9)
            self.assertEqual(loaded_config.position, Position.TOP_RIGHT)
            self.assertEqual(loaded_config.margin, 15)
            
        finally:
            os.unlink(temp_path)
    
    def test_position_coordinates(self):
        """测试位置坐标计算"""
        config = Config()
        
        # 测试不同位置的坐标计算
        test_cases = [
            (Position.TOP_LEFT, 20, 20),
            (Position.CENTER, 140, 90),  # (300-20)//2, (200-20)//2
            (Position.BOTTOM_RIGHT, 260, 160),  # 300-20-20, 200-20-20
        ]
        
        for position, expected_x, expected_y in test_cases:
            config.config.position = position
            x, y = config.get_position_coordinates(300, 200, 20, 20)
            self.assertEqual(x, expected_x, f"Position {position.value} X coordinate")
            self.assertEqual(y, expected_y, f"Position {position.value} Y coordinate")
    
    def test_auto_font_size(self):
        """测试自动字体大小计算"""
        config = Config()
        
        # 测试自动计算
        config.config.font_size = None
        font_size = config.get_auto_font_size(1920, 1080)
        self.assertEqual(font_size, 36)  # min(1920, 1080) // 30 = 36
        
        # 测试手动设置
        config.config.font_size = 48
        font_size = config.get_auto_font_size(1920, 1080)
        self.assertEqual(font_size, 48)
        
        # 测试最小值限制
        font_size = config.get_auto_font_size(300, 200)
        config.config.font_size = None
        font_size = config.get_auto_font_size(300, 200)
        self.assertEqual(font_size, 16)  # 应该被限制到最小值16


if __name__ == '__main__':
    unittest.main()
