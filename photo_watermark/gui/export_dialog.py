"""
导出设置对话框

提供导出参数配置界面。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Dict, Optional, Callable


class ExportDialog:
    """导出设置对话框"""
    
    def __init__(self, parent, initial_config: Optional[Dict] = None,
                 on_export: Optional[Callable[[Dict], None]] = None):
        self.parent = parent
        self.on_export = on_export
        self.result = None
        
        # 默认配置
        self.config = {
            'output_dir': '',
            'naming_rule': {'type': 'original', 'value': ''},
            'output_format': 'JPEG',
            'quality': 95,
            'resize': {
                'enabled': False,
                'type': 'none',
                'width': 1920,
                'height': 1080,
                'percentage': 100,
                'keep_ratio': True
            }
        }
        
        # 应用初始配置
        if initial_config:
            self.config.update(initial_config)
            
        # 创建对话框
        self._create_dialog()
        
    def _create_dialog(self):
        """创建对话框窗口"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("导出设置")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # 设置为模态对话框
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
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
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 输出目录设置
        self._create_output_dir_section(main_frame)
        
        # 文件命名设置
        self._create_naming_section(main_frame)
        
        # 输出格式设置
        self._create_format_section(main_frame)
        
        # 图片缩放设置
        self._create_resize_section(main_frame)
        
        # 按钮区域
        self._create_buttons(main_frame)
        
    def _create_output_dir_section(self, parent):
        """创建输出目录设置区域"""
        # 标题
        ttk.Label(parent, text="输出目录", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # 目录选择框架
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill='x', pady=(0, 15))
        
        self.output_dir_var = tk.StringVar(value=self.config['output_dir'])
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, state='readonly')
        self.dir_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(dir_frame, text="浏览", command=self._browse_output_dir).pack(side='right')
        
    def _create_naming_section(self, parent):
        """创建文件命名设置区域"""
        # 标题
        ttk.Label(parent, text="文件命名", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        naming_frame = ttk.LabelFrame(parent, text="命名规则")
        naming_frame.pack(fill='x', pady=(0, 15))
        
        # 命名规则选项
        self.naming_var = tk.StringVar(value=self.config['naming_rule']['type'])
        
        ttk.Radiobutton(
            naming_frame, text="保留原文件名", 
            variable=self.naming_var, value="original",
            command=self._on_naming_change
        ).pack(anchor='w', padx=10, pady=5)
        
        # 前缀选项
        prefix_frame = ttk.Frame(naming_frame)
        prefix_frame.pack(fill='x', padx=10, pady=2)
        
        ttk.Radiobutton(
            prefix_frame, text="添加前缀:", 
            variable=self.naming_var, value="prefix",
            command=self._on_naming_change
        ).pack(side='left')
        
        self.prefix_var = tk.StringVar(value=self.config['naming_rule'].get('value', 'wm_') if self.config['naming_rule']['type'] == 'prefix' else 'wm_')
        self.prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=15)
        self.prefix_entry.pack(side='left', padx=(5, 0))
        
        # 后缀选项
        suffix_frame = ttk.Frame(naming_frame)
        suffix_frame.pack(fill='x', padx=10, pady=2)
        
        ttk.Radiobutton(
            suffix_frame, text="添加后缀:", 
            variable=self.naming_var, value="suffix",
            command=self._on_naming_change
        ).pack(side='left')
        
        self.suffix_var = tk.StringVar(value=self.config['naming_rule'].get('value', '_watermarked') if self.config['naming_rule']['type'] == 'suffix' else '_watermarked')
        self.suffix_entry = ttk.Entry(suffix_frame, textvariable=self.suffix_var, width=15)
        self.suffix_entry.pack(side='left', padx=(5, 0))
        
        # 预览
        self.preview_label = ttk.Label(naming_frame, text="", foreground='blue')
        self.preview_label.pack(anchor='w', padx=10, pady=(5, 10))
        
        # 绑定变量变化事件
        self.prefix_var.trace('w', self._update_preview)
        self.suffix_var.trace('w', self._update_preview)
        
        self._on_naming_change()
        
    def _create_format_section(self, parent):
        """创建输出格式设置区域"""
        # 标题
        ttk.Label(parent, text="输出格式", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        format_frame = ttk.LabelFrame(parent, text="格式选项")
        format_frame.pack(fill='x', pady=(0, 15))
        
        # 格式选择
        format_options_frame = ttk.Frame(format_frame)
        format_options_frame.pack(fill='x', padx=10, pady=5)
        
        self.format_var = tk.StringVar(value=self.config['output_format'])
        
        ttk.Radiobutton(
            format_options_frame, text="JPEG", 
            variable=self.format_var, value="JPEG",
            command=self._on_format_change
        ).pack(side='left', padx=(0, 20))
        
        ttk.Radiobutton(
            format_options_frame, text="PNG", 
            variable=self.format_var, value="PNG",
            command=self._on_format_change
        ).pack(side='left')
        
        # JPEG质量设置
        self.quality_frame = ttk.Frame(format_frame)
        self.quality_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(self.quality_frame, text="JPEG质量:").pack(side='left')
        
        self.quality_var = tk.IntVar(value=self.config['quality'])
        self.quality_scale = ttk.Scale(
            self.quality_frame, from_=1, to=100, 
            variable=self.quality_var, orient='horizontal',
            command=self._on_quality_change
        )
        self.quality_scale.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        self.quality_label = ttk.Label(self.quality_frame, text=f"{self.quality_var.get()}")
        self.quality_label.pack(side='right')
        
        self._on_format_change()
        
    def _create_resize_section(self, parent):
        """创建图片缩放设置区域"""
        # 标题
        ttk.Label(parent, text="图片缩放", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        resize_frame = ttk.LabelFrame(parent, text="缩放选项")
        resize_frame.pack(fill='x', pady=(0, 15))
        
        # 启用缩放复选框
        self.resize_enabled_var = tk.BooleanVar(value=self.config['resize']['enabled'])
        ttk.Checkbutton(
            resize_frame, text="启用图片缩放", 
            variable=self.resize_enabled_var,
            command=self._on_resize_enable_change
        ).pack(anchor='w', padx=10, pady=5)
        
        # 缩放选项框架
        self.resize_options_frame = ttk.Frame(resize_frame)
        self.resize_options_frame.pack(fill='x', padx=20, pady=5)
        
        # 缩放类型
        self.resize_type_var = tk.StringVar(value=self.config['resize']['type'])
        
        # 不缩放
        ttk.Radiobutton(
            self.resize_options_frame, text="不缩放", 
            variable=self.resize_type_var, value="none"
        ).pack(anchor='w', pady=2)
        
        # 按宽度缩放
        width_frame = ttk.Frame(self.resize_options_frame)
        width_frame.pack(fill='x', pady=2)
        ttk.Radiobutton(
            width_frame, text="按宽度:", 
            variable=self.resize_type_var, value="width"
        ).pack(side='left')
        self.width_var = tk.IntVar(value=self.config['resize']['width'])
        ttk.Entry(width_frame, textvariable=self.width_var, width=8).pack(side='left', padx=(5, 2))
        ttk.Label(width_frame, text="px").pack(side='left')
        
        # 按高度缩放
        height_frame = ttk.Frame(self.resize_options_frame)
        height_frame.pack(fill='x', pady=2)
        ttk.Radiobutton(
            height_frame, text="按高度:", 
            variable=self.resize_type_var, value="height"
        ).pack(side='left')
        self.height_var = tk.IntVar(value=self.config['resize']['height'])
        ttk.Entry(height_frame, textvariable=self.height_var, width=8).pack(side='left', padx=(5, 2))
        ttk.Label(height_frame, text="px").pack(side='left')
        
        # 按百分比缩放
        percentage_frame = ttk.Frame(self.resize_options_frame)
        percentage_frame.pack(fill='x', pady=2)
        ttk.Radiobutton(
            percentage_frame, text="按比例:", 
            variable=self.resize_type_var, value="percentage"
        ).pack(side='left')
        self.percentage_var = tk.IntVar(value=self.config['resize']['percentage'])
        ttk.Entry(percentage_frame, textvariable=self.percentage_var, width=8).pack(side='left', padx=(5, 2))
        ttk.Label(percentage_frame, text="%").pack(side='left')
        
        self._on_resize_enable_change()
        
    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="取消", command=self._on_cancel).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="导出", command=self._on_export).pack(side='right')
        
    def _browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_dir_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.output_dir_var.set(directory)
            
    def _on_naming_change(self):
        """命名规则变化事件"""
        naming_type = self.naming_var.get()
        
        # 启用/禁用输入框
        if naming_type == "prefix":
            self.prefix_entry.config(state='normal')
            self.suffix_entry.config(state='disabled')
        elif naming_type == "suffix":
            self.prefix_entry.config(state='disabled')
            self.suffix_entry.config(state='normal')
        else:
            self.prefix_entry.config(state='disabled')
            self.suffix_entry.config(state='disabled')
            
        self._update_preview()
        
    def _update_preview(self, *args):
        """更新文件名预览"""
        naming_type = self.naming_var.get()
        example_name = "example"
        
        if naming_type == "prefix":
            preview_name = f"{self.prefix_var.get()}{example_name}"
        elif naming_type == "suffix":
            preview_name = f"{example_name}{self.suffix_var.get()}"
        else:
            preview_name = example_name
            
        # 添加扩展名
        format_ext = ".jpg" if self.format_var.get() == "JPEG" else ".png"
        preview_name += format_ext
        
        self.preview_label.config(text=f"预览: {preview_name}")
        
    def _on_format_change(self):
        """格式变化事件"""
        is_jpeg = self.format_var.get() == "JPEG"
        
        # 显示/隐藏JPEG质量设置
        if is_jpeg:
            self.quality_frame.pack(fill='x', padx=10, pady=5)
        else:
            self.quality_frame.pack_forget()
            
        self._update_preview()
        
    def _on_quality_change(self, value):
        """质量变化事件"""
        self.quality_label.config(text=f"{int(float(value))}")
        
    def _on_resize_enable_change(self):
        """缩放启用状态变化事件"""
        enabled = self.resize_enabled_var.get()
        
        # 启用/禁用缩放选项
        for widget in self.resize_options_frame.winfo_children():
            self._set_widget_state(widget, 'normal' if enabled else 'disabled')
            
    def _set_widget_state(self, widget, state):
        """递归设置组件状态"""
        try:
            widget.config(state=state)
        except:
            pass
            
        for child in widget.winfo_children():
            self._set_widget_state(child, state)
            
    def _on_export(self):
        """导出按钮点击事件"""
        # 验证设置
        if not self.output_dir_var.get():
            messagebox.showerror("错误", "请选择输出目录")
            return
            
        if not os.path.exists(self.output_dir_var.get()):
            messagebox.showerror("错误", "输出目录不存在")
            return
            
        # 收集配置
        naming_rule = {
            'type': self.naming_var.get(),
            'value': ''
        }
        
        if naming_rule['type'] == 'prefix':
            naming_rule['value'] = self.prefix_var.get()
        elif naming_rule['type'] == 'suffix':
            naming_rule['value'] = self.suffix_var.get()
            
        resize_config = {
            'enabled': self.resize_enabled_var.get(),
            'type': self.resize_type_var.get(),
            'width': self.width_var.get(),
            'height': self.height_var.get(),
            'percentage': self.percentage_var.get(),
            'keep_ratio': True
        }
        
        self.result = {
            'output_dir': self.output_dir_var.get(),
            'naming_rule': naming_rule,
            'output_format': self.format_var.get(),
            'quality': self.quality_var.get(),
            'resize': resize_config
        }
        
        # 调用导出回调
        if self.on_export:
            self.on_export(self.result)
            
        self._close()
        
    def _on_cancel(self):
        """取消按钮点击事件"""
        self.result = None
        self._close()
        
    def _close(self):
        """关闭对话框"""
        try:
            self.dialog.grab_release()
            self.dialog.destroy()
        except:
            pass
            
    def show(self) -> Optional[Dict]:
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result
