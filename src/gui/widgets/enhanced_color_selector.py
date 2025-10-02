"""
增强的颜色选择组件

结合下拉框和颜色选择器的复合组件，用于主界面的颜色设置。
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List
from .color_picker import show_color_picker
from ...utils.color_utils import parse_color, rgb_to_hex, get_preset_colors


class EnhancedColorSelector(ttk.Frame):
    """增强的颜色选择器组件"""
    
    def __init__(self, parent, initial_color: str = "white", 
                 on_color_change: Optional[Callable[[str], None]] = None,
                 show_alpha: bool = False, width: int = 15):
        super().__init__(parent)
        
        self.on_color_change = on_color_change
        self.show_alpha = show_alpha
        self.current_color = initial_color
        
        # 预设颜色选项
        self.preset_colors = [
            "white", "black", "red", "green", "blue", "yellow", 
            "orange", "purple", "cyan", "magenta", "pink", "gray"
        ]
        
        self._create_widgets(width)
        self._update_color_display()
        
    def _create_widgets(self, width: int):
        """创建界面组件"""
        # 颜色下拉框
        self.color_var = tk.StringVar(value=self.current_color)
        self.color_combo = ttk.Combobox(
            self,
            textvariable=self.color_var,
            values=self.preset_colors,
            state="readonly",
            width=width
        )
        self.color_combo.pack(side='left', fill='x', expand=True)
        self.color_combo.bind('<<ComboboxSelected>>', self._on_combo_change)
        
        # 颜色预览框
        self.color_preview = tk.Canvas(self, width=25, height=20, 
                                     relief='sunken', borderwidth=1)
        self.color_preview.pack(side='left', padx=(5, 0))
        
        # 更多颜色按钮
        self.more_colors_btn = ttk.Button(
            self, text="更多...", width=6,
            command=self._open_color_picker
        )
        self.more_colors_btn.pack(side='left', padx=(2, 0))
        
    def _update_color_display(self):
        """更新颜色预览"""
        rgb = parse_color(self.current_color)
        if rgb:
            hex_color = rgb_to_hex(rgb)
            self.color_preview.delete('all')
            self.color_preview.create_rectangle(
                1, 1, 24, 19, fill=hex_color, outline='gray'
            )
    
    def _on_combo_change(self, event=None):
        """下拉框选择变化"""
        new_color = self.color_var.get()
        if new_color != self.current_color:
            self.current_color = new_color
            self._update_color_display()
            self._notify_color_change()
    
    def _open_color_picker(self):
        """打开颜色选择器"""
        result = show_color_picker(
            self, 
            title="选择颜色",
            initial_color=self.current_color,
            show_alpha=self.show_alpha
        )
        
        if result:
            # 如果是十六进制颜色，直接使用
            if result.startswith('#'):
                self.current_color = result
            else:
                # 如果是其他格式，尝试解析
                rgb = parse_color(result)
                if rgb:
                    self.current_color = rgb_to_hex(rgb)
                else:
                    self.current_color = result
            
            # 更新下拉框显示
            if self.current_color in self.preset_colors:
                self.color_var.set(self.current_color)
            else:
                # 如果不在预设列表中，添加到下拉框
                current_values = list(self.color_combo['values'])
                if self.current_color not in current_values:
                    current_values.append(self.current_color)
                    self.color_combo['values'] = current_values
                self.color_var.set(self.current_color)
            
            self._update_color_display()
            self._notify_color_change()
    
    def _notify_color_change(self):
        """通知颜色变化"""
        if self.on_color_change:
            self.on_color_change(self.current_color)
    
    def get_color(self) -> str:
        """获取当前颜色"""
        return self.current_color
    
    def set_color(self, color: str):
        """设置颜色"""
        self.current_color = color
        
        # 更新下拉框
        if color in self.preset_colors:
            self.color_var.set(color)
        else:
            # 添加到下拉框选项
            current_values = list(self.color_combo['values'])
            if color not in current_values:
                current_values.append(color)
                self.color_combo['values'] = current_values
            self.color_var.set(color)
        
        self._update_color_display()


class ColorSelectorWithLabel(ttk.Frame):
    """带标签的颜色选择器"""
    
    def __init__(self, parent, label_text: str, initial_color: str = "white",
                 on_color_change: Optional[Callable[[str], None]] = None,
                 show_alpha: bool = False, label_width: int = 10):
        super().__init__(parent)
        
        # 标签
        self.label = ttk.Label(self, text=label_text, width=label_width)
        self.label.pack(side='left')
        
        # 颜色选择器
        self.color_selector = EnhancedColorSelector(
            self, initial_color, on_color_change, show_alpha
        )
        self.color_selector.pack(side='left', fill='x', expand=True, padx=(5, 0))
    
    def get_color(self) -> str:
        """获取当前颜色"""
        return self.color_selector.get_color()
    
    def set_color(self, color: str):
        """设置颜色"""
        self.color_selector.set_color(color)
