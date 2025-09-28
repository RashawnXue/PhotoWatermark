#!/usr/bin/env python3
"""
测试中文字体渲染功能

用于验证字体管理器和中文字体水印是否正常工作。
"""

import os
import sys
from PIL import Image, ImageDraw

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.utils.font_manager import font_manager
from src.core.config import Config, WatermarkConfig, WatermarkType, TextWatermarkConfig
from src.core.watermark import WatermarkProcessor


def test_font_detection():
    """测试字体检测功能"""
    print("=== 测试字体检测功能 ===")
    
    # 获取系统字体
    fonts = font_manager.get_system_fonts()
    print(f"检测到 {len(fonts)} 个系统字体")
    
    # 获取中文字体
    chinese_fonts = font_manager.get_chinese_fonts()
    print(f"检测到 {len(chinese_fonts)} 个中文字体")
    
    if chinese_fonts:
        print("支持中文的字体:")
        for font in chinese_fonts[:5]:  # 显示前5个
            print(f"  - {font['name']}: {font['path']}")
    
    # 获取推荐字体
    recommended = font_manager.get_recommended_fonts()
    print(f"推荐字体 {len(recommended)} 个")
    
    if recommended:
        print("推荐字体列表:")
        for font in recommended[:10]:  # 显示前10个
            chinese_mark = " [中文]" if font.get('supports_chinese', False) else ""
            print(f"  - {font['name']}{chinese_mark}: {font['path']}")


def test_chinese_text_rendering():
    """测试中文文本渲染"""
    print("\n=== 测试中文文本渲染 ===")
    
    # 创建测试图片
    test_image = Image.new('RGB', (800, 600), color='white')
    
    # 创建文本水印配置
    text_config = TextWatermarkConfig(
        text="中文水印测试\n这是第二行\n📸 2024-01-01 12:00:00",
        font_size=48,
        font_color="black",
        font_alpha=0.8,
        font_path=None,  # 使用默认字体
        font_bold=False,
        font_italic=False,
        shadow_enabled=True,
        shadow_color="gray",
        shadow_offset_x=2,
        shadow_offset_y=2,
        stroke_enabled=False
    )
    
    # 创建水印配置
    watermark_config = WatermarkConfig(
        watermark_type=WatermarkType.TEXT,
        text_watermark=text_config
    )
    
    # 创建配置和处理器
    config = Config(watermark_config)
    processor = WatermarkProcessor(config)
    
    try:
        # 添加水印
        result_image = processor.add_text_watermark(test_image)
        
        # 保存测试结果
        output_path = os.path.join(project_root, "test_chinese_watermark.jpg")
        result_image.save(output_path, "JPEG", quality=95)
        print(f"中文水印测试图片已保存: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"中文文本渲染测试失败: {e}")
        return False


def test_different_fonts():
    """测试不同字体的渲染效果"""
    print("\n=== 测试不同字体渲染 ===")
    
    chinese_fonts = font_manager.get_chinese_fonts()
    if not chinese_fonts:
        print("没有找到中文字体，跳过测试")
        return
    
    # 测试前3个中文字体
    test_fonts = chinese_fonts[:3]
    
    for i, font_info in enumerate(test_fonts):
        print(f"测试字体: {font_info['name']}")
        
        # 创建测试图片
        test_image = Image.new('RGB', (600, 200), color='white')
        
        # 创建文本水印配置
        text_config = TextWatermarkConfig(
            text=f"字体测试: {font_info['name']}\n中文字体渲染效果",
            font_size=36,
            font_color="navy",
            font_alpha=0.9,
            font_path=font_info['path'],
            font_name=font_info['name']
        )
        
        # 创建水印配置
        watermark_config = WatermarkConfig(
            watermark_type=WatermarkType.TEXT,
            text_watermark=text_config
        )
        
        # 创建配置和处理器
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        try:
            # 添加水印
            result_image = processor.add_text_watermark(test_image)
            
            # 保存测试结果
            safe_name = font_info['name'].replace('/', '_').replace(' ', '_')
            output_path = os.path.join(project_root, f"test_font_{i+1}_{safe_name}.jpg")
            result_image.save(output_path, "JPEG", quality=95)
            print(f"  保存测试图片: {output_path}")
            
        except Exception as e:
            print(f"  字体 {font_info['name']} 测试失败: {e}")


def main():
    """主测试函数"""
    print("开始测试中文字体功能...")
    
    # 测试字体检测
    test_font_detection()
    
    # 测试中文文本渲染
    success = test_chinese_text_rendering()
    
    if success:
        # 测试不同字体
        test_different_fonts()
    
    print("\n测试完成！")


if __name__ == "__main__":
    main()
