"""
字体预览组件

提供字体预览功能，显示字体的实际效果。
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from ...utils.font_manager import font_manager, StyledFontWrapper


class FontPreview(ttk.Frame):
    """字体预览组件"""
    
    def __init__(self, parent, width: int = 200, height: int = 60):
        super().__init__(parent)
        
        self.width = width
        self.height = height
        self.current_font_path = None
        self.current_font_size = 24
        self.current_bold = False
        self.current_italic = False
        self.preview_text = "字体预览 AaBbCc"
        
        self._create_widgets()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 预览画布
        self.canvas = tk.Canvas(
            self, 
            width=self.width, 
            height=self.height,
            bg='white',
            relief='sunken',
            borderwidth=1
        )
        self.canvas.pack(fill='both', expand=True)
        
        # 初始化显示
        self._update_preview()
        
    def _update_preview(self):
        """更新字体预览"""
        self.canvas.delete('all')
        
        try:
            # 使用字体管理器获取字体，支持样式和中文检测
            font = font_manager.get_font(
                self.current_font_path, 
                self.current_font_size, 
                self.current_bold, 
                self.current_italic,
                self.preview_text
            )
            
            # 创建预览图像
            img = Image.new('RGB', (self.width, self.height), 'white')
            draw = ImageDraw.Draw(img)
            
            # 计算文本位置（居中）
            try:
                bbox = draw.textbbox((0, 0), self.preview_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                # 如果textbbox不可用，使用textsize（旧版PIL）
                try:
                    text_width, text_height = draw.textsize(self.preview_text, font=font)
                except:
                    text_width, text_height = 100, 20
            
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            
            # 绘制文本（支持样式字体）
            if isinstance(font, StyledFontWrapper):
                self._draw_styled_text(draw, (x, y), self.preview_text, font, 'black')
            else:
                draw.text((x, y), self.preview_text, font=font, fill='black')
            
            # 转换为Tkinter图像并显示
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(
                self.width // 2, self.height // 2, 
                image=self.photo
            )
            
        except Exception as e:
            # 如果出错，显示错误信息
            self._draw_fallback_text(f"预览失败: {str(e)[:20]}...")
    
    def _draw_fallback_text(self, text: Optional[str] = None):
        """绘制备用文本（当字体加载失败时）"""
        display_text = text or self.preview_text
        
        # 使用Tkinter内置字体
        font_style = []
        if self.current_bold:
            font_style.append('bold')
        if self.current_italic:
            font_style.append('italic')
        
        font_tuple = ('Arial', min(self.current_font_size // 2, 12), ' '.join(font_style))
        
        self.canvas.create_text(
            self.width // 2, self.height // 2,
            text=display_text,
            font=font_tuple,
            fill='black'
        )
    
    def _draw_styled_text(self, draw: ImageDraw.Draw, position: tuple, text: str, 
                         styled_font: StyledFontWrapper, fill):
        """绘制样式文本（用于预览）"""
        x, y = position
        base_font = styled_font.base_font
        
        if styled_font.bold and styled_font.italic:
            # 粗体斜体
            for dx in range(2):
                for dy in range(2):
                    if dx == 0 and dy == 0:
                        continue
                    skew_x = x + dx - dy // 2
                    draw.text((skew_x, y + dy), text, font=base_font, fill=fill)
            draw.text((x, y), text, font=base_font, fill=fill)
            
        elif styled_font.bold:
            # 粗体
            for dx in range(2):
                for dy in range(2):
                    draw.text((x + dx, y + dy), text, font=base_font, fill=fill)
                    
        elif styled_font.italic:
            # 斜体
            try:
                bbox = base_font.getbbox(text)
                text_height = bbox[3] - bbox[1]
                skew_offset = text_height // 8
                draw.text((x + skew_offset, y), text, font=base_font, fill=fill)
            except:
                draw.text((x + 2, y), text, font=base_font, fill=fill)
        else:
            draw.text((x, y), text, font=base_font, fill=fill)
    
    def set_font(self, font_path: Optional[str], font_size: int = 24, 
                 bold: bool = False, italic: bool = False):
        """设置字体"""
        self.current_font_path = font_path
        self.current_font_size = font_size
        self.current_bold = bold
        self.current_italic = italic
        self._update_preview()
    
    def set_preview_text(self, text: str):
        """设置预览文本"""
        self.preview_text = text
        self._update_preview()


class FontSelector(ttk.Frame):
    """字体选择器（包含预览）"""
    
    def __init__(self, parent, font_list: list, 
                 on_font_change: Optional[Callable] = None,
                 preview_width: int = 200, preview_height: int = 60):
        super().__init__(parent)
        
        self.font_list = font_list
        self.on_font_change = on_font_change
        self.current_font_info = None
        
        self._create_widgets(preview_width, preview_height)
        
    def _create_widgets(self, preview_width: int, preview_height: int):
        """创建界面组件"""
        # 字体选择下拉框
        select_frame = ttk.Frame(self)
        select_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(select_frame, text="字体:").pack(side='left')
        
        font_names = [font['name'] for font in self.font_list]
        self.font_var = tk.StringVar()
        
        self.font_combo = ttk.Combobox(
            select_frame,
            textvariable=self.font_var,
            values=font_names,
            state="readonly"
        )
        self.font_combo.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.font_combo.bind('<<ComboboxSelected>>', self._on_font_selected)
        
        # 字体样式选项
        style_frame = ttk.Frame(self)
        style_frame.pack(fill='x', pady=(0, 5))
        
        self.bold_var = tk.BooleanVar()
        self.italic_var = tk.BooleanVar()
        
        self.bold_check = ttk.Checkbutton(
            style_frame, text="粗体", 
            variable=self.bold_var,
            command=self._on_style_change
        )
        self.bold_check.pack(side='left')
        
        self.italic_check = ttk.Checkbutton(
            style_frame, text="斜体", 
            variable=self.italic_var,
            command=self._on_style_change
        )
        self.italic_check.pack(side='left', padx=(10, 0))
        
        # 字体大小
        size_frame = ttk.Frame(self)
        size_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(size_frame, text="大小:").pack(side='left')
        self.size_var = tk.IntVar(value=24)
        size_entry = ttk.Entry(size_frame, textvariable=self.size_var, width=6)
        size_entry.pack(side='left', padx=(5, 0))
        self.size_var.trace_add('write', self._on_size_change)
        
        # 字体预览
        preview_frame = ttk.LabelFrame(self, text="预览")
        preview_frame.pack(fill='x', pady=(5, 0))
        
        self.font_preview = FontPreview(preview_frame, preview_width, preview_height)
        self.font_preview.pack(padx=5, pady=5)
        
        # 设置默认字体
        if font_names:
            # 优先选择支持中文的字体
            chinese_fonts = [f for f in self.font_list if f.get('supports_chinese', False)]
            if chinese_fonts:
                self.font_var.set(chinese_fonts[0]['name'])
                self.current_font_info = chinese_fonts[0]
            else:
                self.font_var.set(font_names[0])
                self.current_font_info = self.font_list[0]
            
            self._update_preview()
    
    def _on_font_selected(self, event=None):
        """字体选择变化"""
        selected_name = self.font_var.get()
        
        # 找到对应的字体信息
        for font_info in self.font_list:
            if font_info['name'] == selected_name:
                self.current_font_info = font_info
                break
        
        self._update_style_availability()
        self._update_preview()
        self._notify_change()
    
    def _on_style_change(self):
        """字体样式变化"""
        self._update_preview()
        self._notify_change()
    
    def _on_size_change(self, *args):
        """字体大小变化"""
        try:
            size = self.size_var.get()
            if 8 <= size <= 200:  # 限制字体大小范围
                self._update_preview()
                self._notify_change()
        except:
            pass
    
    def _update_style_availability(self):
        """更新字体样式可用性"""
        if not self.current_font_info:
            return
        
        # 这里可以根据字体信息判断是否支持粗体和斜体
        # 目前简化处理，假设所有字体都支持
        self.bold_check.config(state='normal')
        self.italic_check.config(state='normal')
    
    def _update_preview(self):
        """更新预览"""
        if self.current_font_info:
            font_path = self.current_font_info.get('path')
            font_size = self.size_var.get()
            bold = self.bold_var.get()
            italic = self.italic_var.get()
            
            self.font_preview.set_font(font_path, font_size, bold, italic)
    
    def _notify_change(self):
        """通知字体变化"""
        if self.on_font_change and self.current_font_info:
            self.on_font_change(
                self.current_font_info,
                self.size_var.get(),
                self.bold_var.get(),
                self.italic_var.get()
            )
    
    def get_current_font(self):
        """获取当前字体信息"""
        return {
            'font_info': self.current_font_info,
            'size': self.size_var.get(),
            'bold': self.bold_var.get(),
            'italic': self.italic_var.get()
        }
    
    def set_font(self, font_name: str, size: int = 24, bold: bool = False, italic: bool = False):
        """设置字体"""
        # 设置字体名称
        if font_name in [f['name'] for f in self.font_list]:
            self.font_var.set(font_name)
            self._on_font_selected()
        
        # 设置大小和样式
        self.size_var.set(size)
        self.bold_var.set(bold)
        self.italic_var.set(italic)
        
        self._update_preview()
