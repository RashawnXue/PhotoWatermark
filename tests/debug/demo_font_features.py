#!/usr/bin/env python3
"""
字体功能演示脚本

演示新增的中文字体支持和字体选择功能。
"""

import os
import sys
from PIL import Image

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from src.utils.font_manager import font_manager
from src.core.config import Config, WatermarkConfig, WatermarkType, TextWatermarkConfig, Position
from src.core.watermark import WatermarkProcessor


def demo_font_detection():
    """演示字体检测功能"""
    print("=== 字体检测功能演示 ===")
    
    # 获取系统字体统计
    all_fonts = font_manager.get_system_fonts()
    chinese_fonts = font_manager.get_chinese_fonts()
    recommended_fonts = font_manager.get_recommended_fonts()
    
    print(f"✅ 检测到系统字体: {len(all_fonts)} 个")
    print(f"✅ 支持中文字体: {len(chinese_fonts)} 个")
    print(f"✅ 推荐字体: {len(recommended_fonts)} 个")
    
    print("\n🎯 推荐的中文字体 (前5个):")
    chinese_recommended = [f for f in recommended_fonts if f.get('supports_chinese', False)]
    for i, font in enumerate(chinese_recommended[:5], 1):
        print(f"  {i}. {font['name']}")
    
    return chinese_recommended


def demo_chinese_watermark(fonts):
    """演示中文水印功能"""
    print("\n=== 中文水印功能演示 ===")
    
    if not fonts:
        print("❌ 没有找到中文字体，使用默认字体")
        selected_font = None
    else:
        selected_font = fonts[0]
        print(f"🎨 使用字体: {selected_font['name']}")
    
    # 创建演示图片
    demo_image = Image.new('RGB', (800, 600), color=(135, 206, 235))  # 天蓝色背景
    
    # 创建中文水印配置
    text_config = TextWatermarkConfig(
        text="中文水印演示\n📸 拍摄于 2024年9月28日\n支持多种字体样式",
        font_size=42,
        font_color="white",
        font_alpha=0.9,
        font_path=selected_font['path'] if selected_font else None,
        font_name=selected_font['name'] if selected_font else None,
        font_bold=True,
        shadow_enabled=True,
        shadow_color="black",
        shadow_offset_x=3,
        shadow_offset_y=3,
        stroke_enabled=True,
        stroke_color="navy",
        stroke_width=1
    )
    
    # 创建水印配置
    watermark_config = WatermarkConfig(
        watermark_type=WatermarkType.TEXT,
        position=Position.BOTTOM_RIGHT,
        text_watermark=text_config
    )
    
    # 处理水印
    config = Config(watermark_config)
    processor = WatermarkProcessor(config)
    
    try:
        result_image = processor.add_text_watermark(demo_image)
        output_path = "demo_chinese_watermark.jpg"
        result_image.save(output_path, "JPEG", quality=95)
        print(f"✅ 中文水印演示图片已保存: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 中文水印演示失败: {e}")
        return False


def demo_font_styles(fonts):
    """演示不同字体样式"""
    print("\n=== 字体样式演示 ===")
    
    if not fonts:
        print("❌ 没有中文字体可用于演示")
        return
    
    # 选择一个中文字体进行样式演示
    demo_font = fonts[0]
    print(f"🎨 演示字体: {demo_font['name']}")
    
    styles = [
        {"bold": False, "italic": False, "name": "常规", "color": "white"},
        {"bold": True, "italic": False, "name": "粗体", "color": "yellow"},
        {"bold": False, "italic": True, "name": "斜体", "color": "lightgreen"},
        {"bold": True, "italic": True, "name": "粗斜体", "color": "orange"}
    ]
    
    # 创建组合演示图片
    demo_image = Image.new('RGB', (800, 800), color=(70, 130, 180))  # 钢蓝色背景
    
    for i, style in enumerate(styles):
        y_offset = 150 + i * 120
        
        text_config = TextWatermarkConfig(
            text=f"{style['name']}样式演示\n字体: {demo_font['name']}",
            font_size=36,
            font_color=style['color'],
            font_alpha=0.9,
            font_path=demo_font['path'],
            font_name=demo_font['name'],
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
            custom_position=(100, y_offset),
            text_watermark=text_config
        )
        
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        try:
            demo_image = processor.add_text_watermark(demo_image)
            print(f"  ✅ {style['name']}样式")
        except Exception as e:
            print(f"  ❌ {style['name']}样式失败: {e}")
    
    try:
        output_path = "demo_font_styles.jpg"
        demo_image.save(output_path, "JPEG", quality=95)
        print(f"✅ 字体样式演示图片已保存: {output_path}")
    except Exception as e:
        print(f"❌ 保存字体样式演示失败: {e}")


def main():
    """主演示函数"""
    print("🎉 PhotoWatermark 字体功能演示")
    print("=" * 50)
    
    # 演示字体检测
    chinese_fonts = demo_font_detection()
    
    # 演示中文水印
    success = demo_chinese_watermark(chinese_fonts)
    
    if success:
        # 演示字体样式
        demo_font_styles(chinese_fonts)
    
    print("\n" + "=" * 50)
    print("🎊 演示完成！")
    print("\n📋 功能总结:")
    print("✅ 系统字体自动检测")
    print("✅ 中文字体智能识别")
    print("✅ 多种字体样式支持")
    print("✅ 阴影和描边效果")
    print("✅ 完美的中文渲染")
    
    if os.path.exists("demo_chinese_watermark.jpg"):
        print(f"\n📁 请查看生成的演示图片:")
        print(f"   • demo_chinese_watermark.jpg - 中文水印演示")
        if os.path.exists("demo_font_styles.jpg"):
            print(f"   • demo_font_styles.jpg - 字体样式演示")


if __name__ == "__main__":
    main()
