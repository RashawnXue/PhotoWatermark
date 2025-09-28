"""
导出确认对话框

显示导出预览信息并允许用户确认导出操作。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from typing import Dict, List, Optional, Callable


class ExportConfirmDialog:
    """导出确认对话框"""
    
    def __init__(self, parent, files: List[str], config: Dict, 
                 on_confirm: Optional[Callable[[], None]] = None):
        self.parent = parent
        self.files = files
        self.config = config
        self.on_confirm = on_confirm
        self.result = False
        
        # 创建对话框
        self._create_dialog()
        
    def _create_dialog(self):
        """创建对话框窗口"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("确认导出")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # 设置图标（如果有的话）
        try:
            self.dialog.iconbitmap(self.parent.iconbitmap())
        except:
            pass
            
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # 创建内容
        self._create_header(main_frame)
        self._create_summary(main_frame)
        self._create_file_list(main_frame)
        self._create_settings_preview(main_frame)
        self._create_buttons(main_frame)
        
        # 绑定事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.dialog.bind('<Return>', lambda e: self._on_confirm())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
    def _create_header(self, parent):
        """创建标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # 图标和标题
        title_label = ttk.Label(
            header_frame,
            text="🚀 准备导出图片",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(
            header_frame,
            text="请确认以下导出设置和文件列表",
            font=('Arial', 10),
            foreground='gray'
        )
        subtitle_label.pack(anchor='w', pady=(2, 0))
        
    def _create_summary(self, parent):
        """创建导出摘要"""
        summary_frame = ttk.LabelFrame(parent, text="导出摘要", padding="10")
        summary_frame.pack(fill='x', pady=(0, 10))
        
        # 文件数量
        files_count = len(self.files)
        ttk.Label(
            summary_frame,
            text=f"📁 文件数量: {files_count} 张图片",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        # 输出目录
        output_dir = self.config.get('output_dir', '')
        if len(output_dir) > 60:
            display_dir = "..." + output_dir[-57:]
        else:
            display_dir = output_dir
            
        ttk.Label(
            summary_frame,
            text=f"📂 输出目录: {display_dir}",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        # 输出格式
        format_info = self.config.get('output_format', 'JPEG')
        if format_info == 'JPEG':
            quality = self.config.get('quality', 95)
            format_info += f" (质量: {quality}%)"
            
        ttk.Label(
            summary_frame,
            text=f"🎨 输出格式: {format_info}",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        # 文件命名
        naming_rule = self.config.get('naming_rule', {})
        naming_type = naming_rule.get('type', 'original')
        naming_text = {
            'original': '保留原文件名',
            'prefix': f"添加前缀: {naming_rule.get('value', '')}",
            'suffix': f"添加后缀: {naming_rule.get('value', '')}"
        }.get(naming_type, '保留原文件名')
        
        ttk.Label(
            summary_frame,
            text=f"✏️  文件命名: {naming_text}",
            font=('Arial', 10)
        ).pack(anchor='w')
        
    def _create_file_list(self, parent):
        """创建文件列表"""
        list_frame = ttk.LabelFrame(parent, text="待导出文件", padding="10")
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建树形视图
        columns = ('filename', 'size', 'path')
        self.file_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=8
        )
        
        # 配置列
        self.file_tree.heading('filename', text='文件名')
        self.file_tree.heading('size', text='大小')
        self.file_tree.heading('path', text='路径')
        
        self.file_tree.column('filename', width=200)
        self.file_tree.column('size', width=80)
        self.file_tree.column('path', width=250)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 填充文件列表
        self._populate_file_list()
        
    def _populate_file_list(self):
        """填充文件列表"""
        for i, file_path in enumerate(self.files):
            filename = os.path.basename(file_path)
            
            # 获取文件大小
            try:
                size = os.path.getsize(file_path)
                size_str = self._format_file_size(size)
            except:
                size_str = "未知"
                
            # 获取目录路径
            dir_path = os.path.dirname(file_path)
            if len(dir_path) > 40:
                dir_path = "..." + dir_path[-37:]
                
            # 插入到树形视图
            self.file_tree.insert('', 'end', values=(filename, size_str, dir_path))
            
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
            
    def _create_settings_preview(self, parent):
        """创建设置预览"""
        settings_frame = ttk.LabelFrame(parent, text="导出设置", padding="10")
        settings_frame.pack(fill='x', pady=(0, 10))
        
        # 创建两列布局
        left_frame = ttk.Frame(settings_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        right_frame = ttk.Frame(settings_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 左列：基本设置
        ttk.Label(left_frame, text="基本设置:", font=('Arial', 9, 'bold')).pack(anchor='w')
        
        format_text = self.config.get('output_format', 'JPEG')
        ttk.Label(left_frame, text=f"• 输出格式: {format_text}").pack(anchor='w', padx=(10, 0))
        
        if format_text == 'JPEG':
            quality = self.config.get('quality', 95)
            ttk.Label(left_frame, text=f"• 图片质量: {quality}%").pack(anchor='w', padx=(10, 0))
            
        # 右列：尺寸设置
        ttk.Label(right_frame, text="尺寸设置:", font=('Arial', 9, 'bold')).pack(anchor='w')
        
        resize_config = self.config.get('resize', {})
        if resize_config.get('enabled', False):
            resize_type = resize_config.get('type', 'none')
            if resize_type == 'width':
                ttk.Label(right_frame, text=f"• 按宽度: {resize_config.get('width', 1920)}px").pack(anchor='w', padx=(10, 0))
            elif resize_type == 'height':
                ttk.Label(right_frame, text=f"• 按高度: {resize_config.get('height', 1080)}px").pack(anchor='w', padx=(10, 0))
            elif resize_type == 'percentage':
                ttk.Label(right_frame, text=f"• 按比例: {resize_config.get('percentage', 100)}%").pack(anchor='w', padx=(10, 0))
        else:
            ttk.Label(right_frame, text="• 保持原尺寸").pack(anchor='w', padx=(10, 0))
            
    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame,
            text="取消",
            command=self._on_cancel
        )
        cancel_btn.pack(side='right', padx=(5, 0))
        
        # 确认导出按钮
        confirm_btn = ttk.Button(
            button_frame,
            text="确认导出",
            command=self._on_confirm,
            style='Accent.TButton'
        )
        confirm_btn.pack(side='right')
        
        # 修改设置按钮
        modify_btn = ttk.Button(
            button_frame,
            text="修改设置",
            command=self._on_modify_settings
        )
        modify_btn.pack(side='left')
        
        # 设置默认焦点
        confirm_btn.focus_set()
        
    def _on_confirm(self):
        """确认导出"""
        # 再次检查输出目录
        output_dir = self.config.get('output_dir', '')
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return
            
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录: {e}")
                return
                
        self.result = True
        self.dialog.destroy()
        
        # 调用确认回调
        if self.on_confirm:
            self.on_confirm()
            
    def _on_cancel(self):
        """取消导出"""
        self.result = False
        self.dialog.destroy()
        
    def _on_modify_settings(self):
        """修改设置"""
        self.result = 'modify'
        self.dialog.destroy()
        
    def show(self) -> str:
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result
