"""
主窗口

PhotoWatermark GUI应用的主界面。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from typing import List, Optional, Tuple

try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

from .widgets.drag_drop import DragDropFrame
from .widgets.thumbnail import ThumbnailList
from .widgets.progress import ProgressDialog
from .widgets.export_confirm import ExportConfirmDialog
from .widgets.enhanced_color_selector import EnhancedColorSelector, ColorSelectorWithLabel
from .widgets.font_preview import FontSelector
from .file_manager import FileManager
from .export_dialog import ExportDialog
from ..core.config import Config, Position, DateFormat
from ..core.template_manager import TemplateManager
from ..core.image_processor import ImageProcessor
from ..utils.font_manager import font_manager


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
        # Template manager for saving/loading templates and last session
        try:
            self.template_manager = TemplateManager()
        except Exception:
            self.template_manager = None
        self.image_processor = None
        # 当前自定义坐标（像素，基于原始图片尺寸）
        self.custom_position: Optional[Tuple[int, int]] = None
        # 按钮引用用于高亮当前预设位置
        self._position_buttons = {}
        # 保存最近一次预览的显示信息（用于坐标映射）
        self._last_preview_info = None
        # 拖拽状态
        self._dragging = False
        self._drag_offset = (0, 0)
        
        # 设置窗口
        self._setup_window()
        
        # 创建界面
        self._create_widgets()
        
        # 绑定事件
        self._bind_events()
        # Try to auto-restore last session
        try:
            if self.template_manager:
                last = self.template_manager.load_last_session()
                if last:
                    # apply loaded config to GUI
                    self._apply_config_to_gui(last)
        except Exception:
            pass

        # If no last session, try loading a default template (if configured)
        try:
            if self.template_manager and not getattr(self, 'config_loaded_from_last', False):
                default_cfg = self.template_manager.load_default_template()
                if default_cfg:
                    self._apply_config_to_gui(default_cfg)
        except Exception:
            pass

        # bind exit to save last session
        try:
            self.root.protocol('WM_DELETE_WINDOW', self._on_app_close)
        except Exception:
            pass

    def _setup_window(self):
        """设置主窗口"""
        self.root.title("PhotoWatermark - 图片水印工具")
        self.root.geometry("1400x900")  # 增加默认窗口大小
        self.root.minsize(1000, 700)   # 增加最小窗口大小
        
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
        self._bind_events()
        self._create_main_area()
        self._create_status_bar()
        
    def _create_main_area(self):
        """创建主要区域"""
        # 创建水平分割面板
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)

        # 左侧设置面板
        self._create_settings_panel(main_paned)

        # 右侧图片区域
        self._create_image_area(main_paned)

        # 设置初始分割位置 - 增加左侧面板宽度 (调整为原来的130%)
        self.root.after(100, lambda: main_paned.sashpos(0, 520))

    def _create_settings_panel(self, parent):
        """创建左侧设置面板"""
        settings_frame = ttk.Frame(parent)
        parent.add(settings_frame, weight=0)

        # 设置最小宽度 (调整为原来的130%)
        settings_frame.config(width=520)

        # 创建滚动框架
        canvas = tk.Canvas(settings_frame, highlightthickness=0, bg='white')
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # 配置滚动区域
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 确保内容框架宽度与画布一致
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # 确保画布已经渲染
                canvas.itemconfig(window_id, width=canvas_width)

        scrollable_frame.bind("<Configure>", configure_scroll_region)
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 画布大小改变时调整内容宽度
        canvas.bind('<Configure>', configure_scroll_region)

        # 布局滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # 为画布和滚动框架绑定滚轮事件
        canvas.bind("<MouseWheel>", on_mousewheel)  # Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux

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

        # 水印设置
        self._create_watermark_settings(scrollable_frame)
        # 模板设置（嵌入在设置面板下方）
        self._create_template_settings(scrollable_frame)

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

        # 主预览区域（在右侧图片区域下方）
        preview_frame = ttk.LabelFrame(image_frame, text="主预览")
        preview_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.preview_canvas = tk.Canvas(preview_frame, bg='black')
        self.preview_canvas.pack(fill='both', expand=True)

        # 初始化预览显示
        self._init_preview_area()

    def _create_status_bar(self):
        """创建并初始化底部状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side='bottom', fill='x')

        self.status_label = ttk.Label(status_frame, text="准备就绪")
        self.status_label.pack(side='left', padx=10, pady=4)

    

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
        file_menu.add_command(label="退出", command=self._on_app_close, accelerator="Ctrl+Q")
        
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
        
        # 模板菜单
        templates_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="模板", menu=templates_menu)
        templates_menu.add_command(label="保存为模板...", command=self._save_template_dialog)
        templates_menu.add_command(label="模板管理器...", command=self._open_template_manager)
        templates_menu.add_separator()
        templates_menu.add_command(label="导入模板...", command=lambda: messagebox.showinfo("提示", "导入模板功能暂未实现"))
        
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
        
        
    def _bind_events(self):
        """绑定事件"""
        # 键盘快捷键
        self.root.bind('<Control-o>', lambda e: self._import_files())
        self.root.bind('<Control-O>', lambda e: self._import_folder())
        self.root.bind('<Control-e>', lambda e: self._export_images())
        self.root.bind('<Control-a>', lambda e: self._select_all())
        self.root.bind('<Control-l>', lambda e: self._clear_list())
        self.root.bind('<Control-q>', lambda e: self._on_app_close())
        
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
            messagebox.showinfo("提示", "没有找到支持的图片文件\n支持的格式: JPEG, PNG, BMP, TIFF")
            
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
        # 更新主预览区域，选中变化应立即反映
        try:
            self._update_preview_image(selected_files)
        except Exception:
            pass
            
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
        
    def _get_watermark_config(self):
        """从GUI获取水印配置"""
        from ..core.config import WatermarkConfig, WatermarkType, TextWatermarkConfig, ImageWatermarkConfig, Position, DateFormat, ScaleMode

        # 获取文本和图片水印内容
        text_content = self.text_content_var.get() if hasattr(self, 'text_content_var') else ""
        image_path = self.image_path_var.get() if hasattr(self, 'image_path_var') else ""

        # 判断水印类型：无文本且无图片时自动用时间水印
        if (not text_content.strip()) and (not image_path.strip()):
            watermark_type = WatermarkType.TIMESTAMP
        else:
            current_tab = self.watermark_notebook.index(self.watermark_notebook.select())
            if current_tab == 1 and text_content.strip():
                watermark_type = WatermarkType.TEXT
            elif current_tab == 2 and image_path.strip():
                watermark_type = WatermarkType.IMAGE
            else:
                watermark_type = WatermarkType.TIMESTAMP

        # 获取选中字体的路径
        selected_font_name = self.text_font_var.get() if hasattr(self, 'text_font_var') else ""
        selected_font_path = None
        if hasattr(self, 'recommended_fonts'):
            for font_info in self.recommended_fonts:
                if font_info['name'] == selected_font_name:
                    selected_font_path = font_info['path']
                    break

        # 创建文本水印配置
        text_watermark = TextWatermarkConfig(
            text=text_content,
            font_size=self.text_font_size_var.get() if hasattr(self, 'text_font_size_var') else 36,
            font_color=self.text_color_var.get() if hasattr(self, 'text_color_var') else "white",
            font_alpha=self.text_alpha_var.get() if hasattr(self, 'text_alpha_var') else 0.8,
            font_path=selected_font_path,
            font_name=selected_font_name,
            font_bold=self.text_bold_var.get() if hasattr(self, 'text_bold_var') else False,
            font_italic=self.text_italic_var.get() if hasattr(self, 'text_italic_var') else False,
            shadow_enabled=self.shadow_enabled_var.get() if hasattr(self, 'shadow_enabled_var') else False,
            shadow_offset_x=self.shadow_offset_x_var.get() if hasattr(self, 'shadow_offset_x_var') else 2,
            shadow_offset_y=self.shadow_offset_y_var.get() if hasattr(self, 'shadow_offset_y_var') else 2,
            stroke_enabled=self.stroke_enabled_var.get() if hasattr(self, 'stroke_enabled_var') else False,
            stroke_width=self.stroke_width_var.get() if hasattr(self, 'stroke_width_var') else 1
        )

        # 创建图片水印配置
        scale_mode_str = self.scale_mode_var.get() if hasattr(self, 'scale_mode_var') else "percentage"
        scale_mode = ScaleMode.PERCENTAGE if scale_mode_str == "percentage" else ScaleMode.PIXEL

        image_watermark = ImageWatermarkConfig(
            image_path=image_path,
            scale_mode=scale_mode,
            scale_percentage=self.scale_percentage_var.get() if hasattr(self, 'scale_percentage_var') else 20.0,
            scale_width=self.scale_width_var.get() if hasattr(self, 'scale_width_var') else 100,
            scale_height=self.scale_height_var.get() if hasattr(self, 'scale_height_var') else 100,
            keep_aspect_ratio=self.keep_ratio_var.get() if hasattr(self, 'keep_ratio_var') else True,
            alpha=self.image_alpha_var.get() if hasattr(self, 'image_alpha_var') else 0.8
        )

        # 解析位置（如果用户选择了自定义坐标，Position(...) 可能会抛出异常）
        position_str = self.position_var.get()
        try:
            position = Position(position_str)
        except Exception:
            # 允许非枚举的中间状态（例如 'custom'），在这种情况下保留现有配置或使用默认
            try:
                position = self.config.config.position
            except Exception:
                position = Position.BOTTOM_RIGHT

        # 额外的通用设置
        margin_val = None
        try:
            margin_val = int(self.margin_var.get()) if hasattr(self, 'margin_var') else None
        except Exception:
            margin_val = None

        # 日期格式（用于时间水印）
        date_format_val = None
        try:
            date_format_val = DateFormat(self.date_format_var.get()) if hasattr(self, 'date_format_var') else None
        except Exception:
            date_format_val = None

        # 决定时间水印的字体大小来源（时间水印使用 timestamp_font_size_var）
        chosen_font_size = None
        if watermark_type == WatermarkType.TIMESTAMP:
            chosen_font_size = self.timestamp_font_size_var.get() if hasattr(self, 'timestamp_font_size_var') else None
        else:
            chosen_font_size = self.text_font_size_var.get() if hasattr(self, 'text_font_size_var') else None

        # 创建主配置
        watermark_config = WatermarkConfig(
            watermark_type=watermark_type,
            position=position,
            font_size=chosen_font_size,
            font_path=selected_font_path,
            font_color=self.color_var.get() if hasattr(self, 'color_var') else "white",
            font_alpha=self.alpha_var.get() if hasattr(self, 'alpha_var') else 0.8,
            text_watermark=text_watermark,
            image_watermark=image_watermark
        )

        # apply optional common settings
        if margin_val is not None:
            watermark_config.margin = margin_val
        if date_format_val is not None:
            watermark_config.date_format = date_format_val

        # read advanced visual options if UI exposes them
        try:
            if hasattr(self, 'shadow_color_var'):
                watermark_config.text_watermark.shadow_color = self.shadow_color_var.get()
        except Exception:
            pass
        try:
            if hasattr(self, 'shadow_blur_var'):
                watermark_config.text_watermark.shadow_blur = int(self.shadow_blur_var.get())
        except Exception:
            pass
        try:
            if hasattr(self, 'shadow_alpha_var'):
                watermark_config.text_watermark.shadow_alpha = float(self.shadow_alpha_var.get())
        except Exception:
            pass
        try:
            if hasattr(self, 'stroke_color_var'):
                watermark_config.text_watermark.stroke_color = self.stroke_color_var.get()
        except Exception:
            pass
        try:
            if hasattr(self, 'flip_horizontal_var'):
                watermark_config.image_watermark.flip_horizontal = bool(self.flip_horizontal_var.get())
        except Exception:
            pass
        try:
            if hasattr(self, 'flip_vertical_var'):
                watermark_config.image_watermark.flip_vertical = bool(self.flip_vertical_var.get())
        except Exception:
            pass

        # 如果用户设置了自定义像素坐标，则将其写入配置，后端会优先使用 custom_position
        if hasattr(self, 'custom_position') and self.custom_position is not None:
            watermark_config.custom_position = self.custom_position

        # 写入旋转角度到文本和图片水印配置（支持所有类型的水印）
        try:
            rot_val = float(self.rotation_var.get()) if hasattr(self, 'rotation_var') else 0.0
        except Exception:
            rot_val = 0.0

        try:
            if watermark_config.text_watermark is not None:
                watermark_config.text_watermark.rotation = float(rot_val)
        except Exception:
            pass

        try:
            if watermark_config.image_watermark is not None:
                watermark_config.image_watermark.rotation = float(rot_val)
        except Exception:
            pass

        return watermark_config

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
        # 获取新的水印配置
        watermark_config = self._get_watermark_config()
        
        # 更新配置对象
        from ..core.config import Config
        self.config = Config(watermark_config)
        
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
            message = f"导出完成！\n成功: {success_count}/{total}\n失败: {len(failed_files)} 张"
        else:
            message = f"导出完成！\n成功处理 {success_count} 张图片"
            
        progress_dialog.complete(message)
        
        # 更新状态栏
        self.status_label.config(text=f"导出完成 - 成功: {success_count}, 失败: {len(failed_files)}")
        
        # 如果有失败的文件，显示详细信息
        if failed_files:
            failed_list = "\n".join([os.path.basename(f) for f in failed_files[:10]])
            if len(failed_files) > 10:
                failed_list += f"\n... 还有 {len(failed_files) - 10} 个文件"
                
            messagebox.showwarning(
                "部分文件处理失败", 
                f"以下文件处理失败:\n{failed_list}"
            )
            
    def _create_watermark_settings(self, parent):
        """创建水印设置界面"""
        watermark_frame = ttk.LabelFrame(parent, text="水印设置")
        watermark_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # 创建选项卡
        self.watermark_notebook = ttk.Notebook(watermark_frame)
        self.watermark_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        # 时间水印选项卡
        self._create_timestamp_watermark_tab()
        
        # 文本水印选项卡
        self._create_text_watermark_tab()
        
        # 图片水印选项卡
        self._create_image_watermark_tab()
        
        # 通用位置设置
        self._create_position_settings(watermark_frame)
    
    def _create_timestamp_watermark_tab(self):
        """创建时间水印选项卡"""
        timestamp_frame = ttk.Frame(self.watermark_notebook)
        self.watermark_notebook.add(timestamp_frame, text="时间水印")
        
        # 字体颜色
        color_frame = ttk.Frame(timestamp_frame)
        color_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        self.color_var = tk.StringVar(value="white")
        self.timestamp_color_selector = ColorSelectorWithLabel(
            color_frame,
            label_text="字体颜色:",
            initial_color="white",
            on_color_change=lambda color: (self.color_var.set(color), self._schedule_redraw()),
            label_width=8
        )
        self.timestamp_color_selector.pack(fill='x')

        # 透明度
        ttk.Label(timestamp_frame, text="透明度:").pack(anchor='w', padx=10, pady=(5, 0))
        self.alpha_var = tk.DoubleVar(value=0.8)
        alpha_scale = ttk.Scale(
            timestamp_frame,
            from_=0.1, to=1.0,
            variable=self.alpha_var,
            orient='horizontal',
            command=lambda v: self._schedule_redraw()
        )
        alpha_scale.pack(fill='x', padx=10, pady=(0, 10))
        # 字体大小（用于时间水印）
        ttk.Label(timestamp_frame, text="字体大小:").pack(anchor='w', padx=10, pady=(0, 0))
        self.timestamp_font_size_var = tk.IntVar(value=36)
        ts_size_entry = ttk.Entry(timestamp_frame, textvariable=self.timestamp_font_size_var, width=8)
        ts_size_entry.pack(anchor='w', padx=10, pady=(0, 10))
        self.timestamp_font_size_var.trace_add('write', lambda *args: self._schedule_redraw())

        self._schedule_redraw()

    def _create_template_settings(self, parent):
        """在设置面板中嵌入模版设置区域（列表 + 操作按钮）。"""
        frame = ttk.LabelFrame(parent, text="模版设置")
        frame.pack(fill='x', padx=10, pady=(0, 10))

        left = ttk.Frame(frame)
        left.pack(side='left', fill='both', expand=True, padx=(5,0), pady=5)

        self.template_listbox = tk.Listbox(left, height=6)
        self.template_listbox.pack(fill='both', expand=True)

        sb = ttk.Scrollbar(left, orient='vertical', command=self.template_listbox.yview)
        sb.pack(side='right', fill='y')
        self.template_listbox.config(yscrollcommand=sb.set)

        right = ttk.Frame(frame)
        right.pack(side='right', fill='y', padx=5, pady=5)

        ttk.Button(right, text='应用', width=12, command=self._template_apply_selected).pack(pady=(0,5))
        ttk.Button(right, text='保存为模板', width=12, command=self._save_template_dialog).pack(pady=5)
        ttk.Button(right, text='设为默认', width=12, command=self._template_set_default_selected).pack(pady=5)
        ttk.Button(right, text='重命名', width=12, command=self._template_rename_selected).pack(pady=5)
        ttk.Button(right, text='删除', width=12, command=self._template_delete_selected).pack(pady=5)
        # info area below buttons
        self._template_info_label = ttk.Label(right, text='', wraplength=160, justify='left', foreground='gray')
        self._template_info_label.pack(side='bottom', pady=(10,0))

        # refresh list initially
        try:
            self._template_refresh_list()
        except Exception:
            pass

    def _on_rotation_slider(self, value: str):
        """当旋转滑块移动时，更新文本输入框并触发重绘"""
        try:
            # value may be string from Tk scale
            val = float(value)
            # normalize to -180..180
            if val > 180:
                val = 180.0
            if val < -180:
                val = -180.0
            # write back as integer-like string for the entry
            self.rotation_var.set(str(int(val)))
        except Exception:
            # ignore slider glitches
            pass
    
    def _create_text_watermark_tab(self):
        """创建文本水印选项卡"""
        text_frame = ttk.Frame(self.watermark_notebook)
        self.watermark_notebook.add(text_frame, text="文本水印")

        # 文本内容
        ttk.Label(text_frame, text="水印文本:").pack(anchor='w', padx=10, pady=(10, 0))
        self.text_content_var = tk.StringVar(value="")
        text_entry = tk.Text(text_frame, height=3, wrap=tk.WORD)
        text_entry.pack(fill='x', padx=10, pady=(0, 5))

        # 绑定文本变化事件：将 Text 内容同步到 StringVar 并刷新预览
        def on_text_change(event=None):
            content = text_entry.get("1.0", tk.END)
            if content.endswith('\n'):
                content = content[:-1]
            self.text_content_var.set(content)
            self._schedule_redraw()

        text_entry.bind('<KeyRelease>', on_text_change)
        self.text_entry_widget = text_entry

        # 字体设置
        font_frame = ttk.LabelFrame(text_frame, text="字体设置")
        font_frame.pack(fill='x', padx=10, pady=(5, 0))

        # 获取推荐字体列表
        self.recommended_fonts = font_manager.get_recommended_fonts()
        
        # 创建字体选择器（包含预览功能）
        self.text_font_var = tk.StringVar()
        self.text_font_size_var = tk.IntVar(value=36)
        self.text_bold_var = tk.BooleanVar()
        self.text_italic_var = tk.BooleanVar()
        
        self.font_selector = FontSelector(
            font_frame,
            font_list=self.recommended_fonts,
            on_font_change=self._on_font_change_enhanced,
            preview_width=250,
            preview_height=50
        )
        self.font_selector.pack(fill='x', padx=10, pady=5)
        
        # 同步字体选择器的变量与主窗口变量
        self._sync_font_selector_vars()

        # 字体颜色
        color_frame = ttk.Frame(font_frame)
        color_frame.pack(fill='x', padx=10, pady=5)
        
        self.text_color_var = tk.StringVar(value="white")
        self.text_color_selector = ColorSelectorWithLabel(
            color_frame,
            label_text="字体颜色:",
            initial_color="white",
            on_color_change=lambda color: (self.text_color_var.set(color), self._schedule_redraw()),
            label_width=8
        )
        self.text_color_selector.pack(fill='x')

        # 字体样式已集成到字体选择器中，无需额外控件

        # 透明度
        alpha_frame = ttk.Frame(font_frame)
        alpha_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(alpha_frame, text="透明度:").pack(side='left')
        self.text_alpha_var = tk.DoubleVar(value=0.8)
        alpha_scale = ttk.Scale(
            alpha_frame,
            from_=0.1, to=1.0,
            variable=self.text_alpha_var,
            orient='horizontal',
            length=150,
            command=lambda v: self._schedule_redraw()
        )
        alpha_scale.pack(side='right')
        self.text_alpha_var.trace_add('write', lambda *args: self._schedule_redraw())

        # 效果设置
        effects_frame = ttk.LabelFrame(text_frame, text="视觉效果")
        effects_frame.pack(fill='x', padx=10, pady=(5, 0))

        # 阴影效果
        self.shadow_enabled_var = tk.BooleanVar()
        shadow_check = ttk.Checkbutton(
            effects_frame,
            text="启用阴影",
            variable=self.shadow_enabled_var,
            command=self._on_shadow_toggle
        )
        shadow_check.pack(anchor='w', padx=10, pady=5)

        self.shadow_frame = ttk.Frame(effects_frame)
        self.shadow_frame.pack(fill='x', padx=20, pady=(0, 5))

        # 阴影颜色
        shadow_color_frame = ttk.Frame(self.shadow_frame)
        shadow_color_frame.pack(fill='x', pady=2)
        
        self.shadow_color_var = tk.StringVar(value="black")
        self.shadow_color_selector = ColorSelectorWithLabel(
            shadow_color_frame,
            label_text="阴影颜色:",
            initial_color="black",
            on_color_change=lambda color: (self.shadow_color_var.set(color), self._schedule_redraw()),
            label_width=8
        )
        self.shadow_color_selector.pack(fill='x')
        
        # 阴影偏移
        offset_frame = ttk.Frame(self.shadow_frame)
        offset_frame.pack(fill='x', pady=2)
        ttk.Label(offset_frame, text="偏移:").pack(side='left')
        self.shadow_offset_x_var = tk.IntVar(value=2)
        self.shadow_offset_y_var = tk.IntVar(value=2)
        ttk.Entry(offset_frame, textvariable=self.shadow_offset_x_var, width=5).pack(side='left', padx=(5, 2))
        ttk.Label(offset_frame, text="x").pack(side='left', padx=(0, 5))
        ttk.Entry(offset_frame, textvariable=self.shadow_offset_y_var, width=5).pack(side='left', padx=(0, 2))
        ttk.Label(offset_frame, text="y").pack(side='left')
        
        # 阴影模糊
        blur_frame = ttk.Frame(self.shadow_frame)
        blur_frame.pack(fill='x', pady=2)
        ttk.Label(blur_frame, text="模糊半径:").pack(side='left')
        self.shadow_blur_var = tk.IntVar(value=2)
        ttk.Entry(blur_frame, textvariable=self.shadow_blur_var, width=5).pack(side='right')
        
        # 阴影透明度
        shadow_alpha_frame = ttk.Frame(self.shadow_frame)
        shadow_alpha_frame.pack(fill='x', pady=2)
        ttk.Label(shadow_alpha_frame, text="阴影透明度:").pack(side='left')
        self.shadow_alpha_var = tk.DoubleVar(value=0.5)
        shadow_alpha_scale = ttk.Scale(
            shadow_alpha_frame,
            from_=0.1, to=1.0,
            variable=self.shadow_alpha_var,
            orient='horizontal',
            length=100,
            command=lambda v: self._schedule_redraw()
        )
        shadow_alpha_scale.pack(side='right')
        
        # 绑定变化事件
        self.shadow_offset_x_var.trace_add('write', lambda *args: self._schedule_redraw())
        self.shadow_offset_y_var.trace_add('write', lambda *args: self._schedule_redraw())
        self.shadow_blur_var.trace_add('write', lambda *args: self._schedule_redraw())

        # 描边效果
        self.stroke_enabled_var = tk.BooleanVar()
        stroke_check = ttk.Checkbutton(
            effects_frame,
            text="启用描边",
            variable=self.stroke_enabled_var,
            command=self._on_stroke_toggle
        )
        stroke_check.pack(anchor='w', padx=10, pady=5)

        self.stroke_frame = ttk.Frame(effects_frame)
        self.stroke_frame.pack(fill='x', padx=20, pady=(0, 10))

        # 描边颜色
        stroke_color_frame = ttk.Frame(self.stroke_frame)
        stroke_color_frame.pack(fill='x', pady=2)
        
        self.stroke_color_var = tk.StringVar(value="black")
        self.stroke_color_selector = ColorSelectorWithLabel(
            stroke_color_frame,
            label_text="描边颜色:",
            initial_color="black",
            on_color_change=lambda color: (self.stroke_color_var.set(color), self._schedule_redraw()),
            label_width=8
        )
        self.stroke_color_selector.pack(fill='x')
        
        # 描边宽度
        stroke_width_frame = ttk.Frame(self.stroke_frame)
        stroke_width_frame.pack(fill='x', pady=2)
        ttk.Label(stroke_width_frame, text="描边宽度:").pack(side='left')
        self.stroke_width_var = tk.IntVar(value=1)
        ttk.Entry(stroke_width_frame, textvariable=self.stroke_width_var, width=5).pack(side='right')
        self.stroke_width_var.trace_add('write', lambda *args: self._schedule_redraw())

        # 初始化效果控件状态
        self._on_shadow_toggle()
        self._on_stroke_toggle()
    
    def _create_image_watermark_tab(self):
        """创建图片水印选项卡"""
        image_frame = ttk.Frame(self.watermark_notebook)
        self.watermark_notebook.add(image_frame, text="图片水印")

        # 图片选择
        ttk.Label(image_frame, text="水印图片:").pack(anchor='w', padx=10, pady=(10, 0))
        file_frame = ttk.Frame(image_frame)
        file_frame.pack(fill='x', padx=10, pady=(0, 5))

        self.image_path_var = tk.StringVar(value="")
        path_entry = ttk.Entry(file_frame, textvariable=self.image_path_var)
        path_entry.pack(side='left', fill='x', expand=True)

        ttk.Button(
            file_frame,
            text="浏览",
            command=self._browse_watermark_image,
            width=8
        ).pack(side='right', padx=(5, 0))
        self.image_path_var.trace_add('write', lambda *args: self._schedule_redraw())
        
        # (rotation mapping handled when building watermark_config)

        # 缩放设置
        scale_frame = ttk.LabelFrame(image_frame, text="尺寸设置")
        scale_frame.pack(fill='x', padx=10, pady=(5, 0))

        # 缩放模式
        self.scale_mode_var = tk.StringVar(value="percentage")

        percentage_frame = ttk.Frame(scale_frame)
        percentage_frame.pack(fill='x', padx=10, pady=5)
        ttk.Radiobutton(
            percentage_frame, text="按比例:",
            variable=self.scale_mode_var, value="percentage",
            command=lambda: self._schedule_redraw()
        ).pack(side='left')
        self.scale_percentage_var = tk.DoubleVar(value=20.0)
        percentage_entry = ttk.Entry(percentage_frame, textvariable=self.scale_percentage_var, width=8)
        percentage_entry.pack(side='left', padx=(5, 2))
        ttk.Label(percentage_frame, text="%").pack(side='left')
        self.scale_percentage_var.trace_add('write', lambda *args: self._schedule_redraw())

        pixel_frame = ttk.Frame(scale_frame)
        pixel_frame.pack(fill='x', padx=10, pady=5)
        ttk.Radiobutton(
            pixel_frame, text="按像素:",
            variable=self.scale_mode_var, value="pixel",
            command=lambda: self._schedule_redraw()
        ).pack(side='left')
        self.scale_width_var = tk.IntVar(value=100)
        self.scale_height_var = tk.IntVar(value=100)
        ttk.Entry(pixel_frame, textvariable=self.scale_width_var, width=6).pack(side='left', padx=(5, 2))
        ttk.Label(pixel_frame, text="x").pack(side='left', padx=(0, 2))
        ttk.Entry(pixel_frame, textvariable=self.scale_height_var, width=6).pack(side='left', padx=(0, 2))
        ttk.Label(pixel_frame, text="px").pack(side='left')

        # 保持宽高比
        self.keep_ratio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            scale_frame, text="保持宽高比",
            variable=self.keep_ratio_var
        ).pack(anchor='w', padx=10, pady=5)
        self.scale_width_var.trace_add('write', lambda *args: self._schedule_redraw())
        self.scale_height_var.trace_add('write', lambda *args: self._schedule_redraw())
        self.keep_ratio_var.trace_add('write', lambda *args: self._schedule_redraw())

        # 透明度设置
        alpha_frame = ttk.LabelFrame(image_frame, text="透明度设置")
        alpha_frame.pack(fill='x', padx=10, pady=(5, 0))
        
        alpha_control_frame = ttk.Frame(alpha_frame)
        alpha_control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(alpha_control_frame, text="透明度:").pack(side='left')
        
        self.image_alpha_var = tk.DoubleVar(value=0.8)
        
        # 透明度滑块
        alpha_slider = ttk.Scale(
            alpha_control_frame,
            from_=0.0,
            to=1.0,
            variable=self.image_alpha_var,
            orient='horizontal',
            length=150,
            command=lambda v: self._on_image_alpha_change()
        )
        alpha_slider.pack(side='left', padx=(5, 10), fill='x', expand=True)
        
        # 透明度数值显示
        self.image_alpha_label = ttk.Label(alpha_control_frame, text="80%")
        self.image_alpha_label.pack(side='right')
        
        # 初始化透明度显示
        self._update_image_alpha_display()

        
    def _create_position_settings(self, parent):
        """创建通用位置设置"""
        position_frame = ttk.LabelFrame(parent, text="位置设置")
        position_frame.pack(fill='x', padx=10, pady=(5, 0))
        
        ttk.Label(position_frame, text="水印位置:").pack(anchor='w', padx=10, pady=(5, 0))
        # internal position (enum value strings)
        self.position_var = tk.StringVar(value="bottom-right")
        # user-facing display (Chinese labels)
        self._position_display_map = {
            'top-left': '左上',
            'top-center': '顶部居中',
            'top-right': '右上',
            'center-left': '左中',
            'center': '居中',
            'center-right': '右中',
            'bottom-left': '左下',
            'bottom-center': '底部居中',
            'bottom-right': '右下'
        }
        # reverse map
        self._position_reverse_map = {v: k for k, v in self._position_display_map.items()}

        self.position_display_var = tk.StringVar(value=self._position_display_map.get(self.position_var.get(), '右下'))
        position_combo = ttk.Combobox(
            position_frame,
            textvariable=self.position_display_var,
            values=list(self._position_display_map.values()),
            state="readonly"
        )
        position_combo.pack(fill='x', padx=10, pady=(0, 10))
        # 位置选择变化时同步内部 position_var 并刷新预览
        def _on_position_display_change(event=None):
            disp = self.position_display_var.get()
            eng = self._position_reverse_map.get(disp)
            if eng:
                self.position_var.set(eng)
            self._schedule_redraw()

        position_combo.bind('<<ComboboxSelected>>', _on_position_display_change)

        # 增加九宫格预设按钮（便捷一键定位）
        presets_frame = ttk.Frame(position_frame)
        presets_frame.pack(fill='x', padx=10, pady=(5, 5))

        from ..core.config import Position as _PositionEnum

        btn_map = [
            (_PositionEnum.TOP_LEFT, '左上'), (_PositionEnum.TOP_CENTER, '顶部居中'), (_PositionEnum.TOP_RIGHT, '右上'),
            (_PositionEnum.CENTER_LEFT, '左中'), (_PositionEnum.CENTER, '居中'), (_PositionEnum.CENTER_RIGHT, '右中'),
            (_PositionEnum.BOTTOM_LEFT, '左下'), (_PositionEnum.BOTTOM_CENTER, '底部居中'), (_PositionEnum.BOTTOM_RIGHT, '右下')
        ]

        for i, (pos_enum, label) in enumerate(btn_map):
            r = i // 3
            c = i % 3
            btn = ttk.Button(presets_frame, text=label, width=8,
                             command=lambda p=pos_enum, l=label: self._set_preset_position(p, l))
            btn.grid(row=r, column=c, padx=3, pady=3)
            self._position_buttons[pos_enum] = btn

        # 旋转控制（放在位置设置面板以便快速定位/预览）
        ttk.Label(position_frame, text="旋转角度 (°):").pack(anchor='w', padx=10, pady=(5, 0))
        self.rotation_var = tk.StringVar(value='0')
        rot_ui_frame = ttk.Frame(position_frame)
        rot_ui_frame.pack(fill='x', padx=10, pady=(0, 5))
        rot_slider = ttk.Scale(rot_ui_frame, from_=-180, to=180, variable=tk.DoubleVar(value=0.0), orient='horizontal', command=lambda v: self._on_rotation_slider(v))
        rot_slider.pack(side='left', fill='x', expand=True)
        rot_entry = ttk.Entry(rot_ui_frame, textvariable=self.rotation_var, width=6)
        rot_entry.pack(side='right', padx=(5, 0))
        # 自动刷新并验证旋转角度输入
        self.rotation_var.trace_add('write', lambda *args: self._schedule_redraw())

    # 坐标输入（像素）
        coord_frame = ttk.Frame(position_frame)
        coord_frame.pack(fill='x', padx=10, pady=(5, 10))
        ttk.Label(coord_frame, text="坐标 (px):").pack(side='left')
        self.coord_x_var = tk.IntVar(value=0)
        self.coord_y_var = tk.IntVar(value=0)
        ttk.Entry(coord_frame, textvariable=self.coord_x_var, width=8).pack(side='left', padx=(5,2))
        ttk.Label(coord_frame, text="x").pack(side='left', padx=(0,3))
        ttk.Entry(coord_frame, textvariable=self.coord_y_var, width=8).pack(side='left', padx=(2,5))
        ttk.Button(coord_frame, text="应用坐标", command=self._apply_manual_coordinates).pack(side='left')

        # 点击预览设置坐标的提示
        ttk.Label(position_frame, text="提示: 点击预览图片可设置自定义坐标。", font=('Arial', 8), foreground='gray').pack(anchor='w', padx=10)

    def _set_preset_position(self, pos_enum, display_label=None):
        """设置预设位置（九宫格按钮回调）
        pos_enum: Position enum
        display_label: 中文显示标签（可选），用于同步 combobox
        """
        try:
            # 更新配置中的位置并清除自定义坐标
            self.position_var.set(pos_enum.value)
            self.custom_position = None
            # 同步显示标签（如果有）
            if display_label and hasattr(self, 'position_display_var'):
                self.position_display_var.set(display_label)
            # 高亮选中按钮（样式）
            for p, btn in self._position_buttons.items():
                try:
                    if p == pos_enum:
                        btn.state(['pressed'])
                    else:
                        btn.state(['!pressed'])
                except Exception:
                    pass
            self._schedule_redraw()
        except Exception:
            pass

    def _apply_manual_coordinates(self):
        """应用手动输入的坐标到自定义位置"""
        try:
            x = int(self.coord_x_var.get())
            y = int(self.coord_y_var.get())
            self.custom_position = (x, y)
            self._schedule_redraw()
        except Exception:
            messagebox.showerror("错误", "请输入有效的整数坐标")

    def _on_preview_click(self, event):
        """用户点击预览画布时，将画布坐标映射为原图像像素坐标并设置为自定义位置"""
        try:
            if not self._preview_img_tk:
                return
        except Exception:
            return

        # 获取当前预view image geometry
        try:
            info = self._last_preview_info
            if not info:
                # no mapping info available
                return
            img_x, img_y, img_w, img_h = info['img_box']  # (left, top, width, height)
            canvas_x = event.x
            canvas_y = event.y
            # 判断是否点击在图片区域
            if not (img_x <= canvas_x <= img_x + img_w and img_y <= canvas_y <= img_y + img_h):
                return
            # 计算在图片内的相对坐标
            rel_x = (canvas_x - img_x) / img_w
            rel_y = (canvas_y - img_y) / img_h
            # 映射回原始图片像素尺寸
            orig_w = info.get('orig_width')
            orig_h = info.get('orig_height')
            px = int(rel_x * orig_w)
            py = int(rel_y * orig_h)
            self.custom_position = (px, py)
            # 更新坐标输入框
            self.coord_x_var.set(px)
            self.coord_y_var.set(py)
            self.position_var.set('custom')
            self._schedule_redraw()
        except Exception:
            pass

    def _on_preview_mouse_down(self, event):
        """鼠标按下：若点击在水印上则开始拖拽，否则作为点击设置坐标"""
        try:
            info = self._last_preview_info
            if not info:
                return

            # 判断是否点击在计算出的水印区域（canvas坐标）
            wm_box = info.get('watermark_box')
            if wm_box:
                wx, wy, ww, wh = wm_box
                if wx <= event.x <= wx + ww and wy <= event.y <= wy + wh:
                    # 在水印上，开始拖拽
                    self._dragging = True
                    self._drag_offset = (event.x - wx, event.y - wy)
                    return

            # 否则作为普通点击设置坐标
            self._on_preview_click(event)
        except Exception:
            pass

    def _on_preview_mouse_move(self, event):
        """鼠标移动（拖拽）: 实时更新自定义位置并刷新预览"""
        try:
            if not self._dragging:
                return
            info = self._last_preview_info
            if not info:
                return

            img_left, img_top, img_w, img_h = info['img_box']
            orig_w = info.get('orig_width')
            orig_h = info.get('orig_height')

            # 计算新的水印左上角（canvas坐标）
            offset_x, offset_y = self._drag_offset
            new_left = event.x - offset_x
            new_top = event.y - offset_y

            # 限制在图片区域内
            new_left = max(img_left, min(new_left, img_left + img_w))
            new_top = max(img_top, min(new_top, img_top + img_h))

            # 转换为相对并映射回原图像像素
            rel_x = (new_left - img_left) / img_w
            rel_y = (new_top - img_top) / img_h
            px = int(rel_x * orig_w)
            py = int(rel_y * orig_h)

            # 更新自定义位置和输入框
            self.custom_position = (px, py)
            self.coord_x_var.set(px)
            self.coord_y_var.set(py)
            self.position_var.set('custom')

            # 实时刷新预览（直接调用以获得更即时反馈）
            self._update_preview_image(self.thumbnail_list.get_selected_files())
        except Exception:
            pass

    def _on_preview_mouse_up(self, event):
        """结束拖拽"""
        try:
            if self._dragging:
                self._dragging = False
                # 最终刷新
                self._schedule_redraw()
        except Exception:
            pass
    
    def _on_shadow_toggle(self):
        """阴影效果开关切换"""
        if hasattr(self, 'shadow_frame'):
            if self.shadow_enabled_var.get():
                for child in self.shadow_frame.winfo_children():
                    self._enable_widget_recursive(child)
            else:
                for child in self.shadow_frame.winfo_children():
                    self._disable_widget_recursive(child)
        # 切换阴影后刷新预览
        self._redraw_preview()
    
    def _on_stroke_toggle(self):
        """描边效果开关切换"""
        if hasattr(self, 'stroke_frame'):
            if self.stroke_enabled_var.get():
                for child in self.stroke_frame.winfo_children():
                    self._enable_widget_recursive(child)
            else:
                for child in self.stroke_frame.winfo_children():
                    self._disable_widget_recursive(child)
        # 切换描边后刷新预览
        self._redraw_preview()
    
    def _on_font_change_enhanced(self, font_info, size, bold, italic):
        """增强字体选择器的变化事件"""
        # 更新相关变量
        if font_info:
            self.text_font_var.set(font_info['name'])
        self.text_font_size_var.set(size)
        self.text_bold_var.set(bold)
        self.text_italic_var.set(italic)
        
        # 刷新预览
        self._redraw_preview()
    
    def _on_image_alpha_change(self):
        """图片透明度变化事件"""
        self._update_image_alpha_display()
        self._schedule_redraw()
    
    def _update_image_alpha_display(self):
        """更新透明度显示"""
        if hasattr(self, 'image_alpha_label'):
            alpha_percent = int(self.image_alpha_var.get() * 100)
            self.image_alpha_label.config(text=f"{alpha_percent}%")
    
    def _sync_font_selector_vars(self):
        """同步字体选择器的变量与主窗口变量"""
        if hasattr(self, 'font_selector'):
            # 将字体选择器的变量与主窗口变量绑定
            def on_bold_change(*args):
                if hasattr(self, 'text_bold_var'):
                    self.text_bold_var.set(self.font_selector.bold_var.get())
                    self._schedule_redraw()
            
            def on_italic_change(*args):
                if hasattr(self, 'text_italic_var'):
                    self.text_italic_var.set(self.font_selector.italic_var.get())
                    self._schedule_redraw()
            
            def on_size_change(*args):
                if hasattr(self, 'text_font_size_var'):
                    self.text_font_size_var.set(self.font_selector.size_var.get())
                    self._schedule_redraw()
            
            # 绑定变化事件
            self.font_selector.bold_var.trace_add('write', on_bold_change)
            self.font_selector.italic_var.trace_add('write', on_italic_change)
            self.font_selector.size_var.trace_add('write', on_size_change)
            
            # 初始同步
            self.text_bold_var.set(self.font_selector.bold_var.get())
            self.text_italic_var.set(self.font_selector.italic_var.get())
            self.text_font_size_var.set(self.font_selector.size_var.get())
    
    def _on_font_change(self, event=None):
        """字体选择变化事件（保持向后兼容）"""
        selected_font_name = self.text_font_var.get()
        selected_font_info = None
        
        # 找到对应的字体信息
        for font_info in self.recommended_fonts:
            if font_info['name'] == selected_font_name:
                selected_font_info = font_info
                break
        
        # 字体变化也刷新预览
        self._redraw_preview()
    
    def _on_font_style_change(self):
        """字体样式变化事件"""
        # 样式变化后刷新预览
        self._redraw_preview()
    
    def _update_font_style_availability(self, font_path: str):
        """更新字体样式可用性显示"""
        try:
            available_styles = font_manager.get_available_styles_for_font(font_path)
            
            # 更新复选框状态
            has_bold = any('bold' in style for style in available_styles)
            has_italic = any('italic' in style for style in available_styles)
            
            # 启用/禁用复选框
            self.bold_checkbox.config(state='normal' if has_bold else 'disabled')
            self.italic_checkbox.config(state='normal' if has_italic else 'disabled')
            
            # 如果样式不可用，取消选中
            if not has_bold:
                self.text_bold_var.set(False)
            if not has_italic:
                self.text_italic_var.set(False)
            
            # 更新提示信息
            style_info = []
            if has_bold:
                style_info.append("粗体")
            if has_italic:
                style_info.append("斜体")
            
            if style_info:
                self.style_info_label.config(text=f"支持: {', '.join(style_info)}")
            else:
                self.style_info_label.config(text="仅支持常规样式")
                
        except Exception as e:
            # 出错时启用所有样式选项
            self.bold_checkbox.config(state='normal')
            self.italic_checkbox.config(state='normal')
            self.style_info_label.config(text="")
    
    def _browse_watermark_image(self):
        """浏览水印图片"""
        from tkinter import filedialog
        file_types = [
            ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=file_types
        )
        
        if filename:
            self.image_path_var.set(filename)

    def _init_preview_area(self):
        """初始化主预览区域内容"""
        # 显示提示文字
        self.preview_canvas.delete('all')
        w = max(200, self.preview_canvas.winfo_reqwidth())
        h = max(120, self.preview_canvas.winfo_reqheight())
        self.preview_canvas.create_text(
            w//2, h//2,
            text="请选择图片进行预览",
            fill="white",
            font=("Arial", 18)
        )
        # 绑定画布尺寸变化，重绘当前预览
        self.preview_canvas.bind('<Configure>', lambda e: self._schedule_redraw())
        # 绑定点击和拖拽事件，允许用户点击或拖拽设置自定义坐标
        self.preview_canvas.bind('<Button-1>', self._on_preview_mouse_down)
        self.preview_canvas.bind('<B1-Motion>', self._on_preview_mouse_move)
        self.preview_canvas.bind('<ButtonRelease-1>', self._on_preview_mouse_up)

    def _schedule_redraw(self, delay: int = 200):
        """防抖调度重绘，delay 单位毫秒。

        连续触发时会取消上一次计划，减少重复合成开销。
        """
        try:
            if hasattr(self, '_redraw_after_id') and self._redraw_after_id:
                self.root.after_cancel(self._redraw_after_id)
        except Exception:
            pass

        # 在主线程延迟调用真正的重绘函数
        self._redraw_after_id = self.root.after(delay, lambda: self._redraw_preview())

    def _update_preview_image(self, selected_files: List[str]):
        """切换并绘制预览图片（叠加当前水印设置）"""
        if not selected_files:
            self._init_preview_area()
            return

        img_path = selected_files[0]
        try:
            from PIL import Image, ImageTk
            from ..core.config import Config, WatermarkType
            from ..core.image_processor import ImageProcessor
            # 加载原图
            img = Image.open(img_path)
            # 获取当前水印配置
            watermark_config = self._get_watermark_config()
            preview_config = Config(watermark_config)
            preview_config.config.preview_mode = True  # 标记为预览模式
            # 如果当前为时间水印，确保预览配置使用时间选项的字体大小和字体路径
            try:
                if preview_config.config.watermark_type == WatermarkType.TIMESTAMP:
                    if hasattr(self, 'timestamp_font_size_var'):
                        preview_config.config.font_size = self.timestamp_font_size_var.get()
                    # 使用当前选中的字体（共用文本水印的字体选择）
                    selected_font_path = None
                    try:
                        selected_font_name = self.text_font_var.get() if hasattr(self, 'text_font_var') else ""
                        if hasattr(self, 'recommended_fonts'):
                            for font_info in self.recommended_fonts:
                                if font_info.get('name') == selected_font_name:
                                    selected_font_path = font_info.get('path')
                                    break
                    except Exception:
                        selected_font_path = None

                    if selected_font_path:
                        preview_config.config.font_path = selected_font_path

                    # 让时间水印使用界面上选择的颜色和透明度
                    try:
                        if hasattr(self, 'color_var'):
                            preview_config.config.font_color = self.color_var.get()
                        if hasattr(self, 'alpha_var'):
                            preview_config.config.font_alpha = float(self.alpha_var.get())
                    except Exception:
                        pass
            except Exception:
                pass

            # 当为文本水印时，让预览使用文本面板的颜色/透明度/字号覆盖
            try:
                if preview_config.config.watermark_type == WatermarkType.TEXT:
                    if hasattr(self, 'text_color_var'):
                        preview_config.config.text_watermark.font_color = self.text_color_var.get()
                    if hasattr(self, 'text_alpha_var'):
                        preview_config.config.text_watermark.font_alpha = float(self.text_alpha_var.get())
                    if hasattr(self, 'text_font_size_var') and self.text_font_size_var.get():
                        preview_config.config.text_watermark.font_size = int(self.text_font_size_var.get())
            except Exception:
                pass
            # 合成水印
            processor = ImageProcessor(preview_config)
            # 依据当前水印类型准备文本（时间水印需从EXIF或回退到当前时间）
            text_for_watermark = None
            wm_type = preview_config.config.watermark_type
            if wm_type == WatermarkType.TIMESTAMP:
                try:
                    text_for_watermark = processor.exif_reader.get_watermark_text(img_path, preview_config.config.date_format)
                except Exception:
                    # 回退到当前日期格式字符串（保险）
                    from datetime import datetime
                    text_for_watermark = processor.exif_reader.format_date(datetime.now(), preview_config.config.date_format)
            elif wm_type == WatermarkType.TEXT:
                text_for_watermark = preview_config.config.text_watermark.text

            # 使用 preview_with_bbox 获取水印包围盒以便在预览中做交互
            try:
                watermarked_img, wm_bbox = processor.watermark_processor.preview_with_bbox(img, text_for_watermark)
            except Exception:
                watermarked_img = processor.watermark_processor.process_watermark(img, text_for_watermark)
                wm_bbox = None

            # 缩放到预览区域
            canvas_w = max(10, self.preview_canvas.winfo_width())
            canvas_h = max(10, self.preview_canvas.winfo_height())
            img_ratio = watermarked_img.width / watermarked_img.height
            canvas_ratio = canvas_w / canvas_h

            if img_ratio > canvas_ratio:
                target_w = canvas_w - 20
                target_h = int(target_w / img_ratio)
            else:
                target_h = canvas_h - 20
                target_w = int(target_h * img_ratio)

            preview_img = watermarked_img.copy()
            preview_img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)

            self._preview_img_tk = ImageTk.PhotoImage(preview_img)
            self.preview_canvas.delete('all')
            # 计算图片在画布上的显示位置，以便映射点击坐标到原图像像素
            img_left = (canvas_w - preview_img.width) // 2
            img_top = (canvas_h - preview_img.height) // 2
            self._last_preview_info = {
                'img_box': (img_left, img_top, preview_img.width, preview_img.height),
                'orig_width': watermarked_img.width,
                'orig_height': watermarked_img.height,
            }
            # 如果有水印包围盒（基于原始图片像素），将其映射到canvas上的显示坐标
            try:
                if wm_bbox:
                    wm_left, wm_top, wm_w, wm_h = wm_bbox
                    # 计算缩放因子（preview_img 相对于 watermarked_img 的缩放）
                    scale_x = preview_img.width / watermarked_img.width
                    scale_y = preview_img.height / watermarked_img.height
                    canvas_wm_left = img_left + int(wm_left * scale_x)
                    canvas_wm_top = img_top + int(wm_top * scale_y)
                    canvas_wm_w = int(wm_w * scale_x)
                    canvas_wm_h = int(wm_h * scale_y)
                    self._last_preview_info['watermark_box'] = (canvas_wm_left, canvas_wm_top, canvas_wm_w, canvas_wm_h)
                else:
                    self._last_preview_info['watermark_box'] = None
            except Exception:
                self._last_preview_info['watermark_box'] = None
            self.preview_canvas.create_image(
                img_left, img_top,
                image=self._preview_img_tk,
                anchor='nw'
            )
        except Exception as e:
            # 验证字体大小与旋转角度输入是否合法，给出友好提示
            bad_font_input = False
            bad_rotation_input = False
            try:
                # 尝试读取并转换时间水印字号/文本水印字号
                if hasattr(self, 'timestamp_font_size_var'):
                    _ = int(self.timestamp_font_size_var.get())
                if hasattr(self, 'text_font_size_var'):
                    _ = int(self.text_font_size_var.get())
            except Exception:
                bad_font_input = True

            try:
                if hasattr(self, 'rotation_var'):
                    # allow empty/str that can be converted
                    _ = float(self.rotation_var.get())
            except Exception:
                bad_rotation_input = True

            self.preview_canvas.delete('all')
            if bad_font_input:
                message = "请正确输入字体大小"
            elif bad_rotation_input:
                message = "请正确输入旋转角度"
            else:
                message = f"图片加载失败\n{e}"

            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width()//2,
                self.preview_canvas.winfo_height()//2,
                text=message,
                fill="red",
                font=("Arial", 14)
            )

    def _redraw_preview(self):
        """画布尺寸变化或其他情况需要重绘当前选中图片时调用"""
        try:
            selected = self.thumbnail_list.get_selected_files()
            if selected:
                self._update_preview_image(selected)
            else:
                # 若未选择，但列表中有文件，则显示第一张作为预览（非选中状态）
                all_files = self.thumbnail_list.get_all_files()
                if all_files:
                    self._update_preview_image([all_files[0]])
                else:
                    self._init_preview_area()
        except Exception:
            pass

    # ---------------------- Template related UI ----------------------
    def _apply_config_to_gui(self, wm_config):
        """Apply a WatermarkConfig object to GUI controls. Best-effort, per-type mapping.

        This restores only the relevant fields for the template's watermark type and
        avoids contaminating other watermark types (e.g. applying an image template
        won't leave text content active).
        """
        from ..core.config import WatermarkType as _WMT

        # 1) Position and custom pixel coordinates
        try:
            if getattr(wm_config, 'position', None) is not None:
                try:
                    self.position_var.set(wm_config.position.value)
                except Exception:
                    pass
            cp = getattr(wm_config, 'custom_position', None)
            if cp:
                try:
                    x = int(cp[0]); y = int(cp[1])
                    self.custom_position = (x, y)
                    if hasattr(self, 'coord_x_var'):
                        self.coord_x_var.set(x)
                    if hasattr(self, 'coord_y_var'):
                        self.coord_y_var.set(y)
                    self.position_var.set('custom')
                except Exception:
                    pass
            else:
                # clear previous custom if template doesn't carry one
                try:
                    self.custom_position = None
                except Exception:
                    pass
        except Exception:
            pass

        # 2) Select the correct tab according to watermark_type
        try:
            wt = getattr(wm_config, 'watermark_type', None)
            if wt == _WMT.TIMESTAMP:
                self.watermark_notebook.select(0)
            elif wt == _WMT.TEXT:
                self.watermark_notebook.select(1)
            elif wt == _WMT.IMAGE:
                self.watermark_notebook.select(2)
        except Exception:
            pass

        # 3) Common fields (color/alpha/font path)
        try:
            if hasattr(wm_config, 'font_color') and wm_config.font_color:
                self.color_var.set(wm_config.font_color)
                if hasattr(self, 'timestamp_color_selector'):
                    self.timestamp_color_selector.set_color(wm_config.font_color)
            if hasattr(wm_config, 'font_alpha') and wm_config.font_alpha is not None:
                self.alpha_var.set(wm_config.font_alpha)
            if hasattr(wm_config, 'font_path') and wm_config.font_path:
                for f in getattr(self, 'recommended_fonts', []):
                    if f.get('path') == wm_config.font_path or f.get('name') == getattr(wm_config, 'font_name', None):
                        self.text_font_var.set(f.get('name'))
                        # 更新字体选择器
                        if hasattr(self, 'font_selector'):
                            self.font_selector.set_font(f.get('name'))
                        break
        except Exception:
            pass

        # 4) Text watermark fields (apply but only activate if template is text/timestamp)
        try:
            tw = getattr(wm_config, 'text_watermark', None)
            if tw:
                if getattr(tw, 'text', None) is not None:
                    try:
                        self.text_content_var.set(tw.text)
                        if hasattr(self, 'text_entry_widget'):
                            try:
                                self.text_entry_widget.delete('1.0', tk.END)
                                self.text_entry_widget.insert('1.0', tw.text)
                            except Exception:
                                pass
                    except Exception:
                        pass
                if getattr(tw, 'font_size', None):
                    try:
                        self.text_font_size_var.set(tw.font_size)
                    except Exception:
                        pass
                if getattr(tw, 'font_color', None):
                    try:
                        self.text_color_var.set(tw.font_color)
                        if hasattr(self, 'text_color_selector'):
                            self.text_color_selector.set_color(tw.font_color)
                    except Exception:
                        pass
                if getattr(tw, 'font_alpha', None) is not None:
                    try:
                        self.text_alpha_var.set(tw.font_alpha)
                    except Exception:
                        pass
                try:
                    self.text_bold_var.set(bool(getattr(tw, 'font_bold', False)))
                    self.text_italic_var.set(bool(getattr(tw, 'font_italic', False)))
                    self.shadow_enabled_var.set(bool(getattr(tw, 'shadow_enabled', False)))
                    self.stroke_enabled_var.set(bool(getattr(tw, 'stroke_enabled', False)))
                    self.rotation_var.set(str(float(getattr(tw, 'rotation', 0.0))))
                    
                    # 更新字体选择器的所有设置
                    if hasattr(self, 'font_selector'):
                        font_name = None
                        if getattr(tw, 'font_path', None):
                            for f in getattr(self, 'recommended_fonts', []):
                                if f.get('path') == tw.font_path:
                                    font_name = f.get('name')
                                    break
                        elif getattr(tw, 'font_name', None):
                            font_name = tw.font_name
                        
                        if font_name:
                            self.font_selector.set_font(
                                font_name,
                                getattr(tw, 'font_size', 36),
                                bool(getattr(tw, 'font_bold', False)),
                                bool(getattr(tw, 'font_italic', False))
                            )
                        
                        # 确保主窗口变量也同步更新
                        self.text_bold_var.set(bool(getattr(tw, 'font_bold', False)))
                        self.text_italic_var.set(bool(getattr(tw, 'font_italic', False)))
                        self.text_font_size_var.set(getattr(tw, 'font_size', 36))
                    
                    # 阴影设置
                    if hasattr(self, 'shadow_color_var') and getattr(tw, 'shadow_color', None):
                        self.shadow_color_var.set(tw.shadow_color)
                        if hasattr(self, 'shadow_color_selector'):
                            self.shadow_color_selector.set_color(tw.shadow_color)
                    if hasattr(self, 'shadow_offset_x_var') and getattr(tw, 'shadow_offset_x', None) is not None:
                        self.shadow_offset_x_var.set(tw.shadow_offset_x)
                    if hasattr(self, 'shadow_offset_y_var') and getattr(tw, 'shadow_offset_y', None) is not None:
                        self.shadow_offset_y_var.set(tw.shadow_offset_y)
                    if hasattr(self, 'shadow_blur_var') and getattr(tw, 'shadow_blur', None) is not None:
                        self.shadow_blur_var.set(tw.shadow_blur)
                    if hasattr(self, 'shadow_alpha_var') and getattr(tw, 'shadow_alpha', None) is not None:
                        self.shadow_alpha_var.set(tw.shadow_alpha)
                    
                    # 描边设置
                    if hasattr(self, 'stroke_color_var') and getattr(tw, 'stroke_color', None):
                        self.stroke_color_var.set(tw.stroke_color)
                        if hasattr(self, 'stroke_color_selector'):
                            self.stroke_color_selector.set_color(tw.stroke_color)
                    if hasattr(self, 'stroke_width_var') and getattr(tw, 'stroke_width', None) is not None:
                        self.stroke_width_var.set(tw.stroke_width)
                except Exception:
                    pass
        except Exception:
            pass

        # 5) Image watermark fields
        try:
            iw = getattr(wm_config, 'image_watermark', None)
            if iw:
                try:
                    if getattr(iw, 'image_path', None):
                        self.image_path_var.set(iw.image_path)
                except Exception:
                    pass
                try:
                    if getattr(iw, 'scale_mode', None):
                        self.scale_mode_var.set('percentage' if getattr(iw, 'scale_mode').name.lower() == 'percentage' else 'pixel')
                    if getattr(iw, 'scale_percentage', None):
                        self.scale_percentage_var.set(iw.scale_percentage)
                    if getattr(iw, 'scale_width', None):
                        self.scale_width_var.set(iw.scale_width)
                    if getattr(iw, 'scale_height', None):
                        self.scale_height_var.set(iw.scale_height)
                    if getattr(iw, 'alpha', None) is not None:
                        try:
                            self.image_alpha_var.set(iw.alpha)
                            self._update_image_alpha_display()
                        except Exception:
                            pass
                    self.rotation_var.set(str(float(getattr(iw, 'rotation', 0.0))))
                except Exception:
                    pass
        except Exception:
            pass

        # 6) Ensure no cross-contamination: depending on watermark_type, clear the other type's main input
        try:
            wt = getattr(wm_config, 'watermark_type', None)
            if wt == _WMT.TEXT:
                # ensure image is deselected so preview uses text
                try:
                    self.image_path_var.set("")
                except Exception:
                    pass
            elif wt == _WMT.IMAGE:
                # ensure text is cleared so preview uses image
                try:
                    self.text_content_var.set("")
                    if hasattr(self, 'text_entry_widget'):
                        try:
                            self.text_entry_widget.delete('1.0', tk.END)
                        except Exception:
                            pass
                except Exception:
                    pass
            elif wt == _WMT.TIMESTAMP:
                # clear both text and image so timestamp is used
                try:
                    self.text_content_var.set("")
                    if hasattr(self, 'text_entry_widget'):
                        try:
                            self.text_entry_widget.delete('1.0', tk.END)
                        except Exception:
                            pass
                    self.image_path_var.set("")
                except Exception:
                    pass
        except Exception:
            pass

        # 7) Timestamp font size (if present)
        try:
            if getattr(wm_config, 'font_size', None):
                try:
                    self.timestamp_font_size_var.set(wm_config.font_size)
                except Exception:
                    pass
        except Exception:
            pass

        # final redraw to reflect applied template
        try:
            self._schedule_redraw()
        except Exception:
            pass

    def _on_app_close(self):
        """Save last session and then quit."""
        try:
            wm = self._get_watermark_config()
            if getattr(self, 'template_manager', None):
                try:
                    self.template_manager.save_last_session(wm)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            try:
                self.root.quit()
            except Exception:
                pass

    def _save_template_dialog(self):
        """Show a simple dialog to name and save the current settings as a template."""
        if not getattr(self, 'template_manager', None):
            messagebox.showerror("错误", "模板管理器不可用")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("保存为模板")
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text="模板名称:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        name_var = tk.StringVar()
        ttk.Entry(dlg, textvariable=name_var, width=40).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(dlg, text="描述 (可选):").grid(row=1, column=0, padx=10, pady=0, sticky='nw')
        desc_text = tk.Text(dlg, height=4, width=40)
        desc_text.grid(row=1, column=1, padx=10, pady=5)

        def _on_save():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入模板名称")
                return
            desc = desc_text.get('1.0', tk.END).strip()
            try:
                cfg = self._get_watermark_config()
                self.template_manager.save_template(name, cfg, desc)
                # 刷新嵌入式模板列表并选中新保存的模板
                try:
                    self._template_refresh_list()
                    # 选中新保存项
                    items = self.template_manager.list_templates()
                    for idx, it in enumerate(items):
                        if it.get('name') == name:
                            try:
                                self.template_listbox.select_clear(0, tk.END)
                                self.template_listbox.select_set(idx)
                                self.template_listbox.see(idx)
                            except Exception:
                                pass
                            break
                except Exception:
                    pass

                messagebox.showinfo("成功", f"模板 '{name}' 已保存")
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"保存模板失败: {e}")

        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="保存", command=_on_save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="取消", command=dlg.destroy).pack(side='left', padx=5)

    def _open_template_manager(self):
        """Open a simple template manager window to list/apply/delete templates."""
        if not getattr(self, 'template_manager', None):
            messagebox.showerror("错误", "模板管理器不可用")
            return

        mgr = tk.Toplevel(self.root)
        mgr.title("模板管理器")
        mgr.geometry('600x400')
        mgr.transient(self.root)

        listbox = tk.Listbox(mgr)
        listbox.pack(side='left', fill='both', expand=True, padx=(10,0), pady=10)

        scrollbar = ttk.Scrollbar(mgr, orient='vertical', command=listbox.yview)
        scrollbar.pack(side='left', fill='y', pady=10)
        listbox.config(yscrollcommand=scrollbar.set)

        meta_frame = ttk.Frame(mgr)
        meta_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        info_label = ttk.Label(meta_frame, text='选择模板以查看信息')
        info_label.pack(anchor='nw')

        def _refresh_list():
            listbox.delete(0, tk.END)
            for item in self.template_manager.list_templates():
                label = f"{item['name']}    ({item.get('modified_at') or ''})"
                listbox.insert(tk.END, label)

        def _on_select(evt=None):
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            items = self.template_manager.list_templates()
            if idx >= len(items):
                return
            item = items[idx]
            info_text = f"名称: {item['name']}\n修改时间: {item.get('modified_at')}\n描述: {item.get('description','')}\n路径: {item.get('path')}"
            info_label.config(text=info_text)
            # also update embedded panel info if present
            try:
                if hasattr(self, '_template_info_label'):
                    self._template_info_label.config(text=f"{item.get('description','')}\n{item.get('modified_at','')}")
            except Exception:
                pass

        def _apply_selected():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            items = self.template_manager.list_templates()
            item = items[idx]
            try:
                cfg = self.template_manager.load_template(item['name'])
                self._apply_config_to_gui(cfg)
                messagebox.showinfo('提示', f"模板 '{item['name']}' 已应用")
            except Exception as e:
                messagebox.showerror('错误', f"加载模板失败: {e}")

        def _delete_selected():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            items = self.template_manager.list_templates()
            item = items[idx]
            if messagebox.askyesno('确认', f"确定删除模板 '{item['name']}' ?"):
                try:
                    self.template_manager.delete_template(item['name'])
                    _refresh_list()
                except Exception as e:
                    messagebox.showerror('错误', f"删除失败: {e}")

        btn_apply = ttk.Button(meta_frame, text='应用', command=_apply_selected)
        btn_apply.pack(fill='x', pady=(10, 2))
        btn_delete = ttk.Button(meta_frame, text='删除', command=_delete_selected)
        btn_delete.pack(fill='x', pady=2)
        btn_close = ttk.Button(meta_frame, text='关闭', command=mgr.destroy)
        btn_close.pack(side='bottom', pady=5)

        listbox.bind('<<ListboxSelect>>', _on_select)
        _refresh_list()

    # Embedded template UI helpers (used by 左侧设置面板中的模版设置)
    def _template_refresh_list(self):
        if not getattr(self, 'template_manager', None):
            return
        try:
            self.template_listbox.delete(0, tk.END)
            for item in self.template_manager.list_templates():
                # Show only date portion for modified time to avoid long ISO timestamps
                mod = item.get('modified_at') or ''
                mod_display = ''
                if mod:
                    try:
                        mod_display = mod.split('T')[0]
                    except Exception:
                        mod_display = mod
                label = f"{item['name']}" + (f"    ({mod_display})" if mod_display else '')
                self.template_listbox.insert(tk.END, label)
        except Exception:
            pass

    def _template_apply_selected(self):
        if not getattr(self, 'template_manager', None):
            messagebox.showerror('错误', '模板管理器不可用')
            return
        sel = self.template_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        items = self.template_manager.list_templates()
        if idx >= len(items):
            return
        item = items[idx]
        try:
            cfg = self.template_manager.load_template(item['name'])
            self._apply_config_to_gui(cfg)
            messagebox.showinfo('提示', f"模板 '{item['name']}' 已应用")
        except Exception as e:
            messagebox.showerror('错误', f"加载模板失败: {e}")

    def _template_delete_selected(self):
        if not getattr(self, 'template_manager', None):
            return
        sel = self.template_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        items = self.template_manager.list_templates()
        if idx >= len(items):
            return
        item = items[idx]
        if messagebox.askyesno('确认', f"确定删除模板 '{item['name']}' ?"):
            try:
                self.template_manager.delete_template(item['name'])
                self._template_refresh_list()
            except Exception as e:
                messagebox.showerror('错误', f"删除失败: {e}")

    def _template_rename_selected(self):
        if not getattr(self, 'template_manager', None):
            return
        sel = self.template_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        items = self.template_manager.list_templates()
        if idx >= len(items):
            return
        item = items[idx]
        new_name = simpledialog.askstring('重命名', '输入新模板名:', initialvalue=item['name'], parent=self.root)
        if not new_name:
            return
        try:
            self.template_manager.rename_template(item['name'], new_name)
            self._template_refresh_list()
        except Exception as e:
            messagebox.showerror('错误', f"重命名失败: {e}")

    def _template_set_default_selected(self):
        """将选中的模板设为默认模板"""
        if not getattr(self, 'template_manager', None):
            messagebox.showerror('错误', '模板管理器不可用')
            return
        sel = self.template_listbox.curselection()
        if not sel:
            messagebox.showinfo('提示', '请先选择一个模板')
            return
        idx = sel[0]
        items = self.template_manager.list_templates()
        if idx >= len(items):
            return
        item = items[idx]
        try:
            self.template_manager.set_default_template(item['name'])
            messagebox.showinfo('提示', f"模板 '{item['name']}' 已设为默认")
            # refresh list to reflect any visual marker for default
            try:
                self._template_refresh_list()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('错误', f"设为默认失败: {e}")

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
