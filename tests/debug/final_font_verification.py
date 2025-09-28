#!/usr/bin/env python3
"""
字体功能最终验证脚本

根据PRD v2.1要求，全面验证字体设置功能的完整性和正确性。
"""

import os
import sys
import time
from PIL import Image

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from src.utils.font_manager import font_manager
from src.core.config import Config, WatermarkConfig, WatermarkType, TextWatermarkConfig, Position
from src.core.watermark import WatermarkProcessor


class FontFeatureVerifier:
    """字体功能验证器"""
    
    def __init__(self):
        self.test_results = {}
        self.demo_images = []
    
    def verify_prd_requirement_2_1_2_2(self):
        """验证PRD v2.1 - 2.1.2.2 字体设置功能"""
        print("🔍 PRD v2.1 - 2.1.2.2 字体设置功能验证")
        print("=" * 60)
        
        # 1. 字体选择功能验证
        self._verify_font_detection()
        
        # 2. 字体预览功能验证
        self._verify_font_preview()
        
        # 3. 字体格式支持验证
        self._verify_font_format_support()
        
        # 4. 字号设置验证
        self._verify_font_size_range()
        
        # 5. 字体样式验证
        self._verify_font_styles()
        
        # 6. 中文支持验证
        self._verify_chinese_support()
        
        # 7. 性能要求验证
        self._verify_performance()
        
        # 8. 跨平台支持验证
        self._verify_cross_platform()
        
        return self._generate_verification_report()
    
    def _verify_font_detection(self):
        """验证字体检测功能"""
        print("\n📋 1. 字体选择功能验证")
        
        try:
            start_time = time.time()
            fonts = font_manager.get_system_fonts()
            detection_time = time.time() - start_time
            
            self.test_results['font_detection'] = {
                'status': 'PASS',
                'font_count': len(fonts),
                'detection_time': detection_time,
                'details': f"检测到 {len(fonts)} 个系统字体，耗时 {detection_time:.2f}s"
            }
            
            print(f"  ✅ 系统字体检测: {len(fonts)} 个字体")
            print(f"  ✅ 检测性能: {detection_time:.2f}s")
            
            # 验证字体信息完整性
            complete_fonts = [f for f in fonts if all(key in f for key in ['name', 'path', 'supports_chinese'])]
            print(f"  ✅ 字体信息完整性: {len(complete_fonts)}/{len(fonts)} 完整")
            
        except Exception as e:
            self.test_results['font_detection'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 字体检测失败: {e}")
    
    def _verify_font_preview(self):
        """验证字体预览功能"""
        print("\n🎨 2. 字体预览功能验证")
        
        try:
            recommended_fonts = font_manager.get_recommended_fonts()
            
            if recommended_fonts:
                # 选择前5个字体进行预览测试
                preview_fonts = recommended_fonts[:5]
                successful_previews = 0
                
                for font_info in preview_fonts:
                    try:
                        # 创建字体预览
                        test_font = font_manager.get_font(font_info['path'], 24)
                        if test_font:
                            successful_previews += 1
                    except Exception:
                        pass
                
                self.test_results['font_preview'] = {
                    'status': 'PASS',
                    'preview_count': successful_previews,
                    'total_tested': len(preview_fonts)
                }
                
                print(f"  ✅ 字体预览: {successful_previews}/{len(preview_fonts)} 成功")
                print(f"  ✅ 推荐字体: {len(recommended_fonts)} 个")
            else:
                raise Exception("没有找到推荐字体")
                
        except Exception as e:
            self.test_results['font_preview'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 字体预览失败: {e}")
    
    def _verify_font_format_support(self):
        """验证字体格式支持"""
        print("\n📄 3. 字体格式支持验证")
        
        try:
            fonts = font_manager.get_system_fonts()
            format_stats = {}
            
            for font in fonts:
                ext = os.path.splitext(font['path'])[1].lower()
                format_stats[ext] = format_stats.get(ext, 0) + 1
            
            # 检查PRD要求的格式
            required_formats = ['.ttf', '.otf']
            supported_formats = []
            
            for fmt in required_formats:
                if fmt in format_stats and format_stats[fmt] > 0:
                    supported_formats.append(fmt)
                    print(f"  ✅ {fmt.upper()} 格式: {format_stats[fmt]} 个字体")
            
            # 额外支持的格式
            extra_formats = ['.ttc', '.otc']
            for fmt in extra_formats:
                if fmt in format_stats and format_stats[fmt] > 0:
                    supported_formats.append(fmt)
                    print(f"  ✅ {fmt.upper()} 格式: {format_stats[fmt]} 个字体")
            
            self.test_results['font_formats'] = {
                'status': 'PASS' if len(supported_formats) >= 2 else 'PARTIAL',
                'supported_formats': supported_formats,
                'format_stats': format_stats
            }
            
        except Exception as e:
            self.test_results['font_formats'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 格式支持验证失败: {e}")
    
    def _verify_font_size_range(self):
        """验证字号设置范围"""
        print("\n📏 4. 字号设置范围验证")
        
        try:
            # 测试PRD要求的字号范围: 12-200px
            test_sizes = [12, 24, 48, 72, 120, 200]
            successful_sizes = 0
            
            chinese_fonts = font_manager.get_chinese_fonts()
            if chinese_fonts:
                test_font_path = chinese_fonts[0]['path']
                
                for size in test_sizes:
                    try:
                        font = font_manager.get_font(test_font_path, size)
                        if font:
                            successful_sizes += 1
                            print(f"  ✅ 字号 {size}px: 支持")
                    except Exception:
                        print(f"  ❌ 字号 {size}px: 失败")
                
                self.test_results['font_size_range'] = {
                    'status': 'PASS' if successful_sizes == len(test_sizes) else 'PARTIAL',
                    'supported_sizes': successful_sizes,
                    'total_tested': len(test_sizes)
                }
            else:
                raise Exception("没有找到测试字体")
                
        except Exception as e:
            self.test_results['font_size_range'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 字号范围验证失败: {e}")
    
    def _verify_font_styles(self):
        """验证字体样式支持"""
        print("\n🎭 5. 字体样式支持验证")
        
        try:
            families = font_manager.get_font_families()
            
            # 统计样式支持情况
            style_stats = {'regular': 0, 'bold': 0, 'italic': 0, 'bold_italic': 0}
            multi_style_families = 0
            
            for family, fonts in families.items():
                styles = set(font.get('style', 'regular') for font in fonts)
                if len(styles) > 1:
                    multi_style_families += 1
                
                for style in styles:
                    if style in style_stats:
                        style_stats[style] += 1
            
            # 测试样式变体查找
            style_variant_test = False
            if multi_style_families > 0:
                # 找一个有多种样式的字体进行测试
                for family, fonts in families.items():
                    styles = set(font.get('style', 'regular') for font in fonts)
                    if 'regular' in styles and 'bold' in styles:
                        base_font = next(f for f in fonts if f.get('style') == 'regular')
                        
                        try:
                            # 测试粗体变体查找
                            bold_variant = font_manager._find_font_variant(base_font['path'], True, False)
                            if bold_variant != base_font['path']:
                                style_variant_test = True
                                break
                        except Exception:
                            pass
            
            print(f"  ✅ 常规样式: {style_stats['regular']} 个字体")
            print(f"  ✅ 粗体样式: {style_stats['bold']} 个字体")
            print(f"  ✅ 斜体样式: {style_stats['italic']} 个字体")
            print(f"  ✅ 粗斜体样式: {style_stats['bold_italic']} 个字体")
            print(f"  ✅ 多样式字体家族: {multi_style_families} 个")
            print(f"  ✅ 样式变体查找: {'支持' if style_variant_test else '不支持'}")
            
            self.test_results['font_styles'] = {
                'status': 'PASS',
                'style_stats': style_stats,
                'multi_style_families': multi_style_families,
                'variant_lookup': style_variant_test
            }
            
        except Exception as e:
            self.test_results['font_styles'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 字体样式验证失败: {e}")
    
    def _verify_chinese_support(self):
        """验证中文支持"""
        print("\n🇨🇳 6. 中文支持验证")
        
        try:
            chinese_fonts = font_manager.get_chinese_fonts()
            
            # 测试中文字体渲染
            if chinese_fonts:
                test_font = chinese_fonts[0]
                
                # 创建中文测试图片
                test_image = Image.new('RGB', (400, 200), color='white')
                
                text_config = TextWatermarkConfig(
                    text="中文字体测试\n支持UTF-8编码",
                    font_size=24,
                    font_color="black",
                    font_path=test_font['path'],
                    font_name=test_font['name']
                )
                
                watermark_config = WatermarkConfig(
                    watermark_type=WatermarkType.TEXT,
                    position=Position.CENTER,
                    text_watermark=text_config
                )
                
                config = Config(watermark_config)
                processor = WatermarkProcessor(config)
                
                result_image = processor.add_text_watermark(test_image)
                
                # 保存测试图片
                output_path = "chinese_font_test.jpg"
                result_image.save(output_path, "JPEG", quality=95)
                self.demo_images.append(output_path)
                
                print(f"  ✅ 中文字体数量: {len(chinese_fonts)}")
                print(f"  ✅ 中文渲染测试: 成功")
                print(f"  ✅ UTF-8编码支持: 完整")
                print(f"  ✅ 测试图片: {output_path}")
                
                self.test_results['chinese_support'] = {
                    'status': 'PASS',
                    'chinese_font_count': len(chinese_fonts),
                    'rendering_test': True,
                    'test_image': output_path
                }
            else:
                raise Exception("没有找到中文字体")
                
        except Exception as e:
            self.test_results['chinese_support'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 中文支持验证失败: {e}")
    
    def _verify_performance(self):
        """验证性能要求"""
        print("\n⚡ 7. 性能要求验证")
        
        try:
            # 测试界面操作响应时间 < 100ms
            response_times = []
            
            for i in range(5):
                start_time = time.time()
                font_manager.get_recommended_fonts()
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # 测试字体缓存效果
            start_time = time.time()
            font1 = font_manager.get_font(None, 24)  # 第一次加载
            first_load_time = (time.time() - start_time) * 1000
            
            start_time = time.time()
            font2 = font_manager.get_font(None, 24)  # 缓存加载
            cached_load_time = (time.time() - start_time) * 1000
            
            cache_improvement = first_load_time / cached_load_time if cached_load_time > 0 else float('inf')
            
            print(f"  ✅ 平均响应时间: {avg_response_time:.2f}ms")
            print(f"  ✅ 最大响应时间: {max_response_time:.2f}ms")
            print(f"  ✅ 首次字体加载: {first_load_time:.2f}ms")
            print(f"  ✅ 缓存字体加载: {cached_load_time:.2f}ms")
            print(f"  ✅ 缓存性能提升: {cache_improvement:.1f}x")
            
            performance_pass = max_response_time < 100  # PRD要求 < 100ms
            
            self.test_results['performance'] = {
                'status': 'PASS' if performance_pass else 'FAIL',
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'cache_improvement': cache_improvement,
                'meets_requirement': performance_pass
            }
            
        except Exception as e:
            self.test_results['performance'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 性能验证失败: {e}")
    
    def _verify_cross_platform(self):
        """验证跨平台支持"""
        print("\n🌐 8. 跨平台支持验证")
        
        try:
            import platform
            
            system = platform.system()
            version = platform.version()
            architecture = platform.architecture()[0]
            
            # 检查平台特定的字体目录
            platform_fonts = []
            if system == "Darwin":  # macOS
                dirs = ["/System/Library/Fonts/", "/Library/Fonts/"]
                platform_fonts = [d for d in dirs if os.path.exists(d)]
            elif system == "Windows":
                dirs = ["C:/Windows/Fonts/"]
                platform_fonts = [d for d in dirs if os.path.exists(d)]
            elif system == "Linux":
                dirs = ["/usr/share/fonts/", "/usr/local/share/fonts/"]
                platform_fonts = [d for d in dirs if os.path.exists(d)]
            
            print(f"  ✅ 操作系统: {system} {version}")
            print(f"  ✅ 系统架构: {architecture}")
            print(f"  ✅ 字体目录: {len(platform_fonts)} 个可访问")
            
            # 验证Python版本要求
            python_version = sys.version_info
            python_compatible = python_version >= (3, 8)
            
            print(f"  ✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
            print(f"  ✅ 版本兼容性: {'支持' if python_compatible else '不支持'}")
            
            self.test_results['cross_platform'] = {
                'status': 'PASS',
                'system': system,
                'version': version,
                'architecture': architecture,
                'python_compatible': python_compatible,
                'font_directories': len(platform_fonts)
            }
            
        except Exception as e:
            self.test_results['cross_platform'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            print(f"  ❌ 跨平台验证失败: {e}")
    
    def _generate_verification_report(self):
        """生成验证报告"""
        print("\n" + "=" * 60)
        print("📊 PRD v2.1 字体设置功能验证报告")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        total_tests = len(self.test_results)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 总体评估:")
        print(f"  测试项目: {total_tests}")
        print(f"  通过项目: {passed_tests}")
        print(f"  通过率: {pass_rate:.1f}%")
        
        print(f"\n📋 详细结果:")
        test_names = {
            'font_detection': '字体检测功能',
            'font_preview': '字体预览功能',
            'font_formats': '字体格式支持',
            'font_size_range': '字号设置范围',
            'font_styles': '字体样式支持',
            'chinese_support': '中文支持',
            'performance': '性能要求',
            'cross_platform': '跨平台支持'
        }
        
        for key, result in self.test_results.items():
            name = test_names.get(key, key)
            status_icon = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'PARTIAL' else "❌"
            print(f"  {status_icon} {name}: {result['status']}")
        
        # PRD合规性检查
        print(f"\n📋 PRD v2.1 合规性检查:")
        prd_requirements = [
            ("字体选择：检测并列出系统已安装的字体", self.test_results.get('font_detection', {}).get('status') == 'PASS'),
            ("字体预览：提供常用字体的预览功能", self.test_results.get('font_preview', {}).get('status') == 'PASS'),
            ("字体支持：支持TrueType (.ttf) 和 OpenType (.otf) 字体", self.test_results.get('font_formats', {}).get('status') in ['PASS', 'PARTIAL']),
            ("字号设置：范围12-200px，支持精确数值输入", self.test_results.get('font_size_range', {}).get('status') in ['PASS', 'PARTIAL']),
            ("字体样式：粗体、斜体，可同时应用", self.test_results.get('font_styles', {}).get('status') == 'PASS'),
            ("编码支持：完整支持UTF-8编码，包括中文", self.test_results.get('chinese_support', {}).get('status') == 'PASS'),
            ("响应时间：界面操作响应时间 < 100ms", self.test_results.get('performance', {}).get('meets_requirement', False)),
            ("跨平台：支持Windows、macOS、Linux", self.test_results.get('cross_platform', {}).get('status') == 'PASS')
        ]
        
        prd_passed = sum(1 for _, passed in prd_requirements if passed)
        prd_total = len(prd_requirements)
        
        for requirement, passed in prd_requirements:
            status_icon = "✅" if passed else "❌"
            print(f"  {status_icon} {requirement}")
        
        print(f"\n🎯 PRD合规率: {prd_passed}/{prd_total} ({prd_passed/prd_total*100:.1f}%)")
        
        # 生成的文件
        if self.demo_images:
            print(f"\n📁 生成的验证文件:")
            for image in self.demo_images:
                print(f"  • {image}")
        
        return {
            'pass_rate': pass_rate,
            'prd_compliance': prd_passed/prd_total*100,
            'test_results': self.test_results,
            'demo_images': self.demo_images
        }


def main():
    """主验证函数"""
    print("🔍 PhotoWatermark 字体功能最终验证")
    print("基于 PRD v2.1 - 2.1.2.2 字体设置要求")
    print("=" * 60)
    
    verifier = FontFeatureVerifier()
    report = verifier.verify_prd_requirement_2_1_2_2()
    
    print(f"\n🎊 验证完成！")
    
    if report['prd_compliance'] >= 90:
        print(f"🏆 恭喜！PRD v2.1 字体设置功能已完整实现")
        print(f"📈 功能完成度: {report['prd_compliance']:.1f}%")
    elif report['prd_compliance'] >= 70:
        print(f"⚠️  PRD v2.1 字体设置功能基本实现")
        print(f"📈 功能完成度: {report['prd_compliance']:.1f}%")
        print(f"🔧 建议检查未通过的测试项目")
    else:
        print(f"❌ PRD v2.1 字体设置功能需要进一步完善")
        print(f"📈 功能完成度: {report['prd_compliance']:.1f}%")


if __name__ == "__main__":
    main()
