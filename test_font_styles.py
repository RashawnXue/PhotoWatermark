#!/usr/bin/env python3
"""
字体样式测试脚本
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.widgets.font_preview import FontSelector
from utils.font_manager import font_manager

def test_font_styles():
    """测试字体样式功能"""
    root = tk.Tk()
    root.title("字体样式测试")
    root.geometry("600x500")
    
    def on_font_change(font_info, size, bold, italic):
        """字体变化回调"""
        info_text = f"字体: {font_info['name']}\n"
        info_text += f"大小: {size}px\n"
        info_text += f"粗体: {'是' if bold else '否'}\n"
        info_text += f"斜体: {'是' if italic else '否'}\n"
        info_text += f"路径: {font_info['path']}"
        
        info_label.config(text=info_text)
    
    # 获取字体列表
    fonts = font_manager.get_recommended_fonts()
    
    # 创建字体选择器
    font_selector = FontSelector(
        root,
        font_list=fonts,
        on_font_change=on_font_change,
        preview_width=300,
        preview_height=80
    )
    font_selector.pack(fill='x', padx=20, pady=20)
    
    # 信息显示
    ttk.Label(root, text="当前字体信息:", font=('Arial', 12, 'bold')).pack(pady=(20, 5))
    info_label = ttk.Label(root, text="未选择字体", justify='left', font=('Arial', 10))
    info_label.pack(pady=5)
    
    # 测试说明
    instructions = """测试说明:
1. 选择不同的字体
2. 勾选粗体和斜体选项
3. 调整字体大小
4. 观察预览区域的字体效果变化
5. 查看下方的字体信息显示"""
    
    ttk.Label(root, text=instructions, justify='left', foreground='gray').pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_font_styles()
