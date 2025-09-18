"""
颜色处理工具函数
"""

import re
from typing import Tuple, Optional, Dict


# 预定义颜色映射
COLOR_NAMES = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'gray': (128, 128, 128),
    'grey': (128, 128, 128),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'brown': (165, 42, 42),
    'pink': (255, 192, 203),
    'lime': (0, 255, 0),
    'navy': (0, 0, 128),
    'teal': (0, 128, 128),
    'silver': (192, 192, 192),
    'gold': (255, 215, 0),
}


def parse_color(color_str: str) -> Optional[Tuple[int, int, int]]:
    """解析颜色字符串
    
    支持的格式:
    - 颜色名称: 'white', 'black', 'red' 等
    - 十六进制: '#FF0000', '#ff0000', 'FF0000'
    - RGB: 'rgb(255,0,0)', 'RGB(255, 0, 0)'
    - 逗号分隔: '255,0,0'
    """
    color_str = color_str.strip().lower()
    
    # 颜色名称
    if color_str in COLOR_NAMES:
        return COLOR_NAMES[color_str]
    
    # 十六进制颜色
    hex_match = re.match(r'^#?([0-9a-f]{6})$', color_str)
    if hex_match:
        hex_color = hex_match.group(1)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    
    # RGB格式
    rgb_match = re.match(r'^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$', color_str)
    if rgb_match:
        r, g, b = map(int, rgb_match.groups())
        if all(0 <= c <= 255 for c in (r, g, b)):
            return (r, g, b)
    
    # 逗号分隔的RGB
    comma_match = re.match(r'^(\d+)\s*,\s*(\d+)\s*,\s*(\d+)$', color_str)
    if comma_match:
        r, g, b = map(int, comma_match.groups())
        if all(0 <= c <= 255 for c in (r, g, b)):
            return (r, g, b)
    
    return None


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """RGB转十六进制"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def get_contrast_color(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """获取对比色（黑色或白色）"""
    # 计算亮度
    brightness = (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114)
    return (0, 0, 0) if brightness > 128 else (255, 255, 255)


def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                ratio: float) -> Tuple[int, int, int]:
    """混合两种颜色
    
    Args:
        color1: 第一种颜色
        color2: 第二种颜色  
        ratio: 混合比例 (0.0 = 完全是color1, 1.0 = 完全是color2)
    """
    ratio = max(0.0, min(1.0, ratio))  # 限制在0-1之间
    
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    
    return (r, g, b)


def adjust_brightness(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """调整颜色亮度
    
    Args:
        rgb: RGB颜色值
        factor: 亮度因子 (< 1.0 变暗, > 1.0 变亮)
    """
    r, g, b = rgb
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return (r, g, b)


def get_available_colors() -> Dict[str, Tuple[int, int, int]]:
    """获取所有可用的颜色名称"""
    return COLOR_NAMES.copy()
