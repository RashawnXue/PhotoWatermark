"""
水印处理模块

负责在图片上绘制文本水印。
"""

import os
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageColor import getcolor

from .config import Config, WatermarkConfig


class WatermarkProcessor:
    """水印处理器"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def _get_font(self, font_size: int) -> ImageFont.ImageFont:
        """获取字体对象"""
        if self.config.config.font_path and os.path.exists(self.config.config.font_path):
            try:
                return ImageFont.truetype(self.config.config.font_path, font_size)
            except Exception:
                pass
        
        # 尝试使用系统默认字体
        try:
            # 在不同操作系统上尝试不同的默认字体
            system_fonts = [
                # macOS
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                # Windows
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                # Linux
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]
            
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, font_size)
            
            # 如果都找不到，使用PIL的默认字体
            return ImageFont.load_default()
            
        except Exception:
            return ImageFont.load_default()
    
    def _parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """解析颜色字符串"""
        try:
            # 尝试解析颜色名称或十六进制值
            rgb = getcolor(color_str, "RGB")
            return rgb
        except ValueError:
            # 如果解析失败，返回白色
            return (255, 255, 255)
    
    def _get_text_size(self, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
        """获取文本尺寸"""
        # 创建临时图像来测量文本大小
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        
        # 使用textbbox获取文本边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        return width, height
    
    def add_watermark(self, image: Image.Image, text: str) -> Image.Image:
        """在图片上添加文本水印"""
        # 创建副本以避免修改原图
        watermarked_image = image.copy()
        
        # 获取图片尺寸
        img_width, img_height = watermarked_image.size
        
        # 计算字体大小
        font_size = self.config.get_auto_font_size(img_width, img_height)
        font = self._get_font(font_size)
        
        # 获取文本尺寸
        text_width, text_height = self._get_text_size(text, font)
        
        # 计算水印位置
        x, y = self.config.get_position_coordinates(
            img_width, img_height, text_width, text_height
        )
        
        # 解析颜色
        color = self._parse_color(self.config.config.font_color)
        
        # 如果需要透明度效果，创建透明层
        if self.config.config.font_alpha < 1.0:
            # 创建透明层
            overlay = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # 计算alpha值 (0-255)
            alpha = int(self.config.config.font_alpha * 255)
            color_with_alpha = (*color, alpha)
            
            # 在透明层上绘制文本
            draw.text((x, y), text, font=font, fill=color_with_alpha)
            
            # 将透明层合并到原图
            if watermarked_image.mode != 'RGBA':
                watermarked_image = watermarked_image.convert('RGBA')
            
            watermarked_image = Image.alpha_composite(watermarked_image, overlay)
            
            # 如果输出格式不支持透明度，转换回RGB
            if self.config.config.output_format.upper() == 'JPEG':
                # 创建白色背景
                background = Image.new('RGB', watermarked_image.size, (255, 255, 255))
                background.paste(watermarked_image, mask=watermarked_image.split()[-1])
                watermarked_image = background
        else:
            # 直接绘制不透明文本
            draw = ImageDraw.Draw(watermarked_image)
            draw.text((x, y), text, font=font, fill=color)
        
        return watermarked_image
    
    def process_image(self, input_path: str, output_path: str, watermark_text: str) -> bool:
        """处理单张图片"""
        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 添加水印
                watermarked_img = self.add_watermark(img, watermark_text)
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 保存图片
                save_kwargs = {}
                if self.config.config.output_format.upper() == 'JPEG':
                    save_kwargs['quality'] = self.config.config.output_quality
                    save_kwargs['optimize'] = True
                elif self.config.config.output_format.upper() == 'PNG':
                    save_kwargs['optimize'] = True
                
                watermarked_img.save(output_path, 
                                   format=self.config.config.output_format, 
                                   **save_kwargs)
                
                return True
                
        except Exception as e:
            if self.config.config.verbose:
                print(f"处理图片 {input_path} 时出错: {e}")
            return False
    
    def process_image_with_options(self, input_path: str, output_path: str, 
                                 watermark_text: str, output_format: str = None, 
                                 quality: int = 95, resize_config: dict = None) -> bool:
        """处理单张图片（带完整选项）"""
        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 调整图片尺寸
                if resize_config and resize_config.get('enabled', False):
                    img = self._resize_image(img, resize_config)
                
                # 添加水印
                watermarked_img = self.add_watermark(img, watermark_text)
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 确定输出格式
                if output_format is None:
                    output_format = self.config.config.output_format
                
                # 处理格式转换
                if output_format.upper() == 'JPEG':
                    # JPEG不支持透明通道，需要转换
                    if watermarked_img.mode in ('RGBA', 'LA'):
                        # 创建白色背景
                        background = Image.new('RGB', watermarked_img.size, (255, 255, 255))
                        if watermarked_img.mode == 'RGBA':
                            background.paste(watermarked_img, mask=watermarked_img.split()[-1])
                        else:
                            background.paste(watermarked_img)
                        watermarked_img = background
                    elif watermarked_img.mode != 'RGB':
                        watermarked_img = watermarked_img.convert('RGB')
                
                # 保存图片
                save_kwargs = {}
                if output_format.upper() == 'JPEG':
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                elif output_format.upper() == 'PNG':
                    save_kwargs['optimize'] = True
                
                watermarked_img.save(output_path, format=output_format.upper(), **save_kwargs)
                return True
                
        except Exception as e:
            if self.config.config.verbose:
                print(f"处理图片 {input_path} 时出错: {e}")
            return False
    
    def _resize_image(self, img: Image.Image, resize_config: dict) -> Image.Image:
        """调整图片尺寸"""
        if not resize_config.get('enabled', False):
            return img
            
        original_size = img.size
        resize_type = resize_config.get('type', 'none')
        
        if resize_type == 'width':
            new_width = resize_config.get('width', original_size[0])
            ratio = new_width / original_size[0]
            new_height = int(original_size[1] * ratio)
            new_size = (new_width, new_height)
        elif resize_type == 'height':
            new_height = resize_config.get('height', original_size[1])
            ratio = new_height / original_size[1]
            new_width = int(original_size[0] * ratio)
            new_size = (new_width, new_height)
        elif resize_type == 'percentage':
            percentage = resize_config.get('percentage', 100) / 100
            new_width = int(original_size[0] * percentage)
            new_height = int(original_size[1] * percentage)
            new_size = (new_width, new_height)
        elif resize_type == 'custom':
            new_width = resize_config.get('width', original_size[0])
            new_height = resize_config.get('height', original_size[1])
            if resize_config.get('keep_ratio', True):
                # 保持宽高比
                ratio = min(new_width / original_size[0], new_height / original_size[1])
                new_width = int(original_size[0] * ratio)
                new_height = int(original_size[1] * ratio)
            new_size = (new_width, new_height)
        else:
            return img
            
        return img.resize(new_size, Image.Resampling.LANCZOS)
    
    def preview_watermark(self, image: Image.Image, text: str) -> Image.Image:
        """预览水印效果（不保存）"""
        return self.add_watermark(image, text)
