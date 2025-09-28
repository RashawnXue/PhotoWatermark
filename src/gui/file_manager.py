"""
文件管理器

处理文件导入、导出和格式转换。
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Callable
from PIL import Image
import threading

from ..utils.file_utils import list_files_by_extension


class FileManager:
    """文件管理器类"""
    
    def __init__(self):
        self.supported_input_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        self.supported_output_formats = {'JPEG', 'PNG'}
        
    def get_image_files_from_paths(self, paths: List[str], recursive: bool = False) -> List[str]:
        """从路径列表获取所有图片文件"""
        image_files = []
        
        for path in paths:
            if os.path.isfile(path):
                # 单个文件
                if self.is_supported_image(path):
                    image_files.append(path)
            elif os.path.isdir(path):
                # 目录
                image_files.extend(self.get_images_from_directory(path, recursive))
                
        return image_files
        
    def get_images_from_directory(self, directory: str, recursive: bool = False) -> List[str]:
        """从目录获取图片文件"""
        extensions = list(self.supported_input_formats)
        return list_files_by_extension(directory, extensions, recursive)
        
    def is_supported_image(self, file_path: str) -> bool:
        """检查是否为支持的图片格式"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_input_formats
        
    def get_image_info(self, file_path: str) -> Dict:
        """获取图片信息"""
        try:
            with Image.open(file_path) as img:
                return {
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'file_size': os.path.getsize(file_path),
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            return {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'error': str(e)
            }
            
    def validate_output_directory(self, output_dir: str, input_files: List[str]) -> tuple:
        """验证输出目录"""
        if not output_dir:
            return False, "请选择输出目录"
            
        # 检查目录是否存在
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                return False, f"无法创建输出目录: {e}"
                
        # 检查写入权限
        if not os.access(output_dir, os.W_OK):
            return False, "输出目录没有写入权限"
            
        # 检查是否与输入文件目录冲突
        output_path = Path(output_dir).resolve()
        for input_file in input_files:
            input_dir = Path(input_file).parent.resolve()
            if output_path == input_dir:
                return False, "为防止覆盖原图，不能导出到原文件目录"
                
        return True, ""
        
    def generate_output_filename(self, input_path: str, naming_rule: Dict, output_format: str) -> str:
        """生成输出文件名"""
        input_name = Path(input_path).stem
        
        # 应用命名规则
        if naming_rule.get('type') == 'prefix':
            output_name = f"{naming_rule.get('value', '')}{input_name}"
        elif naming_rule.get('type') == 'suffix':
            output_name = f"{input_name}{naming_rule.get('value', '')}"
        else:
            output_name = input_name
            
        # 添加扩展名
        if output_format.upper() == 'JPEG':
            ext = '.jpg'
        elif output_format.upper() == 'PNG':
            ext = '.png'
        else:
            ext = Path(input_path).suffix
            
        return f"{output_name}{ext}"
        
    def resize_image(self, image: Image.Image, resize_config: Dict) -> Image.Image:
        """调整图片尺寸"""
        if not resize_config.get('enabled', False):
            return image
            
        original_size = image.size
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
            return image
            
        return image.resize(new_size, Image.Resampling.LANCZOS)
        
    def save_image(self, image: Image.Image, output_path: str, 
                  output_format: str, quality: int = 95) -> bool:
        """保存图片"""
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if output_format.upper() == 'JPEG':
                # 如果原图有透明通道，需要转换为RGB
                if image.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                    
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
            elif output_format.upper() == 'PNG':
                image.save(output_path, 'PNG', optimize=True)
            else:
                image.save(output_path)
                
            return True
        except Exception as e:
            print(f"保存图片失败 {output_path}: {e}")
            return False
            
    def process_images_async(self, input_files: List[str], output_dir: str,
                           naming_rule: Dict, output_format: str, quality: int,
                           resize_config: Dict, watermark_processor,
                           progress_callback: Optional[Callable] = None,
                           complete_callback: Optional[Callable] = None):
        """异步处理图片"""
        def process():
            try:
                total_files = len(input_files)
                processed_files = []
                failed_files = []
                
                for i, input_file in enumerate(input_files):
                    # 检查是否取消
                    if progress_callback and hasattr(progress_callback, '__self__'):
                        if getattr(progress_callback.__self__, 'cancelled', False):
                            break
                            
                    try:
                        # 更新进度
                        if progress_callback:
                            progress = (i / total_files) * 100
                            status = f"正在处理: {os.path.basename(input_file)}"
                            progress_callback(progress, status)
                            
                        # 处理图片
                        success = self._process_single_image(
                            input_file, output_dir, naming_rule, 
                            output_format, quality, resize_config, 
                            watermark_processor
                        )
                        
                        if success:
                            processed_files.append(input_file)
                        else:
                            failed_files.append(input_file)
                            
                    except Exception as e:
                        print(f"处理图片失败 {input_file}: {e}")
                        failed_files.append(input_file)
                        
                # 完成回调
                if complete_callback:
                    complete_callback(processed_files, failed_files)
                    
            except Exception as e:
                print(f"批量处理失败: {e}")
                if complete_callback:
                    complete_callback([], input_files)
                    
        # 在新线程中执行
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
        
    def _process_single_image(self, input_file: str, output_dir: str,
                            naming_rule: Dict, output_format: str, quality: int,
                            resize_config: Dict, watermark_processor) -> bool:
        """处理单张图片"""
        try:
            # 生成输出文件名
            output_filename = self.generate_output_filename(
                input_file, naming_rule, output_format
            )
            output_path = os.path.join(output_dir, output_filename)
            
            # 处理文件名冲突
            counter = 1
            base_path = output_path
            while os.path.exists(output_path):
                name, ext = os.path.splitext(base_path)
                output_path = f"{name}_{counter}{ext}"
                counter += 1
                
            # 使用水印处理器处理图片
            if watermark_processor:
                success = watermark_processor.process_single_image(
                    input_file, output_path, output_format, quality, resize_config
                )
                return success
            else:
                # 如果没有水印处理器，直接复制并调整尺寸
                with Image.open(input_file) as img:
                    # 调整尺寸
                    img = self.resize_image(img, resize_config)
                    
                    # 保存图片
                    return self.save_image(img, output_path, output_format, quality)
                    
        except Exception as e:
            print(f"处理单张图片失败 {input_file}: {e}")
            return False
