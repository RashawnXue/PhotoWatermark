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
from .widgets.export_confirm import ExportConfirmDialog
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
        settings_frame = ttk.Frame(parent, width=350)
        settings_frame.pack_propagate(False)
        parent.add(settings_frame, weight=0)
        
        # 创建滚动框架
        canvas = tk.Canvas(settings_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局滚动组件 - 调整padding避免遮挡
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 0))
        scrollbar.pack(side="right", fill="y", padx=(5, 0))
        
        # 绑定鼠标滚轮事件到多个组件
        def _on_mousewheel(event):
            # 跨平台鼠标滚轮处理
            if event.delta:
                # Windows和macOS
                delta = int(-1 * (event.delta / 120))
            else:
                # Linux
                delta = -1 if event.num == 4 else 1
            canvas.yview_scroll(delta, "units")
            return "break"  # 阻止事件传播
        
        def _on_mousewheel_linux_up(event):
            canvas.yview_scroll(-1, "units")
            return "break"
            
        def _on_mousewheel_linux_down(event):
            canvas.yview_scroll(1, "units")
            return "break"
        
        def _bind_mousewheel_recursive(widget):
            """递归绑定鼠标滚轮事件到所有子组件"""
            # Windows和macOS
            widget.bind("<MouseWheel>", _on_mousewheel)
            # Linux
            widget.bind("<Button-4>", _on_mousewheel_linux_up)
            widget.bind("<Button-5>", _on_mousewheel_linux_down)
            
            for child in widget.winfo_children():
                _bind_mousewheel_recursive(child)
        
        # 绑定到主要组件
        _bind_mousewheel_recursive(settings_frame)
        _bind_mousewheel_recursive(canvas)
        
        # 延迟绑定子组件（等待组件创建完成）
        def _bind_children():
            _bind_mousewheel_recursive(scrollable_frame)
        
        settings_frame.after(100, _bind_children)
        
        # 设置面板标题
        ttk.Label(
            scrollable_frame, 
            text="设置面板", 
            font=('Arial', 12, 'bold')
        ).pack(pady=(10, 20))
        
        # 导入设置
        import_frame = ttk.LabelFrame(scrollable_frame, text="导入设置")
        import_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(
            import_frame, 
            text="递归导入子文件夹", 
            variable=self.recursive_var
        ).pack(anchor='w', padx=10, pady=5)
        
        # 水印设置（简化版）
        watermark_frame = ttk.LabelFrame(scrollable_frame, text="水印设置")
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
        
        # 导出设置
        export_frame = ttk.LabelFrame(scrollable_frame, text="导出设置")
        export_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # 输出目录
        ttk.Label(export_frame, text="输出目录:").pack(anchor='w', padx=10, pady=(5, 0))
        dir_frame = ttk.Frame(export_frame)
        dir_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        self.output_dir_var = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        dir_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            dir_frame, 
            text="浏览", 
            command=self._browse_output_dir,
            width=6
        ).pack(side='right', padx=(5, 0))
        
        # 输出格式
        ttk.Label(export_frame, text="输出格式:").pack(anchor='w', padx=10, pady=(5, 0))
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        self.format_var = tk.StringVar(value="JPEG")
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.format_var, value="JPEG", command=self._on_format_change).pack(side='left')
        ttk.Radiobutton(format_frame, text="PNG", variable=self.format_var, value="PNG", command=self._on_format_change).pack(side='left', padx=(10, 0))
        
        # JPEG质量设置
        self.quality_frame = ttk.Frame(export_frame)
        self.quality_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        self.quality_label_title = ttk.Label(self.quality_frame, text="JPEG质量:")
        self.quality_label_title.pack(anchor='w')
        quality_scale_frame = ttk.Frame(self.quality_frame)
        quality_scale_frame.pack(fill='x', pady=(0, 5))
        
        self.quality_var = tk.IntVar(value=95)
        self.quality_scale = ttk.Scale(
            quality_scale_frame,
            from_=1, to=100,
            variable=self.quality_var,
            orient='horizontal'
        )
        self.quality_scale.pack(side='left', fill='x', expand=True)
        
        self.quality_label = ttk.Label(quality_scale_frame, text="95%")
        self.quality_label.pack(side='right', padx=(5, 0))
        
        # 绑定质量滑块变化事件
        self.quality_scale.configure(command=self._on_quality_change)
        
        # 文件命名
        ttk.Label(export_frame, text="文件命名:").pack(anchor='w', padx=10, pady=(5, 0))
        self.naming_var = tk.StringVar(value="original")
        
        naming_frame1 = ttk.Frame(export_frame)
        naming_frame1.pack(fill='x', padx=10, pady=(0, 2))
        ttk.Radiobutton(naming_frame1, text="保留原文件名", variable=self.naming_var, value="original").pack(anchor='w')
        
        naming_frame2 = ttk.Frame(export_frame)
        naming_frame2.pack(fill='x', padx=10, pady=(0, 2))
        ttk.Radiobutton(naming_frame2, text="添加前缀:", variable=self.naming_var, value="prefix").pack(side='left')
        self.prefix_var = tk.StringVar(value="wm_")
        ttk.Entry(naming_frame2, textvariable=self.prefix_var, width=10).pack(side='left', padx=(5, 0))
        
        naming_frame3 = ttk.Frame(export_frame)
        naming_frame3.pack(fill='x', padx=10, pady=(0, 5))
        ttk.Radiobutton(naming_frame3, text="添加后缀:", variable=self.naming_var, value="suffix").pack(side='left')
        self.suffix_var = tk.StringVar(value="_watermarked")
        ttk.Entry(naming_frame3, textvariable=self.suffix_var, width=12).pack(side='left', padx=(5, 0))
        
        # 图片尺寸调整
        ttk.Label(export_frame, text="图片尺寸:").pack(anchor='w', padx=10, pady=(5, 0))
        
        # 启用尺寸调整复选框
        self.resize_enabled_var = tk.BooleanVar(value=False)
        resize_check = ttk.Checkbutton(
            export_frame,
            text="启用图片尺寸调整",
            variable=self.resize_enabled_var,
            command=self._on_resize_enable_change
        )
        resize_check.pack(anchor='w', padx=10, pady=(0, 5))
        
        # 尺寸调整选项框架
        self.resize_options_frame = ttk.Frame(export_frame)
        self.resize_options_frame.pack(fill='x', padx=20, pady=(0, 5))
        
        # 调整类型
        self.resize_type_var = tk.StringVar(value="percentage")
        
        # 按百分比缩放
        percentage_frame = ttk.Frame(self.resize_options_frame)
        percentage_frame.pack(fill='x', pady=2)
        ttk.Radiobutton(
            percentage_frame, text="按比例:", 
            variable=self.resize_type_var, value="percentage"
        ).pack(side='left')
        self.percentage_var = tk.IntVar(value=100)
        percentage_entry = ttk.Entry(percentage_frame, textvariable=self.percentage_var, width=8)
        percentage_entry.pack(side='left', padx=(5, 2))
        ttk.Label(percentage_frame, text="%").pack(side='left')
        
        # 按尺寸缩放
        size_frame = ttk.Frame(self.resize_options_frame)
        size_frame.pack(fill='x', pady=2)
        ttk.Radiobutton(
            size_frame, text="按尺寸:", 
            variable=self.resize_type_var, value="custom"
        ).pack(side='left')
        
        # 宽度输入
        ttk.Label(size_frame, text="宽:").pack(side='left', padx=(10, 2))
        self.width_var = tk.IntVar(value=1920)
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=6)
        width_entry.pack(side='left', padx=(0, 2))
        ttk.Label(size_frame, text="px").pack(side='left', padx=(0, 10))
        
        # 高度输入
        ttk.Label(size_frame, text="高:").pack(side='left', padx=(0, 2))
        self.height_var = tk.IntVar(value=1080)
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=6)
        height_entry.pack(side='left', padx=(0, 2))
        ttk.Label(size_frame, text="px").pack(side='left')
        
        
        # 初始化显示状态
        self._on_resize_enable_change()
        
        # 初始化格式相关显示
        self._on_format_change()
        
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
        self.thumbnail_list = ThumbnailList(
            list_frame, 
            self._on_selection_change,
            self._on_list_change  # 添加列表变化回调
        )
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
        # 展开目录中的文件
        all_files = []
        for path in file_paths:
            if os.path.isdir(path):
                # 从目录获取图片文件
                recursive = self.recursive_var.get() if hasattr(self, 'recursive_var') else False
                dir_files = self.file_manager.get_images_from_directory(path, recursive)
                all_files.extend(dir_files)
            elif os.path.isfile(path):
                all_files.append(path)
        
        # 过滤支持的图片文件
        valid_files = [f for f in all_files if self.file_manager.is_supported_image(f)]
        
        if valid_files:
            # 添加到缩略图列表（会自动触发列表变化回调更新计数器）
            self.thumbnail_list.add_files(valid_files)
            
            # 更新状态信息
            self.status_label.config(text=f"成功导入 {len(valid_files)} 张图片")
            
            # 切换到图片列表标签页
            self.notebook.select(1)
            
        # 显示跳过的文件信息
        if len(valid_files) < len(all_files):
            skipped = len(all_files) - len(valid_files)
            if skipped > 0:
                messagebox.showwarning("警告", f"跳过了 {skipped} 个不支持的文件")
        
        # 如果没有找到任何有效文件，显示提示
        if not valid_files and file_paths:
            messagebox.showinfo("提示", "没有找到支持的图片文件\\n支持的格式: JPEG, PNG, BMP, TIFF")
            
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
            
    def _on_list_change(self):
        """列表变化事件处理"""
        # 更新文件计数器
        total_files = len(self.thumbnail_list.get_all_files())
        self.file_count_label.config(text=f"已导入: {total_files} 张图片")
        
        # 更新导出按钮状态
        self._update_export_button()
        
        # 如果列表为空，更新状态
        if total_files == 0:
            self.status_label.config(text="已清空列表")
        
    def _browse_output_dir(self):
        """浏览输出目录"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_dir_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.output_dir_var.set(directory)
            
    def _on_format_change(self):
        """格式改变事件"""
        if hasattr(self, 'quality_frame'):
            if self.format_var.get() == "JPEG":
                # 启用JPEG质量控件
                self.quality_label_title.config(state='normal', foreground='black')
                self.quality_scale.config(state='normal')
                self.quality_label.config(state='normal', foreground='black')
            else:
                # 禁用JPEG质量控件（PNG格式）
                self.quality_label_title.config(state='disabled', foreground='gray')
                self.quality_scale.config(state='disabled')
                self.quality_label.config(state='disabled', foreground='gray')
                
    def _on_quality_change(self, value):
        """质量滑块改变事件"""
        if hasattr(self, 'quality_label'):
            self.quality_label.config(text=f"{int(float(value))}%")
            
    def _on_resize_enable_change(self):
        """尺寸调整启用状态改变事件"""
        if hasattr(self, 'resize_options_frame'):
            if self.resize_enabled_var.get():
                # 启用尺寸调整选项
                for child in self.resize_options_frame.winfo_children():
                    self._enable_widget_recursive(child)
            else:
                # 禁用尺寸调整选项
                for child in self.resize_options_frame.winfo_children():
                    self._disable_widget_recursive(child)
                    
    def _enable_widget_recursive(self, widget):
        """递归启用控件"""
        try:
            widget.config(state='normal')
        except:
            pass
        for child in widget.winfo_children():
            self._enable_widget_recursive(child)
            
    def _disable_widget_recursive(self, widget):
        """递归禁用控件"""
        try:
            widget.config(state='disabled')
        except:
            pass
        for child in widget.winfo_children():
            self._disable_widget_recursive(child)
            
    def _select_all(self):
        """全选"""
        self.thumbnail_list._select_all()
        
    def _clear_list(self):
        """清空列表"""
        result = messagebox.askyesno("确认", "确定要清空图片列表吗？")
        if result:
            # 清空列表（会自动触发列表变化回调更新计数器和状态）
            self.thumbnail_list._clear_all()
            
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
        
        # 从设置面板获取配置
        config = self._get_export_config()
        
        # 直接显示确认对话框
        self._show_export_confirmation(files_to_export, config)
        
    def _get_export_config(self) -> dict:
        """从设置面板获取导出配置"""
        # 收集文件命名规则
        naming_rule = {
            'type': self.naming_var.get(),
            'value': ''
        }
        
        if naming_rule['type'] == 'prefix':
            naming_rule['value'] = self.prefix_var.get()
        elif naming_rule['type'] == 'suffix':
            naming_rule['value'] = self.suffix_var.get()
            
        # 收集尺寸调整配置
        resize_config = {
            'enabled': self.resize_enabled_var.get(),
            'type': self.resize_type_var.get(),
            'width': self.width_var.get(),
            'height': self.height_var.get(),
            'percentage': self.percentage_var.get(),
            'keep_ratio': False
        }
        
        # 收集配置
        config = {
            'output_dir': self.output_dir_var.get(),
            'naming_rule': naming_rule,
            'output_format': self.format_var.get(),
            'quality': self.quality_var.get(),
            'resize': resize_config
        }
        
        return config
            
    def _start_export(self, config: dict):
        """开始导出（从对话框回调）"""
        selected_files = self.thumbnail_list.get_selected_files()
        all_files = self.thumbnail_list.get_all_files()
        files_to_export = selected_files if selected_files else all_files
        
        self._show_export_confirmation(files_to_export, config)
        
    def _show_export_confirmation(self, files: List[str], config: dict):
        """显示导出确认对话框"""
        confirm_dialog = ExportConfirmDialog(
            self.root, 
            files, 
            config, 
            on_confirm=None  # 不使用回调，避免重复调用
        )
        result = confirm_dialog.show()
        
        if result == 'modify':
            # 用户选择修改设置，提示在左侧面板修改
            messagebox.showinfo("提示", "请在左侧设置面板中修改导出设置，然后重新点击导出按钮。")
        elif result is True:
            # 用户确认导出，开始实际导出过程
            self._start_export_with_config(files, config)
        # result is False 表示用户取消，不做任何操作
        
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
