"""
拖拽组件

提供文件拖拽导入功能。
"""

import tkinter as tk
from tkinter import ttk
import os
from typing import List, Callable, Optional


class DragDropFrame(ttk.Frame):
    """支持拖拽的框架组件"""
    
    def __init__(self, parent, on_drop_callback: Optional[Callable[[List[str]], None]] = None):
        super().__init__(parent)
        self.on_drop_callback = on_drop_callback
        
        # 创建拖拽区域
        self.drop_area = tk.Frame(
            self,
            bg='#f0f0f0',
            relief='ridge',
            bd=2,
            height=200
        )
        self.drop_area.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 添加提示文本
        self.label = tk.Label(
            self.drop_area,
            text="拖拽图片文件到此处\\n或点击下方按钮选择文件",
            bg='#f0f0f0',
            fg='#666666',
            font=('Arial', 12)
        )
        self.label.pack(expand=True)
        
        # 绑定拖拽事件
        self._setup_drag_drop()
        
    def _setup_drag_drop(self):
        """设置拖拽事件绑定"""
        # 注意：这里使用基础的tkinter事件
        # 在实际应用中，可能需要使用tkinterdnd2库来获得更好的拖拽支持
        self.drop_area.bind('<Button-1>', self._on_click)
        self.drop_area.bind('<Enter>', self._on_enter)
        self.drop_area.bind('<Leave>', self._on_leave)
        
    def _on_click(self, event):
        """点击事件处理"""
        # 这里可以触发文件选择对话框
        if self.on_drop_callback:
            # 暂时模拟文件选择，实际实现需要使用filedialog
            pass
            
    def _on_enter(self, event):
        """鼠标进入事件"""
        self.drop_area.config(bg='#e8f4fd')
        self.label.config(bg='#e8f4fd', fg='#0066cc')
        
    def _on_leave(self, event):
        """鼠标离开事件"""
        self.drop_area.config(bg='#f0f0f0')
        self.label.config(bg='#f0f0f0', fg='#666666')
        
    def set_drop_callback(self, callback: Callable[[List[str]], None]):
        """设置拖拽回调函数"""
        self.on_drop_callback = callback
        
    def update_text(self, text: str):
        """更新提示文本"""
        self.label.config(text=text)
