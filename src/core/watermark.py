"""
水印处理模块

负责在图片上绘制文本水印。
"""

import os
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL.ImageColor import getcolor

from .config import Config, WatermarkConfig, WatermarkType, TextWatermarkConfig, ImageWatermarkConfig, ScaleMode
from ..utils.font_manager import font_manager


class WatermarkProcessor:
    """水印处理器"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def _get_font(self, font_size: int, font_path: Optional[str] = None, 
                  bold: bool = False, italic: bool = False) -> ImageFont.ImageFont:
        """获取字体对象"""
        # 优先使用指定的字体路径
        target_font_path = font_path or self.config.config.font_path
        
        # 使用字体管理器获取字体
        return font_manager.get_font(target_font_path, font_size, bold, italic)
    
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
    
    def _scale_watermark_image(self, watermark_img: Image.Image, target_size: Tuple[int, int], 
                              img_config: ImageWatermarkConfig) -> Image.Image:
        """缩放水印图片"""
        target_width, target_height = target_size
        
        if img_config.scale_mode == ScaleMode.PERCENTAGE:
            # 按百分比缩放
            scale_factor = img_config.scale_percentage / 100.0
            new_width = int(watermark_img.width * scale_factor)
            new_height = int(watermark_img.height * scale_factor)
        elif img_config.scale_mode == ScaleMode.PIXEL:
            # 按像素缩放
            if img_config.keep_aspect_ratio:
                # 保持宽高比
                ratio = min(img_config.scale_width / watermark_img.width,
                           img_config.scale_height / watermark_img.height)
                new_width = int(watermark_img.width * ratio)
                new_height = int(watermark_img.height * ratio)
            else:
                new_width = img_config.scale_width
                new_height = img_config.scale_height
        else:  # ADAPTIVE
            # 自适应缩放（基于目标图片大小）
            max_size = min(target_width, target_height) // 4  # 不超过目标图片的1/4
            ratio = min(max_size / watermark_img.width, max_size / watermark_img.height)
            new_width = int(watermark_img.width * ratio)
            new_height = int(watermark_img.height * ratio)
        
        # 限制最小尺寸
        new_width = max(20, new_width)
        new_height = max(20, new_height)
        
        return watermark_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _transform_watermark_image(self, watermark_img: Image.Image, 
                                  img_config: ImageWatermarkConfig) -> Image.Image:
        """变换水印图片（旋转、翻转）"""
        result = watermark_img
        
        # 翻转
        if img_config.flip_horizontal:
            result = result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if img_config.flip_vertical:
            result = result.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        # 旋转
        if img_config.rotation != 0:
            result = result.rotate(img_config.rotation, expand=True, fillcolor=(0, 0, 0, 0))
        
        return result
    
    def _apply_watermark_alpha(self, watermark_img: Image.Image, alpha: float) -> Image.Image:
        """应用透明度到水印图片"""
        if watermark_img.mode != 'RGBA':
            watermark_img = watermark_img.convert('RGBA')
        
        # 创建一个新的图片，调整alpha通道
        data = watermark_img.getdata()
        new_data = []
        
        for item in data:
            # item是(R, G, B, A)
            new_alpha = int(item[3] * alpha) if len(item) == 4 else int(255 * alpha)
            new_data.append(item[:3] + (new_alpha,))
        
        result = Image.new('RGBA', watermark_img.size)
        result.putdata(new_data)
        return result
    
    def process_watermark(self, image: Image.Image, text: Optional[str] = None) -> Image.Image:
        """根据配置类型处理水印"""
        watermark_type = self.config.config.watermark_type
        
        if watermark_type == WatermarkType.TIMESTAMP:
            # 时间水印（原有功能）
            if text is None:
                raise ValueError("时间水印需要提供文本内容")
            result = self.add_watermark(image, text)
        elif watermark_type == WatermarkType.TEXT:
            # 文本水印
            result = self.add_text_watermark(image)
        elif watermark_type == WatermarkType.IMAGE:
            # 图片水印
            result = self.add_image_watermark(image)
        else:
            raise ValueError(f"不支持的水印类型: {watermark_type}")
        
        # 确保返回的图片格式与输出格式兼容
        if hasattr(self.config.config, 'output_format') and self.config.config.output_format.upper() == 'JPEG':
            if result.mode in ('RGBA', 'LA'):
                # 创建白色背景
                background = Image.new('RGB', result.size, (255, 255, 255))
                if result.mode == 'RGBA':
                    background.paste(result, mask=result.split()[-1])
                else:
                    background.paste(result)
                result = background
            elif result.mode != 'RGB':
                result = result.convert('RGB')
        
        return result
    
    def add_text_watermark(self, image: Image.Image) -> Image.Image:
        """添加自定义文本水印"""
        text_config = self.config.config.text_watermark
        
        if not text_config.text.strip():
            return image.copy()  # 如果没有文本内容，返回原图
        
        # 创建副本以避免修改原图
        watermarked_image = image.copy()
        
        # 获取图片尺寸
        img_width, img_height = watermarked_image.size
        
        # 计算字体大小
        font_size = text_config.font_size or self.config.get_auto_font_size(img_width, img_height)
        font = self._get_font(
            font_size, 
            text_config.font_path, 
            text_config.font_bold, 
            text_config.font_italic
        )
        
        # 获取文本尺寸
        text_width, text_height = self._get_text_size(text_config.text, font)
        
        # 计算水印位置
        x, y = self.config.get_position_coordinates(
            img_width, img_height, text_width, text_height
        )
        
        # 解析颜色和透明度
        color_rgb = self._parse_color(text_config.font_color)
        alpha = int(text_config.font_alpha * 255)
        text_color = color_rgb + (alpha,)
        
        # 创建透明层用于绘制水印
        overlay = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 绘制阴影效果
        if text_config.shadow_enabled:
            shadow_x = x + text_config.shadow_offset_x
            shadow_y = y + text_config.shadow_offset_y
            shadow_color_rgb = self._parse_color(text_config.shadow_color)
            shadow_alpha = int(text_config.shadow_alpha * 255)
            shadow_color = shadow_color_rgb + (shadow_alpha,)
            
            if text_config.shadow_blur > 0:
                # 创建模糊阴影
                shadow_overlay = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow_overlay)
                shadow_draw.text((shadow_x, shadow_y), text_config.text, font=font, fill=shadow_color)
                shadow_overlay = shadow_overlay.filter(ImageFilter.GaussianBlur(text_config.shadow_blur))
                overlay = Image.alpha_composite(overlay, shadow_overlay)
            else:
                # 绘制普通阴影
                draw.text((shadow_x, shadow_y), text_config.text, font=font, fill=shadow_color)
        
        # 绘制描边效果
        if text_config.stroke_enabled:
            stroke_color_rgb = self._parse_color(text_config.stroke_color)
            stroke_color = stroke_color_rgb + (255,)  # 描边不透明
            
            # 绘制描边（通过在周围绘制多次文本实现）
            for dx in range(-text_config.stroke_width, text_config.stroke_width + 1):
                for dy in range(-text_config.stroke_width, text_config.stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text_config.text, font=font, fill=stroke_color)
        
        # 绘制主文本
        draw.text((x, y), text_config.text, font=font, fill=text_color)
        
        # 合并透明层到原图
        if watermarked_image.mode != 'RGBA':
            watermarked_image = watermarked_image.convert('RGBA')
        
        watermarked_image = Image.alpha_composite(watermarked_image, overlay)
        
        # 如果原图不是RGBA模式，转换回原模式
        if image.mode != 'RGBA':
            watermarked_image = watermarked_image.convert(image.mode)
        
        return watermarked_image
    
    def add_image_watermark(self, image: Image.Image) -> Image.Image:
        """添加图片水印"""
        img_config = self.config.config.image_watermark
        
        if not img_config.image_path or not os.path.exists(img_config.image_path):
            return image.copy()  # 如果没有水印图片，返回原图
        
        # 创建副本以避免修改原图
        watermarked_image = image.copy()
        
        try:
            # 打开水印图片
            with Image.open(img_config.image_path) as watermark_img:
                watermark_img = watermark_img.copy()
                
                # 处理缩放
                watermark_img = self._scale_watermark_image(watermark_img, watermarked_image.size, img_config)
                
                # 处理旋转和翻转
                watermark_img = self._transform_watermark_image(watermark_img, img_config)
                
                # 处理透明度
                if img_config.alpha < 1.0:
                    watermark_img = self._apply_watermark_alpha(watermark_img, img_config.alpha)
                
                # 计算水印位置
                wm_width, wm_height = watermark_img.size
                x, y = self.config.get_position_coordinates(
                    watermarked_image.width, watermarked_image.height, wm_width, wm_height
                )
                
                # 合并水印到原图
                if watermark_img.mode == 'RGBA' or 'transparency' in watermark_img.info:
                    # 有透明通道的水印
                    if watermarked_image.mode != 'RGBA':
                        watermarked_image = watermarked_image.convert('RGBA')
                    
                    # 创建一个与原图同尺寸的透明层
                    overlay = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
                    overlay.paste(watermark_img, (x, y), watermark_img if watermark_img.mode == 'RGBA' else None)
                    watermarked_image = Image.alpha_composite(watermarked_image, overlay)
                else:
                    # 没有透明通道的水印
                    watermarked_image.paste(watermark_img, (x, y))
                
                return watermarked_image
                
        except Exception as e:
            if self.config.config.verbose:
                print(f"添加图片水印失败: {e}")
            return image.copy()
    
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
                                 watermark_text: str = None, output_format: str = None, 
                                 quality: int = 95, resize_config: dict = None) -> bool:
        """处理单张图片（带完整选项）"""
        try:
            # 打开图片
            with Image.open(input_path) as img:
                # 调整图片尺寸
                if resize_config and resize_config.get('enabled', False):
                    img = self._resize_image(img, resize_config)
                
                # 根据水印类型添加水印
                watermarked_img = self.process_watermark(img, watermark_text)
                
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
