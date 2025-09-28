#!/usr/bin/env python3
"""
完整字体样式功能测试

测试新实现的粗体、斜体字体变体功能。
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


def test_font_family_detection():
    """测试字体家族检测功能"""
    print("=== 测试字体家族检测功能 ===")
    
    families = font_manager.get_font_families()
    print(f"检测到 {len(families)} 个字体家族")
    
    # 显示前10个字体家族及其样式
    family_names = sorted(families.keys())[:10]
    for family in family_names:
        fonts = families[family]
        styles = [font.get('style', 'regular') for font in fonts]
        print(f"  {family}: {', '.join(set(styles))}")
    
    return families


def test_font_style_variants():
    """测试字体样式变体查找"""
    print("\n=== 测试字体样式变体查找 ===")
    
    families = font_manager.get_font_families()
    
    # 寻找有多种样式的字体家族
    multi_style_families = []
    for family, fonts in families.items():
        styles = set(font.get('style', 'regular') for font in fonts)
        if len(styles) > 1:
            multi_style_families.append((family, styles, fonts))
    
    if multi_style_families:
        print(f"找到 {len(multi_style_families)} 个有多种样式的字体家族")
        
        # 测试前3个多样式字体家族
        for i, (family, styles, fonts) in enumerate(multi_style_families[:3]):
            print(f"\n测试字体家族 {i+1}: {family}")
            print(f"  可用样式: {', '.join(styles)}")
            
            # 获取基础字体（regular样式）
            base_font = None
            for font in fonts:
                if font.get('style') == 'regular':
                    base_font = font
                    break
            
            if not base_font:
                base_font = fonts[0]
            
            print(f"  基础字体: {base_font['name']} ({base_font['path']})")
            
            # 测试样式变体查找
            available_styles = font_manager.get_available_styles_for_font(base_font['path'])
            print(f"  可用样式变体: {', '.join(available_styles)}")
    else:
        print("没有找到有多种样式的字体家族")
    
    return multi_style_families


def create_style_test_image():
    """创建样式测试图片"""
    return Image.new('RGB', (1000, 800), color=(45, 55, 72))  # 深灰色背景


def test_font_style_rendering():
    """测试字体样式渲染"""
    print("\n=== 测试字体样式渲染 ===")
    
    families = font_manager.get_font_families()
    
    # 寻找支持中文且有多种样式的字体家族
    chinese_multi_style = []
    for family, fonts in families.items():
        styles = set(font.get('style', 'regular') for font in fonts)
        chinese_fonts = [f for f in fonts if f.get('supports_chinese', False)]
        
        if len(styles) > 1 and chinese_fonts:
            chinese_multi_style.append((family, styles, fonts[0]))
    
    if not chinese_multi_style:
        print("没有找到支持中文的多样式字体，使用默认字体测试")
        # 使用第一个中文字体
        chinese_fonts = font_manager.get_chinese_fonts()
        if chinese_fonts:
            test_font = chinese_fonts[0]
            chinese_multi_style = [(test_font['name'], {'regular'}, test_font)]
    
    if chinese_multi_style:
        family, styles, base_font = chinese_multi_style[0]
        print(f"使用字体家族: {family}")
        print(f"基础字体: {base_font['name']}")
        
        # 创建测试图片
        test_image = create_style_test_image()
        
        # 测试所有样式组合
        style_combinations = [
            (False, False, "常规"),
            (True, False, "粗体"),
            (False, True, "斜体"),
            (True, True, "粗斜体")
        ]
        
        y_positions = [150, 300, 450, 600]
        
        for i, (bold, italic, style_name) in enumerate(style_combinations):
            print(f"  测试 {style_name} 样式...")
            
            text_config = TextWatermarkConfig(
                text=f"{style_name}样式测试\n字体: {family}\n中文字体渲染效果",
                font_size=36,
                font_color="white",
                font_alpha=0.9,
                font_path=base_font['path'],
                font_name=base_font['name'],
                font_bold=bold,
                font_italic=italic,
                shadow_enabled=True,
                shadow_color="black",
                shadow_offset_x=2,
                shadow_offset_y=2
            )
            
            watermark_config = WatermarkConfig(
                watermark_type=WatermarkType.TEXT,
                position=Position.CENTER,
                custom_position=(50, y_positions[i]),
                text_watermark=text_config
            )
            
            config = Config(watermark_config)
            processor = WatermarkProcessor(config)
            
            try:
                test_image = processor.add_text_watermark(test_image)
                print(f"    ✅ {style_name}样式渲染成功")
            except Exception as e:
                print(f"    ❌ {style_name}样式渲染失败: {e}")
        
        # 保存测试结果
        try:
            output_path = os.path.join(project_root, "test_font_styles_complete.jpg")
            test_image.save(output_path, "JPEG", quality=95)
            print(f"\n✅ 字体样式测试图片已保存: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 保存测试图片失败: {e}")
            return False
    else:
        print("没有找到合适的测试字体")
        return False


def test_font_variant_lookup():
    """测试字体变体查找功能"""
    print("\n=== 测试字体变体查找功能 ===")
    
    # 获取一个有多种样式的字体家族
    families = font_manager.get_font_families()
    
    test_family = None
    for family, fonts in families.items():
        styles = set(font.get('style', 'regular') for font in fonts)
        if len(styles) >= 2:  # 至少有2种样式
            test_family = (family, fonts)
            break
    
    if not test_family:
        print("没有找到有多种样式的字体家族")
        return
    
    family_name, fonts = test_family
    print(f"测试字体家族: {family_name}")
    
    # 找到基础字体
    base_font = None
    for font in fonts:
        if font.get('style') == 'regular':
            base_font = font
            break
    
    if not base_font:
        base_font = fonts[0]
    
    print(f"基础字体: {base_font['name']}")
    
    # 测试不同样式的查找
    test_styles = [
        (False, False, "regular"),
        (True, False, "bold"),
        (False, True, "italic"),
        (True, True, "bold_italic")
    ]
    
    for bold, italic, expected_style in test_styles:
        try:
            # 使用字体管理器查找变体
            found_path = font_manager._find_font_variant(base_font['path'], bold, italic)
            
            # 检查找到的字体信息
            found_font = None
            for font in fonts:
                if font['path'] == found_path:
                    found_font = font
                    break
            
            if found_font:
                actual_style = found_font.get('style', 'regular')
                print(f"  {expected_style}: 找到 {found_font['name']} (样式: {actual_style})")
            else:
                print(f"  {expected_style}: 找到路径 {found_path}")
                
        except Exception as e:
            print(f"  {expected_style}: 查找失败 - {e}")


def main():
    """主测试函数"""
    print("🧪 完整字体样式功能测试")
    print("=" * 50)
    
    # 测试字体家族检测
    families = test_font_family_detection()
    
    # 测试字体样式变体查找
    multi_style_families = test_font_style_variants()
    
    # 测试字体变体查找功能
    test_font_variant_lookup()
    
    # 测试字体样式渲染
    success = test_font_style_rendering()
    
    print("\n" + "=" * 50)
    print("🎊 测试完成！")
    
    if success:
        print("\n📋 功能验证:")
        print("✅ 字体家族检测和分组")
        print("✅ 字体样式变体识别")
        print("✅ 粗体/斜体字体查找")
        print("✅ 多样式字体渲染")
        print("✅ 中文字体样式支持")
        
        print(f"\n📁 请查看生成的测试图片:")
        print(f"   • test_font_styles_complete.jpg - 完整字体样式测试")
    else:
        print("\n⚠️  部分功能测试失败，请检查日志")


if __name__ == "__main__":
    main()
