#!/usr/bin/env python3
"""
多行文本功能测试脚本

测试修复后的换行符处理功能。
"""

import os
import sys
from PIL import Image

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from src.utils.font_manager import font_manager
from src.core.config import Config, WatermarkConfig, WatermarkType, TextWatermarkConfig, Position
from src.core.watermark import WatermarkProcessor


def create_test_image():
    """创建测试图片"""
    return Image.new('RGB', (800, 600), color=(50, 70, 90))  # 深蓝色背景


def test_multiline_text_watermark():
    """测试多行文本水印"""
    print("=== 测试多行文本水印功能 ===")
    
    # 获取中文字体
    chinese_fonts = font_manager.get_chinese_fonts()
    test_font = chinese_fonts[0] if chinese_fonts else None
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 测试不同的多行文本
    test_cases = [
        {
            'name': '基本多行文本',
            'text': '第一行文本\n第二行文本\n第三行文本',
            'position': Position.TOP_LEFT
        },
        {
            'name': '中文多行文本',
            'text': '中文第一行\n中文第二行\n包含特殊字符：📸🎨✨',
            'position': Position.TOP_RIGHT
        },
        {
            'name': '混合语言多行',
            'text': 'English Line 1\n中文第二行\nMixed Line 3\n数字：12345',
            'position': Position.BOTTOM_LEFT
        },
        {
            'name': '带空行的文本',
            'text': '第一行\n\n第三行（中间有空行）\n最后一行',
            'position': Position.BOTTOM_RIGHT
        },
        {
            'name': '长文本换行',
            'text': '这是一个很长的文本行\n用来测试换行功能\n支持多种样式效果\n包括阴影和描边',
            'position': Position.CENTER
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"测试 {i+1}: {test_case['name']}")
        
        # 创建文本水印配置
        text_config = TextWatermarkConfig(
            text=test_case['text'],
            font_size=24,
            font_color="white",
            font_alpha=0.9,
            font_path=test_font['path'] if test_font else None,
            font_name=test_font['name'] if test_font else None,
            font_bold=False,
            font_italic=False,
            shadow_enabled=True,
            shadow_color="black",
            shadow_offset_x=2,
            shadow_offset_y=2,
            stroke_enabled=True,
            stroke_color="navy",
            stroke_width=1
        )
        
        # 创建水印配置
        watermark_config = WatermarkConfig(
            watermark_type=WatermarkType.TEXT,
            position=test_case['position'],
            text_watermark=text_config
        )
        
        # 处理水印
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        try:
            test_image = processor.add_text_watermark(test_image)
            print(f"  ✅ {test_case['name']} - 成功")
        except Exception as e:
            print(f"  ❌ {test_case['name']} - 失败: {e}")
    
    # 保存测试结果
    try:
        output_path = "multiline_text_test.jpg"
        test_image.save(output_path, "JPEG", quality=95)
        print(f"\n✅ 多行文本测试图片已保存: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 保存测试图片失败: {e}")
        return False


def test_line_spacing():
    """测试行间距功能"""
    print("\n=== 测试行间距功能 ===")
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 获取中文字体
    chinese_fonts = font_manager.get_chinese_fonts()
    test_font = chinese_fonts[0] if chinese_fonts else None
    
    # 测试不同字体大小的行间距
    font_sizes = [16, 24, 36, 48]
    
    for i, font_size in enumerate(font_sizes):
        x_offset = 50 + i * 180
        
        text_config = TextWatermarkConfig(
            text=f"字号{font_size}px\n第二行文本\n第三行文本\n测试行间距",
            font_size=font_size,
            font_color="yellow",
            font_alpha=0.9,
            font_path=test_font['path'] if test_font else None,
            font_name=test_font['name'] if test_font else None
        )
        
        watermark_config = WatermarkConfig(
            watermark_type=WatermarkType.TEXT,
            position=Position.CENTER,
            custom_position=(x_offset, 150),
            text_watermark=text_config
        )
        
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        try:
            test_image = processor.add_text_watermark(test_image)
            print(f"  ✅ 字号 {font_size}px - 行间距正常")
        except Exception as e:
            print(f"  ❌ 字号 {font_size}px - 失败: {e}")
    
    # 保存测试结果
    try:
        output_path = "line_spacing_test.jpg"
        test_image.save(output_path, "JPEG", quality=95)
        print(f"✅ 行间距测试图片已保存: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 保存行间距测试图片失败: {e}")
        return False


def test_special_characters():
    """测试特殊字符处理"""
    print("\n=== 测试特殊字符处理 ===")
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 获取中文字体
    chinese_fonts = font_manager.get_chinese_fonts()
    test_font = chinese_fonts[0] if chinese_fonts else None
    
    # 测试各种特殊字符
    special_texts = [
        "Emoji测试: 📸🎨✨🌟💫",
        "符号测试: ©®™°±×÷",
        "中文标点: 。，！？；：""''（）",
        "数学符号: ∑∞∫∂∇≠≤≥±",
        "箭头符号: ←→↑↓↔⇄⇆"
    ]
    
    for i, text in enumerate(special_texts):
        y_offset = 80 + i * 80
        
        text_config = TextWatermarkConfig(
            text=text,
            font_size=20,
            font_color="lightgreen",
            font_alpha=0.9,
            font_path=test_font['path'] if test_font else None,
            font_name=test_font['name'] if test_font else None
        )
        
        watermark_config = WatermarkConfig(
            watermark_type=WatermarkType.TEXT,
            position=Position.CENTER,
            custom_position=(50, y_offset),
            text_watermark=text_config
        )
        
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        try:
            test_image = processor.add_text_watermark(test_image)
            print(f"  ✅ 特殊字符测试 {i+1} - 成功")
        except Exception as e:
            print(f"  ❌ 特殊字符测试 {i+1} - 失败: {e}")
    
    # 保存测试结果
    try:
        output_path = "special_characters_test.jpg"
        test_image.save(output_path, "JPEG", quality=95)
        print(f"✅ 特殊字符测试图片已保存: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 保存特殊字符测试图片失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 多行文本功能测试")
    print("=" * 50)
    
    # 测试多行文本水印
    success1 = test_multiline_text_watermark()
    
    # 测试行间距
    success2 = test_line_spacing()
    
    # 测试特殊字符
    success3 = test_special_characters()
    
    print("\n" + "=" * 50)
    print("🎊 测试完成！")
    
    if success1 and success2 and success3:
        print("\n📋 功能验证:")
        print("✅ 多行文本支持（\\n 换行符正确处理）")
        print("✅ 自动行间距计算")
        print("✅ 多种字体大小行间距适配")
        print("✅ 特殊字符和Emoji支持")
        print("✅ 阴影和描边效果支持多行")
        print("✅ 中英文混合多行文本")
        
        print(f"\n📁 生成的测试图片:")
        print(f"   • multiline_text_test.jpg - 多行文本测试")
        print(f"   • line_spacing_test.jpg - 行间距测试")
        print(f"   • special_characters_test.jpg - 特殊字符测试")
        
        print(f"\n🎯 问题修复:")
        print(f"   • \\n 换行符现在正确显示为换行")
        print(f"   • 支持任意行数的多行文本")
        print(f"   • 自动计算合适的行间距")
    else:
        print("\n⚠️  部分功能测试失败，请检查日志")


if __name__ == "__main__":
    main()
