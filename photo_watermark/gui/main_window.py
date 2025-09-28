"""
主窗口

PhotoWatermark GUI应用的主界面。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import List, Optional

try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

from .widgets.drag_drop import DragDropFrame
from .widgets.thumbnail import ThumbnailList
from .widgets.progress import ProgressDialog
from .file_manager import FileManager
from .export_dialog import ExportDialog
from ..core.config import Config, Position, DateFormat
from ..core.image_processor import ImageProcessor


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        # 使用TkinterDnD来支持拖拽功能
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
            print("警告: tkinterdnd2 未安装，拖拽功能将不可用")
            
        self.file_manager = FileManager()
        self.config = Config()
        self.image_processor = None
        
        # 设置窗口
        self._setup_window()
        
        # 创建界面
        self._create_widgets()
        
        # 绑定事件
        self._bind_events()
        
    def _setup_window(self):
        """设置主窗口"""
        self.root.title("PhotoWatermark - 图片水印工具")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 设置图标（如果有的话）
        try:
            # self.root.iconbitmap("icon.ico")
            pass
        except:
            pass
            
    def _create_widgets(self):
        """创建界面组件"""
        # 创建菜单栏
        self._create_menu()
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建主要区域
        self._create_main_area()
        
        # 创建状态栏
        self._create_status_bar()
        
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入文件...", command=self._import_files, accelerator="Ctrl+O")
        file_menu.add_command(label="导入文件夹...", command=self._import_folder, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="导出...", command=self._export_images, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="全选", command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="清空列表", command=self._clear_list, accelerator="Ctrl+L")
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="缩略图视图", command=lambda: self._switch_view("thumbnail"))
        view_menu.add_command(label="列表视图", command=lambda: self._switch_view("list"))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
        
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # 导入按钮
        ttk.Button(
            toolbar, text="导入文件", 
            command=self._import_files
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            toolbar, text="导入文件夹", 
            command=self._import_folder
        ).pack(side='left', padx=(0, 5))
        
        # 分隔符
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # 导出按钮
        ttk.Button(
            toolbar, text="导出图片", 
            command=self._export_images,
            state='disabled'
        ).pack(side='left', padx=(0, 5))
        
        # 分隔符
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # 设置按钮
        ttk.Button(
            toolbar, text="水印设置", 
            command=self._show_watermark_settings
        ).pack(side='left', padx=(0, 5))
        
        # 右侧信息
        info_frame = ttk.Frame(toolbar)
        info_frame.pack(side='right')
        
        self.file_count_label = ttk.Label(info_frame, text="已导入: 0 张图片")
        self.file_count_label.pack(side='right')
        
    def _create_main_area(self):
        """创建主要区域"""
        # 创建水平分割面板
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 左侧设置面板
        self._create_settings_panel(main_paned)
        
        # 右侧图片区域
        self._create_image_area(main_paned)
        
    def _create_settings_panel(self, parent):
        """创建左侧设置面板"""
        settings_frame = ttk.Frame(parent, width=300)
        settings_frame.pack_propagate(False)
        parent.add(settings_frame, weight=0)
        
        # 设置面板标题
        ttk.Label(
            settings_frame, 
            text="设置面板", 
            font=('Arial', 12, 'bold')
        ).pack(pady=(10, 20))
        
        # 导入设置
        import_frame = ttk.LabelFrame(settings_frame, text="导入设置")
        import_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(
            import_frame, 
            text="递归导入子文件夹", 
            variable=self.recursive_var
        ).pack(anchor='w', padx=10, pady=5)
        
        # 水印设置（简化版）
        watermark_frame = ttk.LabelFrame(settings_frame, text="水印设置")
        watermark_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # 字体颜色
        ttk.Label(watermark_frame, text="字体颜色:").pack(anchor='w', padx=10, pady=(5, 0))
        self.color_var = tk.StringVar(value="white")
        color_combo = ttk.Combobox(
            watermark_frame, 
            textvariable=self.color_var,
            values=["white", "black", "red", "blue", "green", "yellow"],
            state="readonly"
        )
        color_combo.pack(fill='x', padx=10, pady=(0, 5))
        
        # 位置
        ttk.Label(watermark_frame, text="水印位置:").pack(anchor='w', padx=10, pady=(5, 0))
        self.position_var = tk.StringVar(value="bottom-right")
        position_combo = ttk.Combobox(
            watermark_frame,
            textvariable=self.position_var,
            values=["top-left", "top-center", "top-right", 
                   "center-left", "center", "center-right",
                   "bottom-left", "bottom-center", "bottom-right"],
            state="readonly"
        )
        position_combo.pack(fill='x', padx=10, pady=(0, 5))
        
        # 透明度
        ttk.Label(watermark_frame, text="透明度:").pack(anchor='w', padx=10, pady=(5, 0))
        self.alpha_var = tk.DoubleVar(value=0.8)
        alpha_scale = ttk.Scale(
            watermark_frame,
            from_=0.1, to=1.0,
            variable=self.alpha_var,
            orient='horizontal'
        )
        alpha_scale.pack(fill='x', padx=10, pady=(0, 5))
        
        # 高级设置按钮
        ttk.Button(
            watermark_frame,
            text="高级设置...",
            command=self._show_watermark_settings
        ).pack(pady=10)
        
    def _create_image_area(self, parent):
        """创建右侧图片区域"""
        image_frame = ttk.Frame(parent)
        parent.add(image_frame, weight=1)
        
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(image_frame)
        notebook.pack(fill='both', expand=True)
        
        # 拖拽导入标签页
        drag_frame = ttk.Frame(notebook)
        notebook.add(drag_frame, text="导入图片")
        
        # 创建拖拽区域
        self.drag_drop = DragDropFrame(drag_frame, self._on_files_dropped)
        self.drag_drop.pack(fill='both', expand=True)
        
        # 添加导入按钮
        button_frame = ttk.Frame(drag_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            button_frame, 
            text="选择文件", 
            command=self._import_files
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="选择文件夹", 
            command=self._import_folder
        ).pack(side='left')
        
        # 图片列表标签页
        list_frame = ttk.Frame(notebook)
        notebook.add(list_frame, text="图片列表")
        
        # 创建缩略图列表
        self.thumbnail_list = ThumbnailList(list_frame, self._on_selection_change)
        self.thumbnail_list.pack(fill='both', expand=True)
        
        # 保存notebook引用
        self.notebook = notebook
        
    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(status_frame, text="准备就绪")
        self.status_label.pack(side='left', padx=5, pady=2)
        
        # 进度条（隐藏）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            length=200
        )
        # 默认不显示进度条
        
    def _bind_events(self):
        """绑定事件"""
        # 键盘快捷键
        self.root.bind('<Control-o>', lambda e: self._import_files())
        self.root.bind('<Control-O>', lambda e: self._import_folder())
        self.root.bind('<Control-e>', lambda e: self._export_images())
        self.root.bind('<Control-a>', lambda e: self._select_all())
        self.root.bind('<Control-l>', lambda e: self._clear_list())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
    def _import_files(self):
        """导入文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=file_types
        )
        
        if files:
            self._add_files(list(files))
            
    def _import_folder(self):
        """导入文件夹"""
        folder = filedialog.askdirectory(title="选择图片文件夹")
        
        if folder:
            recursive = self.recursive_var.get()
            image_files = self.file_manager.get_images_from_directory(folder, recursive)
            
            if image_files:
                self._add_files(image_files)
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")
                
    def _add_files(self, file_paths: List[str]):
        """添加文件到列表"""
        print(f"DEBUG: 收到文件路径: {file_paths}")  # 调试信息
        
        # 展开目录中的文件
        all_files = []
        for path in file_paths:
            if os.path.isdir(path):
                print(f"DEBUG: 处理目录: {path}")
                # 从目录获取图片文件
                dir_files = self.file_manager.get_images_from_directory(path, recursive=False)
                all_files.extend(dir_files)
                print(f"DEBUG: 目录中找到 {len(dir_files)} 个图片文件")
            elif os.path.isfile(path):
                print(f"DEBUG: 处理文件: {path}")
                all_files.append(path)
        
        print(f"DEBUG: 展开后的文件列表: {all_files}")
        
        # 过滤支持的图片文件
        valid_files = []
        for f in all_files:
            is_supported = self.file_manager.is_supported_image(f)
            print(f"DEBUG: 文件 {f} 支持状态: {is_supported}")
            if is_supported:
                valid_files.append(f)
        
        print(f"DEBUG: 有效图片文件: {valid_files}")
        
        if valid_files:
            # 添加到缩略图列表
            self.thumbnail_list.add_files(valid_files)
            
            # 更新状态
            total_files = len(self.thumbnail_list.get_all_files())
            self.file_count_label.config(text=f"已导入: {total_files} 张图片")
            self.status_label.config(text=f"成功导入 {len(valid_files)} 张图片")
            
            # 切换到图片列表标签页
            self.notebook.select(1)
            
            # 启用导出按钮
            self._update_export_button()
            
        if len(valid_files) < len(all_files):
            skipped = len(all_files) - len(valid_files)
            if skipped > 0:
                messagebox.showwarning("警告", f"跳过了 {skipped} 个不支持的文件")
        
        if not valid_files and file_paths:
            messagebox.showinfo("提示", "没有找到支持的图片文件")
            
    def _on_files_dropped(self, file_paths: List[str]):
        """文件拖拽事件处理"""
        self._add_files(file_paths)
        
    def _on_selection_change(self, selected_files: List[str]):
        """选择变化事件处理"""
        count = len(selected_files)
        if count > 0:
            self.status_label.config(text=f"已选择 {count} 张图片")
        else:
            self.status_label.config(text="准备就绪")
            
    def _select_all(self):
        """全选"""
        self.thumbnail_list._select_all()
        
    def _clear_list(self):
        """清空列表"""
        result = messagebox.askyesno("确认", "确定要清空图片列表吗？")
        if result:
            self.thumbnail_list._clear_all()
            self.file_count_label.config(text="已导入: 0 张图片")
            self.status_label.config(text="已清空列表")
            self._update_export_button()
            
    def _switch_view(self, view_type: str):
        """切换视图"""
        self.thumbnail_list.view_var.set(view_type)
        self.thumbnail_list._switch_view()
        
    def _update_export_button(self):
        """更新导出按钮状态"""
        has_files = len(self.thumbnail_list.get_all_files()) > 0
        
        # 查找工具栏中的导出按钮并更新状态
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child.cget('text') == '导出图片':
                        child.config(state='normal' if has_files else 'disabled')
                        break
                        
    def _export_images(self):
        """导出图片"""
        all_files = self.thumbnail_list.get_all_files()
        selected_files = self.thumbnail_list.get_selected_files()
        
        if not all_files:
            messagebox.showwarning("警告", "没有可导出的图片")
            return
            
        # 如果没有选择，则导出所有图片
        files_to_export = selected_files if selected_files else all_files
        
        # 显示导出设置对话框
        export_dialog = ExportDialog(self.root, on_export=self._start_export)
        config = export_dialog.show()
        
        if config:
            self._start_export_with_config(files_to_export, config)
            
    def _start_export(self, config: dict):
        """开始导出（从对话框回调）"""
        selected_files = self.thumbnail_list.get_selected_files()
        all_files = self.thumbnail_list.get_all_files()
        files_to_export = selected_files if selected_files else all_files
        
        self._start_export_with_config(files_to_export, config)
        
    def _start_export_with_config(self, files: List[str], config: dict):
        """使用指定配置开始导出"""
        # 验证输出目录
        is_valid, error_msg = self.file_manager.validate_output_directory(
            config['output_dir'], files
        )
        
        if not is_valid:
            messagebox.showerror("错误", error_msg)
            return
            
        # 创建进度对话框
        progress_dialog = ProgressDialog(
            self.root, 
            title="导出图片",
            on_cancel=self._cancel_export
        )
        
        # 更新水印配置
        self._update_watermark_config()
        
        # 创建图像处理器
        self.image_processor = ImageProcessor(self.config)
        
        # 开始异步处理
        self.file_manager.process_images_async(
            files,
            config['output_dir'],
            config['naming_rule'],
            config['output_format'],
            config['quality'],
            config['resize'],
            self.image_processor,
            progress_callback=progress_dialog.update_progress,
            complete_callback=lambda success, failed: self._export_complete(
                progress_dialog, success, failed
            )
        )
        
    def _update_watermark_config(self):
        """更新水印配置"""
        # 从界面获取设置并更新配置
        self.config.config.font_color = self.color_var.get()
        self.config.config.position = Position(self.position_var.get())
        self.config.config.font_alpha = self.alpha_var.get()
        
    def _cancel_export(self):
        """取消导出"""
        # 这里可以设置取消标志
        pass
        
    def _export_complete(self, progress_dialog: ProgressDialog, 
                        success_files: List[str], failed_files: List[str]):
        """导出完成回调"""
        total = len(success_files) + len(failed_files)
        success_count = len(success_files)
        
        if failed_files:
            message = f"导出完成！\\n成功: {success_count}/{total}\\n失败: {len(failed_files)} 张"
        else:
            message = f"导出完成！\\n成功处理 {success_count} 张图片"
            
        progress_dialog.complete(message)
        
        # 更新状态栏
        self.status_label.config(text=f"导出完成 - 成功: {success_count}, 失败: {len(failed_files)}")
        
        # 如果有失败的文件，显示详细信息
        if failed_files:
            failed_list = "\\n".join([os.path.basename(f) for f in failed_files[:10]])
            if len(failed_files) > 10:
                failed_list += f"\\n... 还有 {len(failed_files) - 10} 个文件"
                
            messagebox.showwarning(
                "部分文件处理失败", 
                f"以下文件处理失败:\\n{failed_list}"
            )
            
    def _show_watermark_settings(self):
        """显示水印高级设置"""
        # 这里可以打开更详细的水印设置对话框
        messagebox.showinfo("提示", "高级水印设置功能开发中...")
        
    def _show_about(self):
        """显示关于对话框"""
        about_text = """PhotoWatermark v2.0
        
基于EXIF拍摄时间的图片水印工具

功能特性:
• 自动提取图片EXIF时间信息
• 支持批量处理
• 丰富的水印样式选项
• 直观的图形界面
• 多种导出格式

开发: PhotoWatermark Team
版本: 2.0.0"""
        
        messagebox.showinfo("关于 PhotoWatermark", about_text)
        
    def run(self):
        """运行应用"""
        self.root.mainloop()
