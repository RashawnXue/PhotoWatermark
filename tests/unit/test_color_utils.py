"""
颜色工具函数测试
"""

import unittest
from src.utils.color_utils import (
    parse_color, rgb_to_hex, get_contrast_color, 
    blend_colors, adjust_brightness, get_available_colors
)


class TestColorUtils(unittest.TestCase):
    """颜色工具测试类"""
    
    def test_parse_color_names(self):
        """测试颜色名称解析"""
        test_cases = [
            ("white", (255, 255, 255)),
            ("black", (0, 0, 0)),
            ("red", (255, 0, 0)),
            ("green", (0, 255, 0)),
            ("blue", (0, 0, 255)),
            ("gray", (128, 128, 128)),
            ("grey", (128, 128, 128)),  # 别名
        ]
        
        for color_name, expected_rgb in test_cases:
            with self.subTest(color=color_name):
                result = parse_color(color_name)
                self.assertEqual(result, expected_rgb)
    
    def test_parse_hex_colors(self):
        """测试十六进制颜色解析"""
        test_cases = [
            ("#FF0000", (255, 0, 0)),
            ("#00FF00", (0, 255, 0)),
            ("#0000FF", (0, 0, 255)),
            ("FF0000", (255, 0, 0)),  # 无#前缀
            ("#ff0000", (255, 0, 0)),  # 小写
            ("ff0000", (255, 0, 0)),   # 小写无#
        ]
        
        for hex_color, expected_rgb in test_cases:
            with self.subTest(color=hex_color):
                result = parse_color(hex_color)
                self.assertEqual(result, expected_rgb)
    
    def test_parse_rgb_colors(self):
        """测试RGB格式颜色解析"""
        test_cases = [
            ("rgb(255,0,0)", (255, 0, 0)),
            ("rgb(0, 255, 0)", (0, 255, 0)),
            ("RGB(0, 0, 255)", (0, 0, 255)),
            ("255,0,0", (255, 0, 0)),
            ("0, 255, 0", (0, 255, 0)),
        ]
        
        for rgb_str, expected_rgb in test_cases:
            with self.subTest(color=rgb_str):
                result = parse_color(rgb_str)
                self.assertEqual(result, expected_rgb)
    
    def test_parse_invalid_colors(self):
        """测试无效颜色解析"""
        invalid_colors = [
            "invalid_color",
            "#GG0000",  # 无效十六进制
            "rgb(256,0,0)",  # 超出范围
            "300,0,0",  # 超出范围
            "",
        ]
        
        for invalid_color in invalid_colors:
            with self.subTest(color=invalid_color):
                result = parse_color(invalid_color)
                self.assertIsNone(result)
    
    def test_rgb_to_hex(self):
        """测试RGB转十六进制"""
        test_cases = [
            ((255, 0, 0), "#ff0000"),
            ((0, 255, 0), "#00ff00"),
            ((0, 0, 255), "#0000ff"),
            ((128, 128, 128), "#808080"),
            ((255, 255, 255), "#ffffff"),
            ((0, 0, 0), "#000000"),
        ]
        
        for rgb, expected_hex in test_cases:
            with self.subTest(rgb=rgb):
                result = rgb_to_hex(rgb)
                self.assertEqual(result, expected_hex)
    
    def test_get_contrast_color(self):
        """测试对比色获取"""
        test_cases = [
            ((255, 255, 255), (0, 0, 0)),    # 白色 -> 黑色
            ((0, 0, 0), (255, 255, 255)),    # 黑色 -> 白色
            ((255, 0, 0), (255, 255, 255)),  # 红色 -> 白色 (亮度76.245 < 128)
            ((0, 0, 128), (255, 255, 255)),  # 深蓝 -> 白色
        ]
        
        for rgb, expected_contrast in test_cases:
            with self.subTest(rgb=rgb):
                result = get_contrast_color(rgb)
                self.assertEqual(result, expected_contrast)
    
    def test_blend_colors(self):
        """测试颜色混合"""
        color1 = (255, 0, 0)  # 红色
        color2 = (0, 0, 255)  # 蓝色
        
        # 测试不同混合比例
        result_0 = blend_colors(color1, color2, 0.0)
        self.assertEqual(result_0, color1)
        
        result_1 = blend_colors(color1, color2, 1.0)
        self.assertEqual(result_1, color2)
        
        result_half = blend_colors(color1, color2, 0.5)
        self.assertEqual(result_half, (127, 0, 127))  # 中间值
    
    def test_adjust_brightness(self):
        """测试亮度调整"""
        color = (128, 128, 128)  # 灰色
        
        # 变亮
        brighter = adjust_brightness(color, 1.5)
        self.assertEqual(brighter, (192, 192, 192))
        
        # 变暗
        darker = adjust_brightness(color, 0.5)
        self.assertEqual(darker, (64, 64, 64))
        
        # 测试边界值
        white = (255, 255, 255)
        over_bright = adjust_brightness(white, 2.0)
        self.assertEqual(over_bright, (255, 255, 255))  # 不能超过255
        
        black = (0, 0, 0)
        over_dark = adjust_brightness(black, -1.0)
        self.assertEqual(over_dark, (0, 0, 0))  # 不能低于0
    
    def test_get_available_colors(self):
        """测试获取可用颜色"""
        colors = get_available_colors()
        
        self.assertIsInstance(colors, dict)
        self.assertIn('white', colors)
        self.assertIn('black', colors)
        self.assertIn('red', colors)
        
        # 验证颜色值格式
        for name, rgb in colors.items():
            self.assertIsInstance(rgb, tuple)
            self.assertEqual(len(rgb), 3)
            for value in rgb:
                self.assertIsInstance(value, int)
                self.assertTrue(0 <= value <= 255)


if __name__ == '__main__':
    unittest.main()
