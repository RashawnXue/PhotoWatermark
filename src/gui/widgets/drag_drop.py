"""
拖拽组件

提供文件拖拽导入功能。
"""

import tkinter as tk
from tkinter import ttk
import os
from typing import List, Callable, Optional

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("警告: tkinterdnd2 未安装，拖拽功能将不可用")


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
        drag_text = "拖拽图片文件到此处\n或点击下方按钮选择文件"
        if not DND_AVAILABLE:
            drag_text = "点击下方按钮选择文件\n(拖拽功能需要安装 tkinterdnd2)"
            
        self.label = tk.Label(
            self.drop_area,
            text=drag_text,
            bg='#f0f0f0',
            fg='#666666',
            font=('Arial', 12),
            justify='center'
        )
        self.label.pack(expand=True)
        
        # 绑定拖拽事件
        self._setup_drag_drop()
        
    def _setup_drag_drop(self):
        """设置拖拽事件绑定"""
        if DND_AVAILABLE:
            # 使用tkinterdnd2实现真正的拖拽功能
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind('<<Drop>>', self._on_drop)
            self.drop_area.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.drop_area.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        
        # 绑定鼠标事件（用于视觉反馈）
        self.drop_area.bind('<Enter>', self._on_mouse_enter)
        self.drop_area.bind('<Leave>', self._on_mouse_leave)
        self.label.bind('<Enter>', self._on_mouse_enter)
        self.label.bind('<Leave>', self._on_mouse_leave)
        
    def _on_drop(self, event):
        """文件拖拽放下事件"""
        if not self.on_drop_callback:
            return
            
        # 解析拖拽的文件路径
        files = self._parse_drop_files(event.data)
        
        if files:
            # 过滤出存在的文件和目录
            valid_paths = []
            for file_path in files:
                if os.path.exists(file_path):
                    valid_paths.append(file_path)
            
            if valid_paths:
                self.on_drop_callback(valid_paths)
                self.update_text("文件已拖拽导入！")
                # 2秒后恢复原始文本
                self.after(2000, lambda: self.update_text(
                    "拖拽图片文件到此处\n或点击下方按钮选择文件"
                ))
            else:
                self.update_text("没有找到有效的文件或目录")
                self.after(2000, lambda: self.update_text(
                    "拖拽图片文件到此处\n或点击下方按钮选择文件"
                ))
        
    def _parse_drop_files(self, data):
        """解析拖拽数据中的文件路径"""
        files = []
        
        # tkinterdnd2 返回的数据格式可能是字符串或列表
        if isinstance(data, str):
            import re
            
            # 处理tkinterdnd2的标准格式
            # 通常格式为: {/path/with spaces/file.jpg} /path/without/spaces/file.jpg
            if '{' in data and '}' in data:
                # 使用正则表达式匹配大括号包围的路径和普通路径
                pattern = r'\\{([^}]+)\\}|([^\\s{}]+)'
                matches = re.findall(pattern, data)
                for match in matches:
                    file_path = match[0] if match[0] else match[1]
                    if file_path.strip():
                        files.append(file_path.strip())
            else:
                # 简单的空格分割（适用于没有空格的路径）
                potential_files = data.split()
                for file_path in potential_files:
                    if file_path.strip():
                        files.append(file_path.strip())
                        
            # 如果上面的方法都没有找到文件，可能是单个路径
            if not files and data.strip():
                files = [data.strip()]
                
        elif isinstance(data, (list, tuple)):
            # 直接是文件路径列表
            files = [str(f).strip() for f in data if str(f).strip()]
        else:
            # 其他类型，尝试转换为字符串
            file_str = str(data).strip()
            if file_str:
                files = [file_str]
                
        return files
        
    def _on_drag_enter(self, event):
        """拖拽进入事件"""
        self.drop_area.config(bg='#e8f4fd')
        self.label.config(bg='#e8f4fd', fg='#0066cc')
        self.update_text("释放以导入文件")
        
    def _on_drag_leave(self, event):
        """拖拽离开事件"""
        self.drop_area.config(bg='#f0f0f0')
        self.label.config(bg='#f0f0f0', fg='#666666')
        self.update_text("拖拽图片文件到此处\n或点击下方按钮选择文件")
        
    def _on_mouse_enter(self, event):
        """鼠标进入事件"""
        if not hasattr(event.widget, 'dnd_bind') or not DND_AVAILABLE:
            self.drop_area.config(bg='#e8f4fd')
            self.label.config(bg='#e8f4fd', fg='#0066cc')
        
    def _on_mouse_leave(self, event):
        """鼠标离开事件"""
        if not hasattr(event.widget, 'dnd_bind') or not DND_AVAILABLE:
            self.drop_area.config(bg='#f0f0f0')
            self.label.config(bg='#f0f0f0', fg='#666666')
        
    def set_drop_callback(self, callback: Callable[[List[str]], None]):
        """设置拖拽回调函数"""
        self.on_drop_callback = callback
        
    def update_text(self, text: str):
        """更新提示文本"""
        self.label.config(text=text)
