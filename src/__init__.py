"""
PhotoWatermark - 基于EXIF拍摄时间的图片水印工具

一个命令行程序，能够自动读取图片的EXIF信息中的拍摄时间，
并将其作为水印添加到图片上。
"""

__version__ = "1.0.0"
__author__ = "PhotoWatermark Team"
__email__ = "contact@photowatermark.com"

from .core.image_processor import ImageProcessor
from .core.watermark import WatermarkProcessor
from .core.exif_reader import ExifReader
from .core.config import Config

__all__ = [
    'ImageProcessor',
    'WatermarkProcessor', 
    'ExifReader',
    'Config'
]
