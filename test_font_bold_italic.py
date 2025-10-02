#!/usr/bin/env python3
"""
粗体斜体功能测试脚本
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from PIL import Image, ImageDraw

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import Config, WatermarkConfig, WatermarkType, TextWatermarkConfig
from core.watermark import WatermarkProcessor
from utils.font_manager import font_manager

def test_font_bold_italic():
    """测试粗体斜体功能"""
    root = tk.Tk()
    root.title("粗体斜体功能测试")
    root.geometry("800x700")
    
    # 创建测试界面
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    ttk.Label(main_frame, text="粗体斜体功能测试", 
              font=('Arial', 16, 'bold')).pack(pady=(0, 20))
    
    # 测试参数
    test_text = "测试文本 Test Bold Italic"
    test_font_size = 32
    
    # 获取字体列表
    fonts = font_manager.get_recommended_fonts()
    test_font = fonts[0] if fonts else None
    
    if test_font:
        ttk.Label(main_frame, text=f"测试字体: {test_font['name']}", 
                  font=('Arial', 12)).pack(pady=(0, 10))
    
    # 创建测试图像
    test_image = Image.new('RGB', (600, 400), 'white')
    
    # 测试样式组合
    styles = [
        (False, False, "普通"),
        (True, False, "粗体"),
        (False, True, "斜体"),
        (True, True, "粗体斜体")
    ]
    
    results_frame = ttk.Frame(main_frame)
    results_frame.pack(fill='both', expand=True)
    
    for i, (bold, italic, style_name) in enumerate(styles):
        # 创建配置
        text_config = TextWatermarkConfig(
            text=f"{style_name}: {test_text}",
            font_size=test_font_size,
            font_color="black",
            font_alpha=1.0,
            font_path=test_font['path'] if test_font else None,
            font_name=test_font['name'] if test_font else None,
            font_bold=bold,
            font_italic=italic
        )
        
        watermark_config = WatermarkConfig(
            watermark_type=WatermarkType.TEXT,
            text_watermark=text_config
        )
        
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        # 处理图像
        try:
            result_image = processor.add_text_watermark(test_image.copy())
            
            # 显示结果信息
            result_frame = ttk.Frame(results_frame)
            result_frame.pack(fill='x', pady=5)
            
            status_text = f"✓ {style_name}: 成功生成"
            ttk.Label(result_frame, text=status_text, 
                      foreground='green', font=('Arial', 10)).pack(anchor='w')
            
            # 检查图像是否有变化（简单检查）
            if result_image.size == test_image.size:
                ttk.Label(result_frame, text="  - 图像尺寸正确", 
                          foreground='gray', font=('Arial', 9)).pack(anchor='w')
            
        except Exception as e:
            result_frame = ttk.Frame(results_frame)
            result_frame.pack(fill='x', pady=5)
            
            status_text = f"✗ {style_name}: 失败 - {str(e)}"
            ttk.Label(result_frame, text=status_text, 
                      foreground='red', font=('Arial', 10)).pack(anchor='w')
    
    # 字体管理器测试
    ttk.Separator(results_frame, orient='horizontal').pack(fill='x', pady=20)
    
    ttk.Label(results_frame, text="字体管理器测试", 
              font=('Arial', 12, 'bold')).pack(pady=(0, 10))
    
    # 测试字体获取
    for bold, italic, style_name in styles:
        try:
            font = font_manager.get_font(
                test_font['path'] if test_font else None,
                test_font_size,
                bold,
                italic,
                test_text
            )
            
            font_frame = ttk.Frame(results_frame)
            font_frame.pack(fill='x', pady=2)
            
            font_type = type(font).__name__
            status_text = f"✓ {style_name}: {font_type}"
            ttk.Label(font_frame, text=status_text, 
                      foreground='green', font=('Arial', 9)).pack(anchor='w')
            
        except Exception as e:
            font_frame = ttk.Frame(results_frame)
            font_frame.pack(fill='x', pady=2)
            
            status_text = f"✗ {style_name}: {str(e)}"
            ttk.Label(font_frame, text=status_text, 
                      foreground='red', font=('Arial', 9)).pack(anchor='w')
    
    # 说明信息
    info_text = """
测试说明:
1. 测试了四种字体样式组合：普通、粗体、斜体、粗体斜体
2. 检查水印处理器是否能正确处理各种样式
3. 检查字体管理器是否能正确返回字体对象
4. 如果看到 "StyledFontWrapper" 表示使用了样式包装器（模拟效果）
5. 如果看到 "FreeTypeFont" 表示使用了真实的字体变体
"""
    
    ttk.Label(results_frame, text=info_text, justify='left', 
              foreground='gray', font=('Arial', 9)).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_font_bold_italic()
