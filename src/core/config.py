"""
配置管理模块

负责处理程序配置参数，包括水印样式、文件路径等设置。
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, Tuple
from enum import Enum


class Position(Enum):
    """水印位置枚举"""
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"


class DateFormat(Enum):
    """日期格式枚举"""
    YYYY_MM_DD = "YYYY-MM-DD"
    YYYY_MM_DD_SLASH = "YYYY/MM/DD"
    DD_MM_YYYY = "DD-MM-YYYY"
    DD_MM_YYYY_SLASH = "DD/MM/YYYY"
    MMM_DD_YYYY = "MMM DD, YYYY"
    DD_MMM_YYYY = "DD MMM YYYY"


@dataclass
class WatermarkConfig:
    """水印配置类"""
    # 字体设置
    font_size: Optional[int] = None  # None表示自适应
    font_color: str = "white"
    font_alpha: float = 0.8  # 透明度 0-1
    font_path: Optional[str] = None  # 自定义字体路径
    
    # 位置设置
    position: Position = Position.BOTTOM_RIGHT
    margin: int = 20  # 边距像素
    custom_position: Optional[Tuple[int, int]] = None  # 自定义坐标
    
    # 日期格式
    date_format: DateFormat = DateFormat.YYYY_MM_DD
    
    # 输出设置
    output_format: str = "JPEG"  # JPEG, PNG
    output_quality: int = 95  # JPEG质量 1-100
    
    # 处理设置
    recursive: bool = False
    preview_mode: bool = False
    verbose: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        # 转换枚举值
        data['position'] = self.position.value
        data['date_format'] = self.date_format.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WatermarkConfig':
        """从字典创建配置对象"""
        # 处理枚举值
        if 'position' in data:
            data['position'] = Position(data['position'])
        if 'date_format' in data:
            data['date_format'] = DateFormat(data['date_format'])
        
        return cls(**data)


class Config:
    """配置管理器"""
    
    def __init__(self, config: Optional[WatermarkConfig] = None):
        self.config = config or WatermarkConfig()
    
    def save_to_file(self, filepath: str) -> None:
        """保存配置到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"保存配置文件失败: {e}")
    
    def load_from_file(self, filepath: str) -> None:
        """从文件加载配置"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"配置文件不存在: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.config = WatermarkConfig.from_dict(data)
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {e}")
    
    def get_position_coordinates(self, image_width: int, image_height: int, 
                               text_width: int, text_height: int) -> Tuple[int, int]:
        """根据位置设置计算水印坐标"""
        if self.config.custom_position:
            return self.config.custom_position
        
        margin = self.config.margin
        
        position_map = {
            Position.TOP_LEFT: (margin, margin),
            Position.TOP_CENTER: ((image_width - text_width) // 2, margin),
            Position.TOP_RIGHT: (image_width - text_width - margin, margin),
            Position.CENTER_LEFT: (margin, (image_height - text_height) // 2),
            Position.CENTER: ((image_width - text_width) // 2, (image_height - text_height) // 2),
            Position.CENTER_RIGHT: (image_width - text_width - margin, (image_height - text_height) // 2),
            Position.BOTTOM_LEFT: (margin, image_height - text_height - margin),
            Position.BOTTOM_CENTER: ((image_width - text_width) // 2, image_height - text_height - margin),
            Position.BOTTOM_RIGHT: (image_width - text_width - margin, image_height - text_height - margin),
        }
        
        return position_map[self.config.position]
    
    def get_auto_font_size(self, image_width: int, image_height: int) -> int:
        """自动计算字体大小"""
        if self.config.font_size:
            return self.config.font_size
        
        # 根据图片尺寸自动计算字体大小
        # 取图片较小边的1/30作为基准字体大小
        base_size = min(image_width, image_height) // 30
        return max(16, min(base_size, 72))  # 限制在16-72像素之间
