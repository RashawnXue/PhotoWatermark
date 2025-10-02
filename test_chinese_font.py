#!/usr/bin/env python3
"""
中文字体回退测试脚本
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.widgets.font_preview import FontPreview
from utils.font_manager import font_manager

def test_chinese_font_fallback():
    """测试中文字体回退功能"""
    root = tk.Tk()
    root.title("中文字体回退测试")
    root.geometry("800x600")
    
    # 获取字体列表
    fonts = font_manager.get_recommended_fonts()
    
    # 创建测试界面
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 说明文字
    ttk.Label(main_frame, text="中文字体回退功能测试", 
              font=('Arial', 16, 'bold')).pack(pady=(0, 20))
    
    # 测试文本
    test_texts = [
        "Hello World AaBbCc",  # 纯英文
        "你好世界 AaBbCc",      # 中英混合
        "测试中文字体显示效果",    # 纯中文
        "Font Style 字体样式"    # 中英混合
    ]
    
    # 选择一个英文字体进行测试
    english_fonts = [f for f in fonts if not f.get('supports_chinese', False)]
    test_font = english_fonts[0] if english_fonts else fonts[0]
    
    ttk.Label(main_frame, text=f"测试字体: {test_font['name']}", 
              font=('Arial', 12)).pack(pady=(0, 10))
    
    ttk.Label(main_frame, text="(该字体不支持中文，系统会自动回退到支持中文的字体)", 
              foreground='gray').pack(pady=(0, 20))
    
    # 为每个测试文本创建预览
    for i, text in enumerate(test_texts):
        # 文本标签
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill='x', pady=10)
        
        ttk.Label(text_frame, text=f"测试文本 {i+1}: {text}", 
                  font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # 字体预览
        preview = FontPreview(text_frame, width=400, height=50)
        preview.pack(pady=5)
        
        # 设置字体和预览文本
        preview.set_font(test_font['path'], 24, False, False)
        preview.set_preview_text(text)
    
    # 样式测试
    ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
    
    ttk.Label(main_frame, text="样式测试 (中文 + 粗体/斜体)", 
              font=('Arial', 12, 'bold')).pack(pady=(0, 10))
    
    styles = [
        (False, False, "普通"),
        (True, False, "粗体"),
        (False, True, "斜体"),
        (True, True, "粗体斜体")
    ]
    
    for bold, italic, style_name in styles:
        style_frame = ttk.Frame(main_frame)
        style_frame.pack(fill='x', pady=5)
        
        ttk.Label(style_frame, text=f"{style_name}: 中文字体样式测试", 
                  font=('Arial', 10)).pack(anchor='w')
        
        preview = FontPreview(style_frame, width=300, height=40)
        preview.pack(pady=2)
        
        preview.set_font(test_font['path'], 20, bold, italic)
        preview.set_preview_text("中文字体样式测试")
    
    # 说明信息
    info_text = """
测试说明:
1. 上方使用了一个不支持中文的英文字体
2. 当文本包含中文字符时，系统会自动回退到支持中文的字体
3. 纯英文文本仍使用原字体显示
4. 样式效果（粗体/斜体）在中文字体上也能正常工作
5. 如果看到方框□而不是中文字符，说明字体回退功能需要调试
"""
    
    ttk.Label(main_frame, text=info_text, justify='left', 
              foreground='gray', font=('Arial', 9)).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_chinese_font_fallback()
