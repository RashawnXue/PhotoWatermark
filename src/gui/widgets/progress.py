"""
进度条对话框组件

显示处理进度和状态信息。
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import threading


class ProgressDialog:
    """进度条对话框"""
    
    def __init__(self, parent, title: str = "处理中...", 
                 on_cancel: Optional[Callable] = None):
        self.parent = parent
        self.on_cancel = on_cancel
        self.cancelled = False
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")  # 增加高度，确保按钮完全显示
        self.dialog.resizable(False, False)
        
        # 设置为模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _center_window(self):
        """将窗口居中显示"""
        self.dialog.update_idletasks()
        
        # 获取父窗口位置和大小
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 计算居中位置
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=(20, 10))
        
        # 状态标签
        self.status_label = ttk.Label(
            main_frame,
            text="准备开始处理...",
            font=('Arial', 10),
            wraplength=350  # 添加文本自动换行
        )
        self.status_label.pack(pady=(0, 15))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=350
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # 进度文本
        self.progress_label = ttk.Label(
            main_frame,
            text="0%",
            font=('Arial', 9)
        )
        self.progress_label.pack(pady=(0, 15))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))  # 增加顶部间距
        
        # 取消按钮
        self.cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self._on_cancel
        )
        self.cancel_button.pack(side='right')
        
    def _on_cancel(self):
        """取消按钮点击事件"""
        self.cancelled = True
        if self.on_cancel:
            self.on_cancel()
        self._close()
        
    def _on_close(self):
        """窗口关闭事件"""
        if not self.cancelled:
            self._on_cancel()
            
    def update_progress(self, progress: float, status: str = ""):
        """更新进度
        
        Args:
            progress: 进度百分比 (0-100)
            status: 状态文本
        """
        if self.cancelled:
            return
            
        # 在主线程中更新界面
        self.dialog.after(0, self._update_ui, progress, status)
        
    def _update_ui(self, progress: float, status: str):
        """在主线程中更新UI"""
        if self.cancelled:
            return
            
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")
        
        if status:
            self.status_label.config(text=status)
            
        # 更新界面
        self.dialog.update_idletasks()
        
    def set_indeterminate(self, indeterminate: bool = True):
        """设置为不确定进度模式"""
        if indeterminate:
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start()
            self.progress_label.config(text="处理中...")
        else:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate')
            
    def complete(self, message: str = "处理完成！"):
        """完成处理"""
        self.update_progress(100, message)
        self.cancel_button.config(text="关闭")
        
        # 3秒后自动关闭
        self.dialog.after(3000, self._close)
        
    def _close(self):
        """关闭对话框"""
        try:
            self.dialog.grab_release()
            self.dialog.destroy()
        except:
            pass
            
    def is_cancelled(self) -> bool:
        """检查是否已取消"""
        return self.cancelled
