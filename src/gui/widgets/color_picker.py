"""
颜色选择器组件

提供完整的颜色选择功能，包括RGB、HSV、十六进制输入和预设颜色。
"""

import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Callable, Optional, List, Tuple
import colorsys
import re

from ...utils.color_utils import parse_color, rgb_to_hex, get_available_colors


class ColorPicker(ttk.Frame):
    """颜色选择器组件"""
    
    def __init__(self, parent, initial_color: str = "white", 
                 on_color_change: Optional[Callable[[str], None]] = None,
                 show_alpha: bool = False):
        super().__init__(parent)
        
        self.on_color_change = on_color_change
        self.show_alpha = show_alpha
        self.current_color = initial_color
        self.current_rgb = parse_color(initial_color) or (255, 255, 255)
        self.current_alpha = 1.0
        self._updating_display = False  # 标志位，防止循环触发
        
        # 颜色历史记录
        self.color_history: List[str] = []
        self.max_history = 10
        
        self._create_widgets()
        self._update_color_display()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 主要颜色显示区域
        display_frame = ttk.Frame(self)
        display_frame.pack(fill='x', pady=(0, 10))
        
        # 当前颜色显示
        self.color_display = tk.Canvas(display_frame, width=60, height=40, 
                                     relief='sunken', borderwidth=2)
        self.color_display.pack(side='left', padx=(0, 10))
        
        # 颜色值显示和输入
        values_frame = ttk.Frame(display_frame)
        values_frame.pack(side='left', fill='both', expand=True)
        
        # 十六进制输入
        hex_frame = ttk.Frame(values_frame)
        hex_frame.pack(fill='x', pady=2)
        ttk.Label(hex_frame, text="十六进制:", width=8).pack(side='left')
        self.hex_var = tk.StringVar(value=rgb_to_hex(self.current_rgb))
        hex_entry = ttk.Entry(hex_frame, textvariable=self.hex_var, width=10)
        hex_entry.pack(side='left', padx=(5, 0))
        hex_entry.bind('<KeyRelease>', self._on_hex_change)
        hex_entry.bind('<FocusOut>', self._on_hex_change)
        
        # RGB输入
        rgb_frame = ttk.Frame(values_frame)
        rgb_frame.pack(fill='x', pady=2)
        ttk.Label(rgb_frame, text="RGB:", width=8).pack(side='left')
        
        self.r_var = tk.IntVar(value=self.current_rgb[0])
        self.g_var = tk.IntVar(value=self.current_rgb[1])
        self.b_var = tk.IntVar(value=self.current_rgb[2])
        
        r_entry = ttk.Entry(rgb_frame, textvariable=self.r_var, width=4)
        r_entry.pack(side='left', padx=(5, 2))
        ttk.Label(rgb_frame, text=",").pack(side='left')
        g_entry = ttk.Entry(rgb_frame, textvariable=self.g_var, width=4)
        g_entry.pack(side='left', padx=(2, 2))
        ttk.Label(rgb_frame, text=",").pack(side='left')
        b_entry = ttk.Entry(rgb_frame, textvariable=self.b_var, width=4)
        b_entry.pack(side='left', padx=(2, 0))
        
        # 绑定RGB变化事件
        self.r_var.trace_add('write', self._on_rgb_change)
        self.g_var.trace_add('write', self._on_rgb_change)
        self.b_var.trace_add('write', self._on_rgb_change)
        
        # 透明度控制（如果启用）
        if self.show_alpha:
            alpha_frame = ttk.Frame(values_frame)
            alpha_frame.pack(fill='x', pady=2)
            ttk.Label(alpha_frame, text="透明度:", width=8).pack(side='left')
            self.alpha_var = tk.DoubleVar(value=self.current_alpha)
            alpha_scale = ttk.Scale(alpha_frame, from_=0.0, to=1.0, 
                                  variable=self.alpha_var, orient='horizontal')
            alpha_scale.pack(side='left', fill='x', expand=True, padx=(5, 0))
            self.alpha_var.trace_add('write', self._on_alpha_change)
        
        # 按钮区域
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(button_frame, text="颜色选择器", 
                  command=self._open_color_chooser).pack(side='left')
        ttk.Button(button_frame, text="重置", 
                  command=self._reset_color).pack(side='left', padx=(5, 0))
        
        # 预设颜色
        self._create_preset_colors()
        
        # 颜色历史
        self._create_color_history()
        
    def _create_preset_colors(self):
        """创建预设颜色区域"""
        preset_frame = ttk.LabelFrame(self, text="预设颜色")
        preset_frame.pack(fill='x', pady=(0, 10))
        
        # 获取预设颜色
        preset_colors = [
            ("白色", "white"), ("黑色", "black"), ("红色", "red"), ("绿色", "green"),
            ("蓝色", "blue"), ("黄色", "yellow"), ("青色", "cyan"), ("洋红", "magenta"),
            ("橙色", "orange"), ("紫色", "purple"), ("粉色", "pink"), ("灰色", "gray"),
            ("深红", "#8B0000"), ("深绿", "#006400"), ("深蓝", "#000080"), ("金色", "gold")
        ]
        
        colors_grid = ttk.Frame(preset_frame)
        colors_grid.pack(padx=10, pady=5)
        
        for i, (name, color) in enumerate(preset_colors):
            row = i // 8
            col = i % 8
            
            rgb = parse_color(color) or (128, 128, 128)
            hex_color = rgb_to_hex(rgb)
            
            # 使用Canvas创建颜色按钮，确保在所有平台上都能正确显示颜色
            color_canvas = tk.Canvas(colors_grid, width=25, height=20, 
                                   highlightthickness=1, highlightbackground='gray')
            color_canvas.grid(row=row, column=col, padx=1, pady=1)
            
            # 绘制颜色矩形
            color_canvas.create_rectangle(1, 1, 24, 19, fill=hex_color, outline='gray')
            
            # 绑定点击事件
            color_canvas.bind('<Button-1>', lambda e, c=color: self._set_preset_color(c))
            color_canvas.bind('<Enter>', lambda e: color_canvas.config(highlightbackground='black'))
            color_canvas.bind('<Leave>', lambda e: color_canvas.config(highlightbackground='gray'))
            color_canvas.config(cursor='hand2')
            
            # 保存引用以便添加工具提示
            color_canvas.color_name = name
            
            # 添加工具提示
            self._create_tooltip(color_canvas, name)
    
    def _create_color_history(self):
        """创建颜色历史区域"""
        history_frame = ttk.LabelFrame(self, text="颜色历史")
        history_frame.pack(fill='x')
        
        self.history_frame = ttk.Frame(history_frame)
        self.history_frame.pack(padx=10, pady=5)
        
        self._update_history_display()
    
    def _create_tooltip(self, widget, text):
        """创建工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow",
                           relief="solid", borderwidth=1, font=("Arial", 8))
            label.pack()
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _update_color_display(self):
        """更新颜色显示"""
        hex_color = rgb_to_hex(self.current_rgb)
        self.color_display.delete('all')
        self.color_display.create_rectangle(2, 2, 58, 38, fill=hex_color, outline='gray')
        
        # 暂时禁用事件绑定，避免循环触发
        self._updating_display = True
        
        # 更新输入框
        self.hex_var.set(hex_color)
        self.r_var.set(self.current_rgb[0])
        self.g_var.set(self.current_rgb[1])
        self.b_var.set(self.current_rgb[2])
        
        # 重新启用事件绑定
        self._updating_display = False
    
    def _on_hex_change(self, event=None):
        """十六进制输入变化"""
        if self._updating_display:
            return
            
        try:
            hex_value = self.hex_var.get().strip()
            if not hex_value.startswith('#'):
                hex_value = '#' + hex_value
            
            rgb = parse_color(hex_value)
            if rgb:
                self.current_rgb = rgb
                self.current_color = hex_value
                self._update_color_display()
                self._notify_color_change()
        except Exception:
            pass
    
    def _on_rgb_change(self, *args):
        """RGB输入变化"""
        if self._updating_display:
            return
            
        try:
            r = max(0, min(255, self.r_var.get()))
            g = max(0, min(255, self.g_var.get()))
            b = max(0, min(255, self.b_var.get()))
            
            self.current_rgb = (r, g, b)
            self.current_color = rgb_to_hex(self.current_rgb)
            self._update_color_display()
            self._notify_color_change()
        except Exception:
            pass
    
    def _on_alpha_change(self, *args):
        """透明度变化"""
        try:
            self.current_alpha = self.alpha_var.get()
            self._notify_color_change()
        except Exception:
            pass
    
    def _open_color_chooser(self):
        """打开系统颜色选择器"""
        current_hex = rgb_to_hex(self.current_rgb)
        color = colorchooser.askcolor(color=current_hex, title="选择颜色")
        
        if color[0]:  # color[0] 是RGB元组
            self.current_rgb = tuple(int(c) for c in color[0])
            self._update_color_display()
            self._add_to_history(rgb_to_hex(self.current_rgb))
            self._notify_color_change()
    
    def _set_preset_color(self, color_name: str):
        """设置预设颜色"""
        rgb = parse_color(color_name)
        if rgb:
            self.current_rgb = rgb
            self.current_color = color_name
            self._update_color_display()
            self._add_to_history(color_name)
            self._notify_color_change()
    
    def _reset_color(self):
        """重置为初始颜色"""
        rgb = parse_color("white")
        if rgb:
            self.current_rgb = rgb
            self.current_color = "white"
            self._update_color_display()
            self._notify_color_change()
    
    def _add_to_history(self, color: str):
        """添加颜色到历史记录"""
        if color in self.color_history:
            self.color_history.remove(color)
        
        self.color_history.insert(0, color)
        if len(self.color_history) > self.max_history:
            self.color_history = self.color_history[:self.max_history]
        
        self._update_history_display()
    
    def _update_history_display(self):
        """更新历史记录显示"""
        # 清除现有按钮
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        # 创建历史颜色按钮
        for i, color in enumerate(self.color_history):
            rgb = parse_color(color) or (128, 128, 128)
            hex_color = rgb_to_hex(rgb)
            
            # 使用Canvas创建历史颜色按钮
            history_canvas = tk.Canvas(self.history_frame, width=25, height=20,
                                     highlightthickness=1, highlightbackground='gray')
            history_canvas.grid(row=0, column=i, padx=1, pady=1)
            
            # 绘制颜色矩形
            history_canvas.create_rectangle(1, 1, 24, 19, fill=hex_color, outline='gray')
            
            # 绑定点击事件
            history_canvas.bind('<Button-1>', lambda e, c=color: self._set_preset_color(c))
            history_canvas.bind('<Enter>', lambda e: history_canvas.config(highlightbackground='black'))
            history_canvas.bind('<Leave>', lambda e: history_canvas.config(highlightbackground='gray'))
            history_canvas.config(cursor='hand2')
    
    def _notify_color_change(self):
        """通知颜色变化"""
        if self.on_color_change:
            if self.show_alpha:
                # 返回RGBA格式的字符串
                color_str = f"rgba({self.current_rgb[0]},{self.current_rgb[1]},{self.current_rgb[2]},{self.current_alpha})"
            else:
                # 返回十六进制格式
                color_str = rgb_to_hex(self.current_rgb)
            
            self.on_color_change(color_str)
    
    def get_color(self) -> str:
        """获取当前颜色"""
        if self.show_alpha:
            return f"rgba({self.current_rgb[0]},{self.current_rgb[1]},{self.current_rgb[2]},{self.current_alpha})"
        else:
            return rgb_to_hex(self.current_rgb)
    
    def set_color(self, color: str):
        """设置颜色"""
        rgb = parse_color(color)
        if rgb:
            self.current_rgb = rgb
            self.current_color = color
            self._update_color_display()


class ColorPickerDialog:
    """颜色选择器对话框"""
    
    def __init__(self, parent, title: str = "选择颜色", 
                 initial_color: str = "white", show_alpha: bool = False):
        self.result = None
        self.show_alpha = show_alpha
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # 创建颜色选择器
        self.color_picker = ColorPicker(
            self.dialog, 
            initial_color=initial_color,
            show_alpha=show_alpha
        )
        self.color_picker.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 按钮区域
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="确定", 
                  command=self._on_ok).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="取消", 
                  command=self._on_cancel).pack(side='right')
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def _on_ok(self):
        """确定按钮"""
        self.result = self.color_picker.get_color()
        self.dialog.destroy()
    
    def _on_cancel(self):
        """取消按钮"""
        self.result = None
        self.dialog.destroy()
    
    def get_result(self) -> Optional[str]:
        """获取选择结果"""
        return self.result


def show_color_picker(parent, title: str = "选择颜色", 
                     initial_color: str = "white", 
                     show_alpha: bool = False) -> Optional[str]:
    """显示颜色选择器对话框"""
    dialog = ColorPickerDialog(parent, title, initial_color, show_alpha)
    return dialog.get_result()
