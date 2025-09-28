"""
字体管理模块

负责系统字体的检测、加载和管理。
"""

import os
import platform
from typing import List, Dict, Optional, Tuple
from PIL import ImageFont
import glob


class FontManager:
    """字体管理器"""
    
    def __init__(self):
        self._font_cache: Dict[str, ImageFont.ImageFont] = {}
        self._system_fonts: Optional[List[Dict[str, str]]] = None
        
    def get_system_fonts(self) -> List[Dict[str, str]]:
        """获取系统字体列表"""
        if self._system_fonts is None:
            self._system_fonts = self._scan_system_fonts()
        return self._system_fonts
    
    def _scan_system_fonts(self) -> List[Dict[str, str]]:
        """扫描系统字体"""
        fonts = []
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            fonts.extend(self._scan_macos_fonts())
        elif system == "windows":  # Windows
            fonts.extend(self._scan_windows_fonts())
        else:  # Linux
            fonts.extend(self._scan_linux_fonts())
        
        # 去重并排序
        unique_fonts = {}
        for font in fonts:
            key = font['name'].lower()
            if key not in unique_fonts:
                unique_fonts[key] = font
        
        return sorted(unique_fonts.values(), key=lambda x: x['name'])
    
    def _scan_macos_fonts(self) -> List[Dict[str, str]]:
        """扫描macOS系统字体"""
        fonts = []
        font_dirs = [
            "/System/Library/Fonts/",
            "/Library/Fonts/",
            os.path.expanduser("~/Library/Fonts/")
        ]
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                fonts.extend(self._scan_font_directory(font_dir))
        
        # 添加常用中文字体（确保这些字体优先级高）
        chinese_fonts = [
            {"name": "苹方-简", "path": "/System/Library/Fonts/PingFang.ttc", "supports_chinese": True},
            {"name": "苹方-繁", "path": "/System/Library/Fonts/PingFang.ttc", "supports_chinese": True},
            {"name": "华文黑体", "path": "/System/Library/Fonts/STHeiti Light.ttc", "supports_chinese": True},
            {"name": "华文宋体", "path": "/System/Library/Fonts/Songti.ttc", "supports_chinese": True},
            {"name": "华文楷体", "path": "/System/Library/Fonts/Kaiti.ttc", "supports_chinese": True},
        ]
        
        # 插入到列表开头，确保优先级
        for font in reversed(chinese_fonts):
            if os.path.exists(font["path"]):
                fonts.insert(0, font)
        
        return fonts
    
    def _scan_windows_fonts(self) -> List[Dict[str, str]]:
        """扫描Windows系统字体"""
        fonts = []
        font_dirs = [
            "C:/Windows/Fonts/",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/")
        ]
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                fonts.extend(self._scan_font_directory(font_dir))
        
        # 添加常用中文字体
        chinese_fonts = [
            {"name": "微软雅黑", "path": "C:/Windows/Fonts/msyh.ttc", "supports_chinese": True},
            {"name": "宋体", "path": "C:/Windows/Fonts/simsun.ttc", "supports_chinese": True},
            {"name": "黑体", "path": "C:/Windows/Fonts/simhei.ttf", "supports_chinese": True},
            {"name": "楷体", "path": "C:/Windows/Fonts/simkai.ttf", "supports_chinese": True},
        ]
        
        for font in chinese_fonts:
            if os.path.exists(font["path"]):
                fonts.append(font)
        
        return fonts
    
    def _scan_linux_fonts(self) -> List[Dict[str, str]]:
        """扫描Linux系统字体"""
        fonts = []
        font_dirs = [
            "/usr/share/fonts/",
            "/usr/local/share/fonts/",
            os.path.expanduser("~/.fonts/"),
            os.path.expanduser("~/.local/share/fonts/")
        ]
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                fonts.extend(self._scan_font_directory(font_dir))
        
        return fonts
    
    def _scan_font_directory(self, directory: str) -> List[Dict[str, str]]:
        """扫描字体目录"""
        fonts = []
        font_extensions = ['*.ttf', '*.otf', '*.ttc', '*.otc']
        
        for ext in font_extensions:
            pattern = os.path.join(directory, '**', ext)
            for font_path in glob.glob(pattern, recursive=True):
                try:
                    font_name = self._get_font_name(font_path)
                    if font_name:
                        fonts.append({
                            'name': font_name,
                            'path': font_path,
                            'supports_chinese': self._supports_chinese(font_path)
                        })
                except Exception:
                    continue
        
        return fonts
    
    def _get_font_name(self, font_path: str) -> Optional[str]:
        """获取字体名称"""
        try:
            # 尝试从文件名推断字体名称
            font_name = os.path.splitext(os.path.basename(font_path))[0]
            
            # 清理文件名
            font_name = font_name.replace('-', ' ').replace('_', ' ')
            
            # 特殊处理一些常见字体
            name_mappings = {
                'arial': 'Arial',
                'helvetica': 'Helvetica',
                'times': 'Times New Roman',
                'courier': 'Courier New',
                'verdana': 'Verdana',
                'calibri': 'Calibri',
                'tahoma': 'Tahoma',
                'georgia': 'Georgia',
                'trebuchet': 'Trebuchet MS',
                'comic': 'Comic Sans MS',
                'impact': 'Impact',
                'palatino': 'Palatino',
                'garamond': 'Garamond',
                'bookman': 'Bookman',
                'avenir': 'Avenir',
                'futura': 'Futura',
                'optima': 'Optima',
                'pingfang': '苹方',
                'songti': '宋体',
                'kaiti': '楷体',
                'heiti': '黑体',
                'msyh': '微软雅黑',
                'simsun': '宋体',
                'simhei': '黑体',
                'simkai': '楷体'
            }
            
            font_name_lower = font_name.lower()
            for key, value in name_mappings.items():
                if key in font_name_lower:
                    return value
            
            return font_name.title()
            
        except Exception:
            return None
    
    def _supports_chinese(self, font_path: str) -> bool:
        """检查字体是否支持中文"""
        try:
            # 首先通过文件名和路径判断
            font_name = os.path.basename(font_path).lower()
            font_dir = os.path.dirname(font_path).lower()
            
            # 明确的中文字体指示符
            chinese_indicators = [
                'pingfang', 'songti', 'kaiti', 'heiti', 'stheiti',
                'msyh', 'simsun', 'simhei', 'simkai', 'yahei',
                'chinese', 'cjk', 'sc', 'tc', 'cn', 'tw', 'hk',
                'noto', 'source han', 'adobe', 'wqy'
            ]
            
            # 检查文件名
            for indicator in chinese_indicators:
                if indicator in font_name:
                    return True
            
            # 检查路径（某些中文字体在特定目录下）
            chinese_paths = ['chinese', 'cjk', 'han', 'asian']
            for path_indicator in chinese_paths:
                if path_indicator in font_dir:
                    return True
            
            # 对于常见的系统字体，进行更精确的判断
            # 明确不支持中文的字体
            non_chinese_fonts = [
                'arial', 'helvetica', 'times', 'courier', 'verdana',
                'calibri', 'tahoma', 'georgia', 'trebuchet', 'comic',
                'impact', 'palatino', 'garamond', 'bookman', 'avenir',
                'futura', 'optima', 'monaco', 'menlo', 'consolas'
            ]
            
            font_base = font_name.replace('.ttf', '').replace('.otf', '').replace('.ttc', '')
            for non_chinese in non_chinese_fonts:
                if non_chinese in font_base and len(font_base) < len(non_chinese) + 10:
                    # 如果文件名主要是这些英文字体名，且没有其他明显中文标识，则认为不支持中文
                    return False
            
            # 对于无法确定的字体，尝试实际测试（但要限制范围，避免性能问题）
            if 'supplemental' in font_dir or 'fonts' in font_dir:
                try:
                    font = ImageFont.truetype(font_path, 20)
                    # 测试一个常用中文字符
                    bbox = font.getbbox('中')
                    return bbox[2] > bbox[0]  # 如果有宽度，说明支持中文
                except Exception:
                    pass
            
            return False
            
        except Exception:
            return False
    
    def get_font(self, font_path: Optional[str], font_size: int, 
                 bold: bool = False, italic: bool = False) -> ImageFont.ImageFont:
        """获取字体对象（带缓存）"""
        cache_key = f"{font_path}_{font_size}_{bold}_{italic}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 使用默认字体
                font = self._get_default_font(font_size)
            
            self._font_cache[cache_key] = font
            return font
            
        except Exception:
            # 回退到系统默认字体
            default_font = ImageFont.load_default()
            self._font_cache[cache_key] = default_font
            return default_font
    
    def _get_default_font(self, font_size: int) -> ImageFont.ImageFont:
        """获取默认字体（优先选择支持中文的字体）"""
        system_fonts = self.get_system_fonts()
        
        # 优先选择支持中文的字体
        for font_info in system_fonts:
            if font_info.get('supports_chinese', False):
                try:
                    return ImageFont.truetype(font_info['path'], font_size)
                except Exception:
                    continue
        
        # 如果没有中文字体，选择第一个可用字体
        for font_info in system_fonts:
            try:
                return ImageFont.truetype(font_info['path'], font_size)
            except Exception:
                continue
        
        # 最后回退到PIL默认字体
        return ImageFont.load_default()
    
    def get_chinese_fonts(self) -> List[Dict[str, str]]:
        """获取支持中文的字体列表"""
        system_fonts = self.get_system_fonts()
        return [font for font in system_fonts if font.get('supports_chinese', False)]
    
    def get_recommended_fonts(self) -> List[Dict[str, str]]:
        """获取推荐字体列表"""
        system_fonts = self.get_system_fonts()
        
        # 推荐字体名称（优先级顺序）
        recommended_names = [
            # 中文字体
            '苹方', '微软雅黑', '宋体', '黑体', '楷体', '华文黑体', '华文宋体', '华文楷体',
            # 英文字体
            'Arial', 'Helvetica', 'Times New Roman', 'Calibri', 'Verdana', 
            'Tahoma', 'Georgia', 'Trebuchet MS', 'Avenir', 'Futura'
        ]
        
        recommended_fonts = []
        used_names = set()
        
        # 按推荐顺序添加字体
        for name in recommended_names:
            for font in system_fonts:
                if font['name'] == name and name not in used_names:
                    recommended_fonts.append(font)
                    used_names.add(name)
                    break
        
        # 添加其他支持中文的字体
        for font in system_fonts:
            if (font.get('supports_chinese', False) and 
                font['name'] not in used_names):
                recommended_fonts.append(font)
                used_names.add(font['name'])
        
        # 添加其他常用字体
        for font in system_fonts:
            if font['name'] not in used_names and len(recommended_fonts) < 20:
                recommended_fonts.append(font)
                used_names.add(font['name'])
        
        return recommended_fonts
    
    def clear_cache(self):
        """清空字体缓存"""
        self._font_cache.clear()


# 全局字体管理器实例
font_manager = FontManager()
