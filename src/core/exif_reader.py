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
        # 对于不支持EXIF的格式（如BMP、PNG），直接使用文件修改时间
        if not self.can_read_exif(filepath):
            return self._get_file_modification_time(filepath)
        
        try:
            # 使用PIL读取EXIF信息
            with Image.open(filepath) as img:
                # 使用getexif()方法替代已弃用的_getexif()
                exif_data = img.getexif()
                
                if exif_data is not None and len(exif_data) > 0:
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        
                        # 优先使用DateTimeOriginal，其次是DateTime
                        if tag_name == 'DateTimeOriginal' or tag_name == 'DateTime':
                            try:
                                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            except ValueError:
                                continue
                
                # 如果PIL方法失败，尝试使用piexif
                piexif_result = self._extract_datetime_with_piexif(filepath)
                if piexif_result:
                    return piexif_result
                
                # 如果都失败了，使用文件修改时间作为备选
                return self._get_file_modification_time(filepath)
                
        except Exception as e:
            # 如果出现异常，尝试使用文件修改时间
            return self._get_file_modification_time(filepath)
    
    def _extract_datetime_with_piexif(self, filepath: str) -> Optional[datetime]:
        """使用piexif提取时间信息"""
        try:
            exif_dict = piexif.load(filepath)
            
            # 检查Exif IFD中的DateTimeOriginal
            if 'Exif' in exif_dict and exif_dict['Exif']:
                exif_ifd = exif_dict['Exif']
                if piexif.ExifIFD.DateTimeOriginal in exif_ifd:
                    datetime_bytes = exif_ifd[piexif.ExifIFD.DateTimeOriginal]
                    if isinstance(datetime_bytes, bytes):
                        datetime_str = datetime_bytes.decode('utf-8')
                    else:
                        datetime_str = str(datetime_bytes)
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            
            # 检查0th IFD中的DateTime
            if '0th' in exif_dict and exif_dict['0th']:
                zeroth_ifd = exif_dict['0th']
                if piexif.ImageIFD.DateTime in zeroth_ifd:
                    datetime_bytes = zeroth_ifd[piexif.ImageIFD.DateTime]
                    if isinstance(datetime_bytes, bytes):
                        datetime_str = datetime_bytes.decode('utf-8')
                    else:
                        datetime_str = str(datetime_bytes)
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            
            return None
            
        except Exception as e:
            # 静默处理，不输出错误信息
            return None
    
    def _get_file_modification_time(self, filepath: str) -> Optional[datetime]:
        """获取文件修改时间作为备选"""
        try:
            if os.path.exists(filepath):
                mtime = os.path.getmtime(filepath)
                return datetime.fromtimestamp(mtime)
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
                # 使用getexif()方法替代已弃用的_getexif()
                exif_data = img.getexif()
                
                if exif_data is not None and len(exif_data) > 0:
                    for tag, value in exif_data.items():
                        tag_name = TAGS.get(tag, tag)
                        exif_info[tag_name] = value
                        
        except Exception as e:
            exif_info['error'] = str(e)
        
        return exif_info
