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
        """获取文本尺寸（支持多行文本）"""
        # 创建临时图像来测量文本大小
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        
        # 处理多行文本
        lines = text.split('\n')
        max_width = 0
        total_height = 0
        
        for i, line in enumerate(lines):
            # 获取每行的尺寸
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            
            max_width = max(max_width, line_width)
            total_height += line_height
            
            # 添加行间距（除了最后一行）
            if i < len(lines) - 1:
                total_height += int(line_height * 0.2)  # 20%的行间距
        
        return max_width, total_height
    
    def _draw_multiline_text(self, draw: ImageDraw.ImageDraw, position: Tuple[int, int], 
                            text: str, font: ImageFont.ImageFont, fill: Tuple[int, int, int, int]):
        """绘制多行文本"""
        x, y = position
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():  # 跳过空行
                draw.text((x, y), line, font=font, fill=fill)
            
            # 计算下一行的Y位置
            if i < len(lines) - 1:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                y += line_height + int(line_height * 0.2)  # 添加20%行间距
    
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
        
        # 为了支持旋转，我们在单独的透明图层上绘制文本和效果，然后旋转该层并粘贴回原图
        # 创建最小透明层，仅包含文本区域以减少旋转开销
        text_layer = Image.new('RGBA', (text_width + 10, text_height + 10), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(text_layer)

        # 在局部层上绘制阴影、描边和主文本（使用相对于局部层的坐标）
        local_x = 5
        local_y = 5

        # 阴影
        if text_config.shadow_enabled:
            shadow_color_rgb = self._parse_color(text_config.shadow_color)
            shadow_alpha = int(text_config.shadow_alpha * 255)
            shadow_color = shadow_color_rgb + (shadow_alpha,)
            shadow_x = local_x + text_config.shadow_offset_x
            shadow_y = local_y + text_config.shadow_offset_y

            if text_config.shadow_blur > 0:
                shadow_overlay = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow_overlay)
                self._draw_multiline_text(shadow_draw, (shadow_x, shadow_y), text_config.text, font, shadow_color)
                shadow_overlay = shadow_overlay.filter(ImageFilter.GaussianBlur(text_config.shadow_blur))
                text_layer = Image.alpha_composite(text_layer, shadow_overlay)
            else:
                self._draw_multiline_text(layer_draw, (shadow_x, shadow_y), text_config.text, font, shadow_color)

        # 描边
        if text_config.stroke_enabled:
            stroke_color_rgb = self._parse_color(text_config.stroke_color)
            stroke_color = stroke_color_rgb + (255,)
            for dx in range(-text_config.stroke_width, text_config.stroke_width + 1):
                for dy in range(-text_config.stroke_width, text_config.stroke_width + 1):
                    if dx == 0 and dy == 0:
                        continue
                    self._draw_multiline_text(layer_draw, (local_x + dx, local_y + dy), text_config.text, font, stroke_color)

        # 主文本
        self._draw_multiline_text(layer_draw, (local_x, local_y), text_config.text, font, text_color)

        # 旋转局部层
        rot_angle = 0.0
        try:
            rot_angle = float(getattr(text_config, 'rotation', 0.0))
        except Exception:
            rot_angle = 0.0

        if rot_angle != 0:
            # rotate会改变尺寸，使用expand=True
            rotated_layer = text_layer.rotate(-rot_angle, expand=True, resample=Image.Resampling.BICUBIC)
        else:
            rotated_layer = text_layer

        # 将旋转后的局部层粘贴到目标位置（x,y 为原始图片上的位置）
        paste_x = x - (rotated_layer.width - text_layer.width) // 2
        paste_y = y - (rotated_layer.height - text_layer.height) // 2

        if watermarked_image.mode != 'RGBA':
            watermarked_image = watermarked_image.convert('RGBA')

        # 创建overlay并粘贴
        overlay = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
        overlay.paste(rotated_layer, (paste_x, paste_y), rotated_layer)
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
        
        # 计算并使用配置的字体大小（优先使用显式配置的 font_size）
        configured_size = None
        try:
            configured_size = self.config.config.font_size
        except Exception:
            configured_size = None

        if configured_size is not None:
            font_size = configured_size
        else:
            font_size = self.config.get_auto_font_size(img_width, img_height)

        # 使用配置的字体路径（如果有）
        font_path = None
        try:
            font_path = self.config.config.font_path
        except Exception:
            font_path = None

        # 优先使用 text_watermark 中设置的字体路径（如果存在），否则使用全局 font_path
        try:
            tw_fp = getattr(self.config.config, 'text_watermark', None)
            if tw_fp and getattr(tw_fp, 'font_path', None):
                font = self._get_font(font_size, tw_fp.font_path)
            else:
                font = self._get_font(font_size, font_path)
        except Exception:
            font = self._get_font(font_size, font_path)

        # 获取文本尺寸
        text_width, text_height = self._get_text_size(text, font)

        # 计算水印位置
        x, y = self.config.get_position_coordinates(
            img_width, img_height, text_width, text_height
        )

        # 解析颜色
        color = self._parse_color(self.config.config.font_color)

        # 准备颜色带alpha
        alpha = int(self.config.config.font_alpha * 255)
        color_with_alpha = (*color, alpha)

        # 使用与 add_text_watermark 类似的流程：在局部层绘制文本与效果，然后旋转并合并
        text_layer = Image.new('RGBA', (text_width + 10, text_height + 10), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(text_layer)
        local_x = 5
        local_y = 5

        # 阴影（如果配置在 text_watermark 中）
        try:
            tw_cfg = self.config.config.text_watermark
        except Exception:
            tw_cfg = None

        if tw_cfg and getattr(tw_cfg, 'shadow_enabled', False):
            shadow_color_rgb = self._parse_color(tw_cfg.shadow_color)
            shadow_alpha = int(tw_cfg.shadow_alpha * 255)
            shadow_color = shadow_color_rgb + (shadow_alpha,)
            shadow_x = local_x + getattr(tw_cfg, 'shadow_offset_x', 2)
            shadow_y = local_y + getattr(tw_cfg, 'shadow_offset_y', 2)

            if getattr(tw_cfg, 'shadow_blur', 0) > 0:
                shadow_overlay = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow_overlay)
                self._draw_multiline_text(shadow_draw, (shadow_x, shadow_y), text, font, shadow_color)
                shadow_overlay = shadow_overlay.filter(ImageFilter.GaussianBlur(getattr(tw_cfg, 'shadow_blur', 0)))
                text_layer = Image.alpha_composite(text_layer, shadow_overlay)
            else:
                self._draw_multiline_text(layer_draw, (shadow_x, shadow_y), text, font, shadow_color)

        # 描边
        if tw_cfg and getattr(tw_cfg, 'stroke_enabled', False):
            stroke_color_rgb = self._parse_color(getattr(tw_cfg, 'stroke_color', 'black'))
            stroke_color = stroke_color_rgb + (255,)
            stroke_w = getattr(tw_cfg, 'stroke_width', 1)
            for dx in range(-stroke_w, stroke_w + 1):
                for dy in range(-stroke_w, stroke_w + 1):
                    if dx == 0 and dy == 0:
                        continue
                    self._draw_multiline_text(layer_draw, (local_x + dx, local_y + dy), text, font, stroke_color)

        # 主文本
        self._draw_multiline_text(layer_draw, (local_x, local_y), text, font, color_with_alpha)

        # 旋转（优先使用 text_watermark.rotation，如果不存在则0）
        rot_angle = 0.0
        if tw_cfg is not None:
            try:
                rot_angle = float(getattr(tw_cfg, 'rotation', 0.0))
            except Exception:
                rot_angle = 0.0

        if rot_angle != 0:
            rotated_layer = text_layer.rotate(-rot_angle, expand=True, resample=Image.Resampling.BICUBIC)
        else:
            rotated_layer = text_layer

        paste_x = x - (rotated_layer.width - text_layer.width) // 2
        paste_y = y - (rotated_layer.height - text_layer.height) // 2

        if watermarked_image.mode != 'RGBA':
            watermarked_image = watermarked_image.convert('RGBA')

        overlay = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
        overlay.paste(rotated_layer, (paste_x, paste_y), rotated_layer)
        watermarked_image = Image.alpha_composite(watermarked_image, overlay)

        # 如果输出格式不支持透明度且需要转换为RGB（例如JPEG），在调用方会处理
        if image.mode != 'RGBA':
            watermarked_image = watermarked_image.convert(image.mode)

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
        # 保持向后兼容：返回合成图像
        img, _ = self.preview_with_bbox(image, text)
        return img

    def preview_with_bbox(self, image: Image.Image, text: str):
        """生成带水印的预览图，并返回水印在原始图片坐标系下的包围盒

        返回: (watermarked_image: Image.Image, watermark_bbox: Optional[Tuple[int,int,int,int]])
        watermark_bbox 是 (left, top, width, height) 或 None
        """
        # 仅处理文本和图片两类水印
        watermark_type = self.config.config.watermark_type
        base_img = image.copy()
        overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))

        if watermark_type == WatermarkConfig.watermark_type.__class__:
            # defensive fallback
            pass

        if watermark_type == WatermarkConfig.watermark_type.__class__:
            pass

        if watermark_type.name == 'TEXT' or watermark_type.name == 'TIMESTAMP' or watermark_type.name == 'TEXT':
            # 文本类（包括时间戳）
            try:
                # 获取字体大小与路径
                font_size = None
                try:
                    font_size = self.config.config.font_size
                except Exception:
                    font_size = None

                if font_size is None:
                    font_size = self.config.get_auto_font_size(base_img.width, base_img.height)

                # 优先使用 text_watermark 的 font_path
                try:
                    tw_fp = getattr(self.config.config, 'text_watermark', None)
                    if tw_fp and getattr(tw_fp, 'font_path', None):
                        font = self._get_font(font_size, tw_fp.font_path)
                    else:
                        font = self._get_font(font_size, self.config.config.font_path)
                except Exception:
                    font = self._get_font(font_size, self.config.config.font_path)
                text_content = text or ''
                text_width, text_height = self._get_text_size(text_content, font)

                # 构建局部层并绘制文本（重用 add_watermark 中的局部绘制方式)
                text_layer = Image.new('RGBA', (text_width + 10, text_height + 10), (0, 0, 0, 0))
                layer_draw = ImageDraw.Draw(text_layer)
                local_x = 5
                local_y = 5

                tw_cfg = getattr(self.config.config, 'text_watermark', None)
                # 阴影
                if tw_cfg and getattr(tw_cfg, 'shadow_enabled', False):
                    shadow_color_rgb = self._parse_color(tw_cfg.shadow_color)
                    shadow_alpha = int(tw_cfg.shadow_alpha * 255)
                    shadow_color = shadow_color_rgb + (shadow_alpha,)
                    shadow_x = local_x + getattr(tw_cfg, 'shadow_offset_x', 2)
                    shadow_y = local_y + getattr(tw_cfg, 'shadow_offset_y', 2)
                    if getattr(tw_cfg, 'shadow_blur', 0) > 0:
                        shadow_overlay = Image.new('RGBA', text_layer.size, (0, 0, 0, 0))
                        shadow_draw = ImageDraw.Draw(shadow_overlay)
                        self._draw_multiline_text(shadow_draw, (shadow_x, shadow_y), text_content, font, shadow_color)
                        shadow_overlay = shadow_overlay.filter(ImageFilter.GaussianBlur(getattr(tw_cfg, 'shadow_blur', 0)))
                        text_layer = Image.alpha_composite(text_layer, shadow_overlay)
                    else:
                        self._draw_multiline_text(layer_draw, (shadow_x, shadow_y), text_content, font, shadow_color)

                # 描边
                if tw_cfg and getattr(tw_cfg, 'stroke_enabled', False):
                    stroke_color_rgb = self._parse_color(getattr(tw_cfg, 'stroke_color', 'black'))
                    stroke_color = stroke_color_rgb + (255,)
                    stroke_w = getattr(tw_cfg, 'stroke_width', 1)
                    for dx in range(-stroke_w, stroke_w + 1):
                        for dy in range(-stroke_w, stroke_w + 1):
                            if dx == 0 and dy == 0:
                                continue
                            self._draw_multiline_text(layer_draw, (local_x + dx, local_y + dy), text_content, font, stroke_color)

                # 主文本
                color = self._parse_color(self.config.config.font_color)
                alpha = int(self.config.config.font_alpha * 255)
                color_with_alpha = (*color, alpha)
                self._draw_multiline_text(layer_draw, (local_x, local_y), text_content, font, color_with_alpha)

                rot_angle = 0.0
                try:
                    rot_angle = float(getattr(tw_cfg, 'rotation', 0.0))
                except Exception:
                    rot_angle = 0.0

                if rot_angle != 0:
                    rotated_layer = text_layer.rotate(-rot_angle, expand=True, resample=Image.Resampling.BICUBIC)
                else:
                    rotated_layer = text_layer

                # 计算位置
                text_wm_width, text_wm_height = rotated_layer.size
                x, y = self.config.get_position_coordinates(base_img.width, base_img.height, text_wm_width, text_wm_height)
                paste_x = x
                paste_y = y
                overlay.paste(rotated_layer, (paste_x, paste_y), rotated_layer)
            except Exception:
                pass

        elif watermark_type == WatermarkConfig.image_watermark.__class__ or watermark_type.name == 'IMAGE':
            # 图片水印
            try:
                img_cfg = self.config.config.image_watermark
                if img_cfg and img_cfg.image_path and os.path.exists(img_cfg.image_path):
                    with Image.open(img_cfg.image_path) as wm_img:
                        wm = wm_img.copy()
                        wm = self._scale_watermark_image(wm, base_img.size, img_cfg)
                        wm = self._transform_watermark_image(wm, img_cfg)
                        if img_cfg.alpha < 1.0:
                            wm = self._apply_watermark_alpha(wm, img_cfg.alpha)
                        wm_w, wm_h = wm.size
                        x, y = self.config.get_position_coordinates(base_img.width, base_img.height, wm_w, wm_h)
                        overlay.paste(wm, (x, y), wm if wm.mode == 'RGBA' else None)
            except Exception:
                pass

        # 合并并计算bbox
        result = base_img.copy()
        if result.mode != 'RGBA':
            result = result.convert('RGBA')
        if overlay.getbbox():
            bbox = overlay.getbbox()  # (left, upper, right, lower)
            wm_left, wm_top, wm_right, wm_bottom = bbox
            watermark_bbox = (wm_left, wm_top, wm_right - wm_left, wm_bottom - wm_top)
            result = Image.alpha_composite(result, overlay)
        else:
            watermark_bbox = None
            result = Image.alpha_composite(result, overlay)

        # 如果原图不是RGBA，返回原模式图
        if image.mode != 'RGBA':
            result = result.convert(image.mode)

        return result, watermark_bbox
