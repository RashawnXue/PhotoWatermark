#!/usr/bin/env python3
"""
测试图片尺寸调整功能的脚本
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.config import Config
from src.core.image_processor import ImageProcessor
from src.gui.file_manager import FileManager
from PIL import Image

def test_resize_functionality():
    """测试图片尺寸调整功能"""
    print("测试图片尺寸调整功能...")
    
    # 检查测试文件
    test_file = "tests/fixtures/test_images/photo1.jpg"
    if not os.path.exists(test_file):
        print("测试文件不存在")
        return
        
    print(f"测试文件: {test_file}")
    
    # 获取原始图片尺寸
    with Image.open(test_file) as img:
        original_size = img.size
        print(f"原始尺寸: {original_size[0]}x{original_size[1]}")
    
    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"临时输出目录: {temp_dir}")
        
        # 创建配置和处理器
        config = Config()
        image_processor = ImageProcessor(config)
        file_manager = FileManager()
        
        # 测试不同的尺寸调整配置
        test_configs = [
            {
                'name': '按百分比缩放50%',
                'resize': {
                    'enabled': True,
                    'type': 'percentage',
                    'percentage': 50,
                    'keep_ratio': True
                },
                'expected_width': original_size[0] // 2,
                'expected_height': original_size[1] // 2
            },
            {
                'name': '按尺寸调整到800x600',
                'resize': {
                    'enabled': True,
                    'type': 'custom',
                    'width': 800,
                    'height': 600,
                    'keep_ratio': False
                },
                'expected_width': 800,
                'expected_height': 600
            },
            {
                'name': '按尺寸调整到1024x768',
                'resize': {
                    'enabled': True,
                    'type': 'custom',
                    'width': 1024,
                    'height': 768,
                    'keep_ratio': False
                },
                'expected_width': 1024,
                'expected_height': 768
            },
            {
                'name': '不调整尺寸',
                'resize': {
                    'enabled': False
                },
                'expected_width': original_size[0],
                'expected_height': original_size[1]
            }
        ]
        
        for i, test_config in enumerate(test_configs):
            print(f"\n{i+1}. {test_config['name']}")
            
            # 设置导出配置
            export_config = {
                'naming_rule': {'type': 'suffix', 'value': f'_test_{i+1}'},
                'output_format': 'JPEG',
                'quality': 95,
                'resize': test_config['resize']
            }
            
            # 处理图片
            success = file_manager._process_single_image(
                test_file, 
                temp_dir,
                export_config['naming_rule'],
                export_config['output_format'],
                export_config['quality'],
                export_config['resize'],
                image_processor
            )
            
            if success:
                # 检查输出文件
                output_filename = file_manager.generate_output_filename(
                    test_file, export_config['naming_rule'], export_config['output_format']
                )
                output_path = os.path.join(temp_dir, output_filename)
                
                if os.path.exists(output_path):
                    with Image.open(output_path) as output_img:
                        actual_size = output_img.size
                        print(f"   实际输出尺寸: {actual_size[0]}x{actual_size[1]}")
                        print(f"   期望输出尺寸: {test_config['expected_width']}x{test_config['expected_height']}")
                        
                        # 检查尺寸是否符合预期（允许1像素的误差）
                        width_ok = abs(actual_size[0] - test_config['expected_width']) <= 1
                        height_ok = abs(actual_size[1] - test_config['expected_height']) <= 1
                        
                        if width_ok and height_ok:
                            print("   结果: 通过")
                        else:
                            print("   结果: 失败 - 尺寸不符合预期")
                else:
                    print("   结果: 失败 - 输出文件不存在")
            else:
                print("   结果: 失败 - 处理失败")

def test_gui_resize_controls():
    """测试GUI尺寸调整控件"""
    print("\n\n测试GUI尺寸调整控件...")
    
    try:
        import tkinter as tk
        from src.gui.main_window import MainWindow
        
        print("GUI窗口已打开，请测试以下功能:")
        print("\n测试步骤:")
        print("1. 在左侧设置面板找到'图片尺寸'部分")
        print("2. 勾选'启用图片尺寸调整'复选框")
        print("3. 测试两种调整模式:")
        print("   - 按比例: 设置百分比（如50%）")
        print("   - 按尺寸: 设置宽度和高度像素值（如800x600px）")
        print("4. 取消勾选复选框，确认选项被禁用")
        print("5. 导入图片并测试导出功能")
        
        print("\n窗口将保持打开状态供您测试...")
        print("关闭窗口结束测试")
        
        app = MainWindow()
        app.root.mainloop()
        
        print("GUI测试完成")
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保在图形界面环境中运行此测试")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    print("图片尺寸调整功能测试")
    print("=" * 50)
    
    test_resize_functionality()
    
    # 询问是否要测试GUI
    try:
        response = input("\n是否要测试GUI控件? (y/n): ").lower().strip()
        if response == 'y' or response == 'yes':
            test_gui_resize_controls()
    except:
        pass
    
    print("\n测试完成")
