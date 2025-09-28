"""
缩略图列表组件

显示图片缩略图和文件信息。
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from typing import List, Dict, Optional, Callable


class ThumbnailItem:
    """缩略图项目"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.selected = False
        self.thumbnail = None
        self.image_size = None
        
    def load_thumbnail(self, size: tuple = (150, 150)) -> Optional[ImageTk.PhotoImage]:
        """加载缩略图"""
        try:
            with Image.open(self.file_path) as img:
                # 保存原始尺寸
                self.image_size = img.size
                
                # 创建缩略图
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 转换为tkinter可用的格式
                self.thumbnail = ImageTk.PhotoImage(img)
                return self.thumbnail
        except Exception as e:
            print(f"加载缩略图失败 {self.file_path}: {e}")
            return None
            
    def get_file_info(self) -> str:
        """获取文件信息字符串"""
        size_mb = self.file_size / (1024 * 1024)
        size_str = f"{size_mb:.1f}MB" if size_mb >= 1 else f"{self.file_size // 1024}KB"
        
        if self.image_size:
            return f"{self.filename}\\n{self.image_size[0]}x{self.image_size[1]} | {size_str}"
        else:
            return f"{self.filename}\\n{size_str}"


class ThumbnailList(ttk.Frame):
    """缩略图列表组件"""
    
    def __init__(self, parent, on_selection_change: Optional[Callable[[List[str]], None]] = None,
                 on_list_change: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.on_selection_change = on_selection_change
        self.on_list_change = on_list_change  # 新增：列表变化回调
        self.items: List[ThumbnailItem] = []
        self.selected_items: List[ThumbnailItem] = []
        
        # 创建界面
        self._create_widgets()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 创建工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # 视图切换按钮
        self.view_var = tk.StringVar(value="thumbnail")
        ttk.Radiobutton(
            toolbar, text="缩略图", variable=self.view_var, 
            value="thumbnail", command=self._switch_view
        ).pack(side='left', padx=5)
        ttk.Radiobutton(
            toolbar, text="列表", variable=self.view_var, 
            value="list", command=self._switch_view
        ).pack(side='left', padx=5)
        
        # 操作按钮
        ttk.Button(
            toolbar, text="全选", command=self._select_all
        ).pack(side='right', padx=5)
        ttk.Button(
            toolbar, text="清空", command=self._clear_all
        ).pack(side='right', padx=5)
        
        # 创建滚动区域
        self.canvas = tk.Canvas(self, bg='white')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def _switch_view(self):
        """切换视图模式"""
        self._refresh_display()
        
    def _select_all(self):
        """全选所有项目"""
        for item in self.items:
            item.selected = True
        self.selected_items = self.items.copy()
        self._refresh_display()
        self._notify_selection_change()
        
    def _clear_all(self):
        """清空所有项目"""
        self.items.clear()
        self.selected_items.clear()
        self._refresh_display()
        self._notify_selection_change()
        self._notify_list_change()  # 通知列表变化
        
    def add_files(self, file_paths: List[str]):
        """添加文件到列表"""
        added_count = 0
        for file_path in file_paths:
            if self._is_image_file(file_path) and not self._file_exists(file_path):
                item = ThumbnailItem(file_path)
                item.load_thumbnail()
                self.items.append(item)
                added_count += 1
        
        if added_count > 0:
            self._refresh_display()
            self._notify_list_change()  # 通知列表变化
        
    def _is_image_file(self, file_path: str) -> bool:
        """检查是否为支持的图片文件"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        
    def _file_exists(self, file_path: str) -> bool:
        """检查文件是否已存在于列表中"""
        return any(item.file_path == file_path for item in self.items)
        
    def _refresh_display(self):
        """刷新显示"""
        # 清空当前显示
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if self.view_var.get() == "thumbnail":
            self._display_thumbnail_view()
        else:
            self._display_list_view()
            
    def _display_thumbnail_view(self):
        """显示缩略图视图"""
        cols = 4  # 每行显示4个缩略图
        
        for i, item in enumerate(self.items):
            row = i // cols
            col = i % cols
            
            # 创建缩略图框架
            frame = tk.Frame(
                self.scrollable_frame,
                relief='raised' if item.selected else 'flat',
                bd=2,
                bg='lightblue' if item.selected else 'white'
            )
            frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # 添加缩略图
            if item.thumbnail:
                label_img = tk.Label(frame, image=item.thumbnail, bg='white')
                label_img.pack(pady=5)
                
            # 添加文件信息
            label_info = tk.Label(
                frame, 
                text=item.get_file_info(),
                bg='white',
                font=('Arial', 8),
                justify='center'
            )
            label_info.pack(pady=2)
            
            # 绑定点击事件
            frame.bind("<Button-1>", lambda e, it=item: self._toggle_selection(it))
            label_img.bind("<Button-1>", lambda e, it=item: self._toggle_selection(it))
            label_info.bind("<Button-1>", lambda e, it=item: self._toggle_selection(it))
            
    def _display_list_view(self):
        """显示列表视图"""
        # 创建表头
        headers = ["文件名", "尺寸", "大小", "路径"]
        for i, header in enumerate(headers):
            label = tk.Label(
                self.scrollable_frame,
                text=header,
                font=('Arial', 10, 'bold'),
                bg='lightgray',
                relief='raised',
                bd=1
            )
            label.grid(row=0, column=i, sticky='ew', padx=1, pady=1)
            
        # 显示文件列表
        for i, item in enumerate(self.items, 1):
            bg_color = 'lightblue' if item.selected else 'white'
            
            # 文件名
            tk.Label(
                self.scrollable_frame,
                text=item.filename,
                bg=bg_color,
                anchor='w'
            ).grid(row=i, column=0, sticky='ew', padx=1, pady=1)
            
            # 尺寸
            size_text = f"{item.image_size[0]}x{item.image_size[1]}" if item.image_size else "N/A"
            tk.Label(
                self.scrollable_frame,
                text=size_text,
                bg=bg_color,
                anchor='center'
            ).grid(row=i, column=1, sticky='ew', padx=1, pady=1)
            
            # 大小
            size_mb = item.file_size / (1024 * 1024)
            size_str = f"{size_mb:.1f}MB" if size_mb >= 1 else f"{item.file_size // 1024}KB"
            tk.Label(
                self.scrollable_frame,
                text=size_str,
                bg=bg_color,
                anchor='center'
            ).grid(row=i, column=2, sticky='ew', padx=1, pady=1)
            
            # 路径
            tk.Label(
                self.scrollable_frame,
                text=item.file_path,
                bg=bg_color,
                anchor='w'
            ).grid(row=i, column=3, sticky='ew', padx=1, pady=1)
            
            # 绑定行点击事件
            for col in range(4):
                widget = self.scrollable_frame.grid_slaves(row=i, column=col)[0]
                widget.bind("<Button-1>", lambda e, it=item: self._toggle_selection(it))
                
    def _toggle_selection(self, item: ThumbnailItem):
        """切换项目选择状态"""
        item.selected = not item.selected
        
        if item.selected and item not in self.selected_items:
            self.selected_items.append(item)
        elif not item.selected and item in self.selected_items:
            self.selected_items.remove(item)
            
        self._refresh_display()
        self._notify_selection_change()
        
    def _notify_selection_change(self):
        """通知选择变化"""
        if self.on_selection_change:
            selected_paths = [item.file_path for item in self.selected_items]
            self.on_selection_change(selected_paths)
            
    def _notify_list_change(self):
        """通知列表变化"""
        if self.on_list_change:
            self.on_list_change()
            
    def get_selected_files(self) -> List[str]:
        """获取选中的文件路径"""
        return [item.file_path for item in self.selected_items]
        
    def get_all_files(self) -> List[str]:
        """获取所有文件路径"""
        return [item.file_path for item in self.items]
