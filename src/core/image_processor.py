"""
图像处理主模块

负责协调整个图片处理流程，包括文件扫描、EXIF读取、水印添加等。
"""

import os
import glob
from typing import List, Tuple, Optional, Generator
from pathlib import Path
from tqdm import tqdm
from PIL import Image

from .config import Config
from .exif_reader import ExifReader
from .watermark import WatermarkProcessor


class ImageProcessor:
    """图像处理器"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    
    def __init__(self, config: Config):
        self.config = config
        self.exif_reader = ExifReader()
        self.watermark_processor = WatermarkProcessor(config)
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'no_exif_files': 0,
            'skipped_files': 0
        }
    
    def is_supported_format(self, filepath: str) -> bool:
        """检查文件格式是否支持"""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.SUPPORTED_FORMATS
    
    def find_images(self, input_path: str) -> List[str]:
        """查找所有支持的图片文件"""
        image_files = []
        
        if os.path.isfile(input_path):
            # 单个文件
            if self.is_supported_format(input_path):
                image_files.append(input_path)
        elif os.path.isdir(input_path):
            # 目录
            if self.config.config.recursive:
                # 递归查找
                for ext in self.SUPPORTED_FORMATS:
                    pattern = os.path.join(input_path, '**', f'*{ext}')
                    image_files.extend(glob.glob(pattern, recursive=True))
                    pattern = os.path.join(input_path, '**', f'*{ext.upper()}')
                    image_files.extend(glob.glob(pattern, recursive=True))
            else:
                # 只查找当前目录
                for ext in self.SUPPORTED_FORMATS:
                    pattern = os.path.join(input_path, f'*{ext}')
                    image_files.extend(glob.glob(pattern))
                    pattern = os.path.join(input_path, f'*{ext.upper()}')
                    image_files.extend(glob.glob(pattern))
        
        # 去重并排序
        image_files = sorted(list(set(image_files)))
        
        if self.config.config.verbose:
            print(f"找到 {len(image_files)} 个图片文件")
        
        return image_files
    
    def get_output_path(self, input_path: str, input_root: str, 
                       output_root: str) -> str:
        """计算输出文件路径"""
        # 获取相对路径
        rel_path = os.path.relpath(input_path, input_root)
        
        # 构建输出路径
        output_path = os.path.join(output_root, rel_path)
        
        return output_path
    
    def create_output_directory(self, input_path: str) -> str:
        """创建输出目录"""
        if os.path.isfile(input_path):
            # 单个文件，在其目录下创建输出目录
            input_dir = os.path.dirname(input_path)
            dir_name = os.path.basename(input_dir) or "images"
        else:
            # 目录
            input_dir = input_path
            dir_name = os.path.basename(input_path.rstrip(os.sep))
        
        output_dir = os.path.join(input_dir, f"{dir_name}_watermark")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            if self.config.config.verbose:
                print(f"创建输出目录: {output_dir}")
        
        return output_dir
    
    def process_single_image(self, input_path: str, output_path: str, 
                           output_format: str = None, quality: int = 95, 
                           resize_config: dict = None) -> Tuple[bool, str]:
        """处理单张图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            output_format: 输出格式 ('JPEG' 或 'PNG')
            quality: JPEG质量 (1-100)
            resize_config: 尺寸调整配置
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息或成功信息)
        """
        try:
            # 提取拍摄时间
            watermark_text = self.exif_reader.get_watermark_text(
                input_path, self.config.config.date_format
            )
            
            if watermark_text is None:
                self.stats['no_exif_files'] += 1
                return False, "无法提取拍摄时间信息"
            
            # 预览模式
            if self.config.config.preview_mode:
                try:
                    with Image.open(input_path) as img:
                        preview_img = self.watermark_processor.preview_watermark(img, watermark_text)
                        # 这里可以添加预览显示逻辑
                        return True, f"预览水印文本: {watermark_text}"
                except Exception as e:
                    return False, f"预览失败: {e}"
            
            # 实际处理
            success = self.watermark_processor.process_image_with_options(
                input_path, output_path, watermark_text, 
                output_format, quality, resize_config
            )
            
            if success:
                self.stats['processed_files'] += 1
                return True, f"成功添加水印: {watermark_text}"
            else:
                self.stats['failed_files'] += 1
                return False, "水印处理失败"
                
        except Exception as e:
            self.stats['failed_files'] += 1
            return False, f"处理出错: {e}"
    
    def process_images(self, input_path: str, output_dir: Optional[str] = None) -> None:
        """批量处理图片"""
        # 查找所有图片文件
        image_files = self.find_images(input_path)
        
        if not image_files:
            print("未找到支持的图片文件")
            return
        
        # 创建输出目录
        if output_dir is None:
            output_dir = self.create_output_directory(input_path)
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # 确定输入根目录（用于计算相对路径）
        if os.path.isfile(input_path):
            input_root = os.path.dirname(input_path)
        else:
            input_root = input_path
        
        self.stats['total_files'] = len(image_files)
        
        # 处理进度条
        with tqdm(image_files, desc="处理图片", unit="张") as pbar:
            for image_file in pbar:
                # 计算输出路径
                output_path = self.get_output_path(image_file, input_root, output_dir)
                
                # 处理单张图片
                success, message = self.process_single_image(image_file, output_path)
                
                # 更新进度条描述
                filename = os.path.basename(image_file)
                if success:
                    pbar.set_postfix_str(f"✓ {filename}")
                else:
                    pbar.set_postfix_str(f"✗ {filename}")
                
                # 详细输出
                if self.config.config.verbose:
                    status = "成功" if success else "失败"
                    print(f"[{status}] {filename}: {message}")
        
        # 输出统计信息
        self.print_statistics()
    
    def print_statistics(self) -> None:
        """打印处理统计信息"""
        print("\n" + "="*50)
        print("处理统计:")
        print(f"总文件数: {self.stats['total_files']}")
        print(f"成功处理: {self.stats['processed_files']}")
        print(f"处理失败: {self.stats['failed_files']}")
        print(f"无EXIF信息: {self.stats['no_exif_files']}")
        
        if self.stats['total_files'] > 0:
            success_rate = (self.stats['processed_files'] / self.stats['total_files']) * 100
            print(f"成功率: {success_rate:.1f}%")
        
        print("="*50)
    
    def validate_input_path(self, input_path: str) -> bool:
        """验证输入路径"""
        if not os.path.exists(input_path):
            print(f"错误: 输入路径不存在: {input_path}")
            return False
        
        if os.path.isfile(input_path):
            if not self.is_supported_format(input_path):
                print(f"错误: 不支持的文件格式: {input_path}")
                return False
        elif os.path.isdir(input_path):
            # 检查目录中是否有支持的图片文件
            has_images = any(
                self.is_supported_format(f) 
                for f in os.listdir(input_path) 
                if os.path.isfile(os.path.join(input_path, f))
            )
            
            if not has_images and not self.config.config.recursive:
                print(f"警告: 目录中未找到支持的图片文件: {input_path}")
                print("提示: 使用 --recursive 选项可以递归搜索子目录")
        
        return True
