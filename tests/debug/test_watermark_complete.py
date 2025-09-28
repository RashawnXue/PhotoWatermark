#!/usr/bin/env python3
"""
完整水印功能测试

测试所有类型的水印功能，包括中文字体。
"""

import os
import sys
from PIL import Image

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.utils.font_manager import font_manager
from src.core.config import Config, WatermarkConfig, WatermarkType, TextWatermarkConfig, Position
from src.core.watermark import WatermarkProcessor


def create_test_image():
    """创建测试图片"""
    # 创建一个简单的渐变背景测试图
    width, height = 800, 600
    image = Image.new('RGB', (width, height))
    pixels = image.load()
    
    for y in range(height):
        for x in range(width):
            # 创建蓝色到白色的渐变
            blue_value = int(255 * (1 - y / height))
            pixels[x, y] = (blue_value, blue_value + 20, 255)
    
    return image


def test_chinese_text_watermark():
    """测试中文文本水印"""
    print("=== 测试中文文本水印 ===")
    
    # 获取中文字体
    chinese_fonts = font_manager.get_chinese_fonts()
    test_font = None
    
    if chinese_fonts:
        # 寻找真正的中文字体
        for font in chinese_fonts:
            if any(indicator in font['name'].lower() for indicator in ['苹方', '宋体', '黑体', '楷体', '华文']):
                test_font = font
                break
        
        if not test_font:
            test_font = chinese_fonts[0]
    
    print(f"使用字体: {test_font['name'] if test_font else '默认字体'}")
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 创建文本水印配置
    text_config = TextWatermarkConfig(
        text="中文水印测试\n📸 2024年1月1日\n支持多行文本",
        font_size=48,
        font_color="white",
        font_alpha=0.9,
        font_path=test_font['path'] if test_font else None,
        font_name=test_font['name'] if test_font else None,
        font_bold=True,
        shadow_enabled=True,
        shadow_color="black",
        shadow_offset_x=3,
        shadow_offset_y=3,
        stroke_enabled=True,
        stroke_color="navy",
        stroke_width=2
    )
    
    # 测试不同位置
    positions = [
        (Position.TOP_LEFT, "左上角"),
        (Position.TOP_RIGHT, "右上角"),
        (Position.BOTTOM_LEFT, "左下角"),
        (Position.BOTTOM_RIGHT, "右下角"),
        (Position.CENTER, "居中")
    ]
    
    for position, name in positions:
        # 创建水印配置
        watermark_config = WatermarkConfig(
            watermark_type=WatermarkType.TEXT,
            position=position,
            text_watermark=text_config
        )
        
        # 创建配置和处理器
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        try:
            # 添加水印
            result_image = processor.add_text_watermark(test_image)
            
            # 保存测试结果
            output_path = os.path.join(project_root, f"test_chinese_watermark_{name}.jpg")
            result_image.save(output_path, "JPEG", quality=95)
            print(f"  {name}水印测试图片已保存: {output_path}")
            
        except Exception as e:
            print(f"  {name}水印测试失败: {e}")


def test_different_font_styles():
    """测试不同字体样式"""
    print("\n=== 测试不同字体样式 ===")
    
    # 获取推荐字体
    fonts = font_manager.get_recommended_fonts()
    chinese_fonts = [f for f in fonts if f.get('supports_chinese', False)]
    
    if not chinese_fonts:
        print("没有找到中文字体")
        return
    
    # 选择前3个中文字体进行测试
    test_fonts = chinese_fonts[:3]
    
    for i, font_info in enumerate(test_fonts):
        if any(indicator in font_info['name'].lower() for indicator in ['苹方', '宋体', '黑体', '楷体', '华文']):
            print(f"测试字体 {i+1}: {font_info['name']}")
            
            # 创建测试图片
            test_image = create_test_image()
            
            # 测试不同样式
            styles = [
                {"bold": False, "italic": False, "name": "常规"},
                {"bold": True, "italic": False, "name": "粗体"},
                {"bold": False, "italic": True, "name": "斜体"},
                {"bold": True, "italic": True, "name": "粗斜体"}
            ]
            
            for style in styles:
                text_config = TextWatermarkConfig(
                    text=f"字体测试: {font_info['name']}\n样式: {style['name']}\n中文字体渲染",
                    font_size=36,
                    font_color="white",
                    font_alpha=0.9,
                    font_path=font_info['path'],
                    font_name=font_info['name'],
                    font_bold=style['bold'],
                    font_italic=style['italic'],
                    shadow_enabled=True,
                    shadow_color="black",
                    shadow_offset_x=2,
                    shadow_offset_y=2
                )
                
                watermark_config = WatermarkConfig(
                    watermark_type=WatermarkType.TEXT,
                    position=Position.CENTER,
                    text_watermark=text_config
                )
                
                config = Config(watermark_config)
                processor = WatermarkProcessor(config)
                
                try:
                    result_image = processor.add_text_watermark(test_image)
                    
                    safe_name = font_info['name'].replace('/', '_').replace(' ', '_')
                    style_name = style['name'].replace('/', '_')
                    output_path = os.path.join(project_root, f"test_font_style_{i+1}_{safe_name}_{style_name}.jpg")
                    result_image.save(output_path, "JPEG", quality=95)
                    print(f"  保存 {style['name']} 样式: {output_path}")
                    
                except Exception as e:
                    print(f"  {style['name']} 样式测试失败: {e}")


def main():
    """主测试函数"""
    print("开始完整水印功能测试...")
    
    # 测试中文文本水印
    test_chinese_text_watermark()
    
    # 测试不同字体样式
    test_different_font_styles()
    
    print("\n完整测试完成！")
    print("请检查生成的测试图片，验证中文字体是否正确显示。")


if __name__ == "__main__":
    main()
