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
                    font_info = self._analyze_font_file(font_path)
                    if font_info:
                        fonts.append(font_info)
                except Exception:
                    continue
        
        return fonts
    
    def _analyze_font_file(self, font_path: str) -> Optional[Dict[str, str]]:
        """分析字体文件，提取字体信息"""
        try:
            font_name = self._get_font_name(font_path)
            if not font_name:
                return None
            
            # 分析字体样式
            font_style = self._detect_font_style(font_path)
            
            return {
                'name': font_name,
                'path': font_path,
                'supports_chinese': self._supports_chinese(font_path),
                'style': font_style['style'],
                'weight': font_style['weight'],
                'family': font_style['family']
            }
        except Exception:
            return None
    
    def _detect_font_style(self, font_path: str) -> Dict[str, str]:
        """检测字体样式信息"""
        file_name = os.path.basename(font_path).lower()
        
        # 检测粗体
        bold_indicators = ['bold', 'heavy', 'black', 'extra', 'ultra', 'demibold', 'semibold', '粗体']
        is_bold = any(indicator in file_name for indicator in bold_indicators)
        
        # 检测斜体
        italic_indicators = ['italic', 'oblique', 'slanted', '斜体']
        is_italic = any(indicator in file_name for indicator in italic_indicators)
        
        # 检测字重
        weight = 'normal'
        if 'thin' in file_name or 'ultralight' in file_name:
            weight = 'thin'
        elif 'light' in file_name:
            weight = 'light'
        elif 'medium' in file_name:
            weight = 'medium'
        elif 'semibold' in file_name or 'demibold' in file_name:
            weight = 'semibold'
        elif 'bold' in file_name:
            weight = 'bold'
        elif 'heavy' in file_name or 'black' in file_name:
            weight = 'heavy'
        
        # 确定样式
        if is_bold and is_italic:
            style = 'bold_italic'
        elif is_bold:
            style = 'bold'
        elif is_italic:
            style = 'italic'
        else:
            style = 'regular'
        
        # 提取字体家族名称
        family = self._extract_font_family(file_name)
        
        return {
            'style': style,
            'weight': weight,
            'family': family
        }
    
    def _extract_font_family(self, file_name: str) -> str:
        """提取字体家族名称"""
        # 移除文件扩展名
        name = file_name.replace('.ttf', '').replace('.otf', '').replace('.ttc', '').replace('.otc', '')
        
        # 移除样式关键词
        style_keywords = [
            'bold', 'italic', 'regular', 'normal', 'light', 'thin', 'medium', 'heavy', 'black',
            'oblique', 'slanted', 'semibold', 'demibold', 'ultra', 'extra',
            '粗体', '斜体', '细体', '中等', '黑体'
        ]
        
        for keyword in style_keywords:
            name = name.replace(keyword, '').replace('-', ' ').replace('_', ' ')
        
        # 清理多余的空格
        name = ' '.join(name.split())
        
        return name.title()
    
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
        """获取字体对象（带缓存），支持字体样式变体"""
        cache_key = f"{font_path}_{font_size}_{bold}_{italic}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        try:
            # 如果指定了字体路径，尝试查找对应样式的变体
            if font_path and os.path.exists(font_path):
                target_font_path = self._find_font_variant(font_path, bold, italic)
                font = ImageFont.truetype(target_font_path, font_size)
            else:
                # 使用默认字体
                font = self._get_default_font(font_size, bold, italic)
            
            self._font_cache[cache_key] = font
            return font
            
        except Exception:
            # 回退到系统默认字体
            try:
                default_font = self._get_default_font(font_size, bold, italic)
                self._font_cache[cache_key] = default_font
                return default_font
            except Exception:
                default_font = ImageFont.load_default()
                self._font_cache[cache_key] = default_font
                return default_font
    
    def _find_font_variant(self, base_font_path: str, bold: bool, italic: bool) -> str:
        """查找字体的样式变体"""
        # 如果不需要特殊样式，直接返回原字体
        if not bold and not italic:
            return base_font_path
        
        # 获取系统字体列表
        system_fonts = self.get_system_fonts()
        
        # 找到基础字体的信息
        base_font_info = None
        for font_info in system_fonts:
            if font_info['path'] == base_font_path:
                base_font_info = font_info
                break
        
        if not base_font_info:
            return base_font_path
        
        # 确定目标样式
        target_style = 'regular'
        if bold and italic:
            target_style = 'bold_italic'
        elif bold:
            target_style = 'bold'
        elif italic:
            target_style = 'italic'
        
        # 在同一字体家族中查找对应样式的变体
        base_family = base_font_info.get('family', base_font_info['name'])
        
        for font_info in system_fonts:
            if (font_info.get('family', font_info['name']) == base_family and 
                font_info.get('style') == target_style):
                return font_info['path']
        
        # 如果找不到精确匹配的样式，尝试模糊匹配
        return self._find_closest_font_variant(system_fonts, base_family, bold, italic)
    
    def _find_closest_font_variant(self, system_fonts: List[Dict[str, str]], 
                                   family: str, bold: bool, italic: bool) -> str:
        """查找最接近的字体变体"""
        candidates = []
        
        for font_info in system_fonts:
            if font_info.get('family', font_info['name']) == family:
                font_style = font_info.get('style', 'regular')
                font_weight = font_info.get('weight', 'normal')
                
                # 计算匹配度
                score = 0
                if bold and ('bold' in font_style or font_weight in ['bold', 'semibold', 'heavy']):
                    score += 2
                if italic and 'italic' in font_style:
                    score += 2
                
                candidates.append((font_info['path'], score))
        
        if candidates:
            # 选择匹配度最高的字体
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        # 如果还是找不到，返回家族中的第一个字体
        for font_info in system_fonts:
            if font_info.get('family', font_info['name']) == family:
                return font_info['path']
        
        # 最后的回退选项
        return system_fonts[0]['path'] if system_fonts else ""
    
    def _get_default_font(self, font_size: int, bold: bool = False, italic: bool = False) -> ImageFont.ImageFont:
        """获取默认字体（优先选择支持中文的字体），支持样式"""
        system_fonts = self.get_system_fonts()
        
        # 确定目标样式
        target_style = 'regular'
        if bold and italic:
            target_style = 'bold_italic'
        elif bold:
            target_style = 'bold'
        elif italic:
            target_style = 'italic'
        
        # 优先选择支持中文且样式匹配的字体
        for font_info in system_fonts:
            if (font_info.get('supports_chinese', False) and 
                font_info.get('style') == target_style):
                try:
                    return ImageFont.truetype(font_info['path'], font_size)
                except Exception:
                    continue
        
        # 如果找不到样式匹配的中文字体，选择任意中文字体
        for font_info in system_fonts:
            if font_info.get('supports_chinese', False):
                try:
                    return ImageFont.truetype(font_info['path'], font_size)
                except Exception:
                    continue
        
        # 如果没有中文字体，选择样式匹配的任意字体
        for font_info in system_fonts:
            if font_info.get('style') == target_style:
                try:
                    return ImageFont.truetype(font_info['path'], font_size)
                except Exception:
                    continue
        
        # 如果还是找不到，选择第一个可用字体
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
    
    def get_font_families(self) -> Dict[str, List[Dict[str, str]]]:
        """获取按字体家族分组的字体列表"""
        system_fonts = self.get_system_fonts()
        families = {}
        
        for font_info in system_fonts:
            family = font_info.get('family', font_info['name'])
            if family not in families:
                families[family] = []
            families[family].append(font_info)
        
        # 按样式排序每个家族的字体
        for family in families:
            families[family].sort(key=lambda x: self._get_style_priority(x.get('style', 'regular')))
        
        return families
    
    def _get_style_priority(self, style: str) -> int:
        """获取样式优先级（用于排序）"""
        priority_map = {
            'regular': 0,
            'italic': 1,
            'bold': 2,
            'bold_italic': 3
        }
        return priority_map.get(style, 999)
    
    def get_available_styles_for_font(self, font_path: str) -> List[str]:
        """获取指定字体可用的样式列表"""
        system_fonts = self.get_system_fonts()
        
        # 找到字体信息
        base_font_info = None
        for font_info in system_fonts:
            if font_info['path'] == font_path:
                base_font_info = font_info
                break
        
        if not base_font_info:
            return ['regular']
        
        # 查找同一家族的所有样式
        family = base_font_info.get('family', base_font_info['name'])
        available_styles = []
        
        for font_info in system_fonts:
            if font_info.get('family', font_info['name']) == family:
                style = font_info.get('style', 'regular')
                if style not in available_styles:
                    available_styles.append(style)
        
        return sorted(available_styles, key=self._get_style_priority)
    
    def clear_cache(self):
        """清空字体缓存"""
        self._font_cache.clear()


# 全局字体管理器实例
font_manager = FontManager()
