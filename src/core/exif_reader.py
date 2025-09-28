"""
EXIF信息读取模块

负责从图片文件中提取EXIF信息，特别是拍摄时间信息。
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS
import piexif

from .config import DateFormat


class ExifReader:
    """EXIF信息读取器"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif'}
    
    def can_read_exif(self, filepath: str) -> bool:
        """检查文件是否支持EXIF读取"""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.supported_formats
    
    def extract_datetime(self, filepath: str) -> Optional[datetime]:
        """提取图片的拍摄时间"""
        if not self.can_read_exif(filepath):
            return None
        
        try:
            # 使用PIL读取EXIF信息
            with Image.open(filepath) as img:
                exif_data = img._getexif()
                
                if exif_data is not None:
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        
                        # 优先使用DateTimeOriginal，其次是DateTime
                        if tag_name == 'DateTimeOriginal' or tag_name == 'DateTime':
                            try:
                                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            except ValueError:
                                continue
                
                # 如果PIL方法失败，尝试使用piexif
                return self._extract_datetime_with_piexif(filepath)
                
        except Exception as e:
            print(f"警告: 读取 {filepath} 的EXIF信息失败: {e}")
            return None
    
    def _extract_datetime_with_piexif(self, filepath: str) -> Optional[datetime]:
        """使用piexif提取时间信息"""
        try:
            exif_dict = piexif.load(filepath)
            
            # 检查Exif IFD中的DateTimeOriginal
            if 'Exif' in exif_dict:
                exif_ifd = exif_dict['Exif']
                if piexif.ExifIFD.DateTimeOriginal in exif_ifd:
                    datetime_str = exif_ifd[piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            
            # 检查0th IFD中的DateTime
            if '0th' in exif_dict:
                zeroth_ifd = exif_dict['0th']
                if piexif.ImageIFD.DateTime in zeroth_ifd:
                    datetime_str = zeroth_ifd[piexif.ImageIFD.DateTime].decode('utf-8')
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            
            return None
            
        except Exception:
            return None
    
    def format_date(self, dt: datetime, format_type: DateFormat) -> str:
        """格式化日期字符串"""
        if format_type == DateFormat.YYYY_MM_DD:
            return dt.strftime('%Y-%m-%d')
        elif format_type == DateFormat.YYYY_MM_DD_SLASH:
            return dt.strftime('%Y/%m/%d')
        elif format_type == DateFormat.DD_MM_YYYY:
            return dt.strftime('%d-%m-%Y')
        elif format_type == DateFormat.DD_MM_YYYY_SLASH:
            return dt.strftime('%d/%m/%Y')
        elif format_type == DateFormat.MMM_DD_YYYY:
            return dt.strftime('%b %d, %Y')
        elif format_type == DateFormat.DD_MMM_YYYY:
            return dt.strftime('%d %b %Y')
        else:
            return dt.strftime('%Y-%m-%d')  # 默认格式
    
    def get_watermark_text(self, filepath: str, format_type: DateFormat) -> Optional[str]:
        """获取用于水印的文本"""
        dt = self.extract_datetime(filepath)
        if dt is None:
            return None
        
        return self.format_date(dt, format_type)
    
    def get_all_exif_info(self, filepath: str) -> Dict[str, Any]:
        """获取所有EXIF信息（用于调试）"""
        exif_info = {}
        
        if not self.can_read_exif(filepath):
            return exif_info
        
        try:
            with Image.open(filepath) as img:
                exif_data = img._getexif()
                
                if exif_data is not None:
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        exif_info[tag_name] = value
                        
        except Exception as e:
            exif_info['error'] = str(e)
        
        return exif_info
