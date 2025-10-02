#!/usr/bin/env python3
"""
颜色选择器测试脚本
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.widgets.color_picker import ColorPickerDialog, show_color_picker
from gui.widgets.enhanced_color_selector import EnhancedColorSelector

def test_color_picker():
    """测试颜色选择器"""
    root = tk.Tk()
    root.title("颜色选择器测试")
    root.geometry("500x400")
    
    def show_picker():
        result = show_color_picker(root, "测试颜色选择器", "blue")
        if result:
            result_label.config(text=f"选择的颜色: {result}")
            # 更新颜色预览
            try:
                from utils.color_utils import parse_color, rgb_to_hex
                rgb = parse_color(result)
                if rgb:
                    hex_color = rgb_to_hex(rgb)
                    color_preview.config(bg=hex_color)
            except:
                pass
        else:
            result_label.config(text="取消选择")
    
    def on_color_change(color):
        enhanced_result_label.config(text=f"增强选择器颜色: {color}")
    
    # 测试按钮
    test_btn = ttk.Button(root, text="打开颜色选择器", command=show_picker)
    test_btn.pack(pady=10)
    
    result_label = ttk.Label(root, text="未选择颜色")
    result_label.pack(pady=5)
    
    # 颜色预览
    color_preview = tk.Label(root, text="颜色预览", width=20, height=3, relief='sunken')
    color_preview.pack(pady=5)
    
    # 测试增强颜色选择器
    ttk.Label(root, text="增强颜色选择器:").pack(pady=(20, 5))
    enhanced_selector = EnhancedColorSelector(
        root, 
        initial_color="red",
        on_color_change=on_color_change
    )
    enhanced_selector.pack(pady=5)
    
    enhanced_result_label = ttk.Label(root, text="增强选择器颜色: red")
    enhanced_result_label.pack(pady=5)
    
    # 说明文字
    ttk.Label(root, text="测试步骤:\n1. 点击'打开颜色选择器'\n2. 在对话框中选择颜色\n3. 点击'确定'按钮\n4. 查看是否正确显示选择的颜色", 
              justify='left').pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_color_picker()
