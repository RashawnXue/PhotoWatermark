#!/usr/bin/env python3
"""
调试重复导出问题的测试脚本
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.config import Config
from src.core.image_processor import ImageProcessor
from src.gui.file_manager import FileManager

def test_single_tiff_export():
    """测试单个TIFF文件导出"""
    print("🔍 测试TIFF文件导出...")
    
    # 检查测试文件
    test_file = "tests/fixtures/test_images/photo1.tiff"
    if not os.path.exists(test_file):
        print("❌ 测试文件不存在")
        return
        
    print(f"📁 测试文件: {test_file}")
    
    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 临时输出目录: {temp_dir}")
        
        # 创建配置和处理器
        config = Config()
        image_processor = ImageProcessor(config)
        file_manager = FileManager()
        
        # 设置导出配置
        export_config = {
            'naming_rule': {'type': 'suffix', 'value': '_watermarked'},
            'output_format': 'JPEG',
            'quality': 95,
            'resize': {'enabled': False}
        }
        
        print("🔧 开始处理...")
        
        # 计算预期的输出文件名
        expected_filename = file_manager.generate_output_filename(
            test_file, export_config['naming_rule'], export_config['output_format']
        )
        expected_path = os.path.join(temp_dir, expected_filename)
        print(f"📝 预期输出文件: {expected_filename}")
        
        # 直接调用处理方法
        success = file_manager._process_single_image(
            test_file, 
            temp_dir,
            export_config['naming_rule'],
            export_config['output_format'],
            export_config['quality'],
            export_config['resize'],
            image_processor
        )
        
        print(f"✅ 处理结果: {'成功' if success else '失败'}")
        
        # 检查输出目录
        output_files = []
        for file in os.listdir(temp_dir):
            if file.endswith(('.jpg', '.jpeg', '.png')):
                output_files.append(file)
                file_path = os.path.join(temp_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"📄 输出文件: {file} ({file_size} bytes)")
        
        print(f"📊 总输出文件数: {len(output_files)}")
        
        if len(output_files) == 1:
            print("✅ 导出正常，只有一个文件")
        elif len(output_files) == 2:
            print("❌ 发现重复导出问题！")
            # 比较两个文件
            if len(output_files) == 2:
                file1_path = os.path.join(temp_dir, output_files[0])
                file2_path = os.path.join(temp_dir, output_files[1])
                size1 = os.path.getsize(file1_path)
                size2 = os.path.getsize(file2_path)
                print(f"🔍 文件1大小: {size1} bytes")
                print(f"🔍 文件2大小: {size2} bytes")
                
                if size1 == size2:
                    print("⚠️ 两个文件大小相同，可能是完全重复")
                else:
                    print("⚠️ 两个文件大小不同")
        else:
            print(f"⚠️ 异常情况，输出了 {len(output_files)} 个文件")

def test_watermark_processor_direct():
    """直接测试WatermarkProcessor"""
    print("\n🔍 直接测试WatermarkProcessor...")
    
    test_file = "tests/fixtures/test_images/photo1.tiff"
    if not os.path.exists(test_file):
        print("❌ 测试文件不存在")
        return
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Config()
        image_processor = ImageProcessor(config)
        
        output_path = os.path.join(temp_dir, "direct_test.jpg")
        
        print("🔧 直接调用ImageProcessor.process_single_image...")
        success, message = image_processor.process_single_image(
            test_file, output_path, "JPEG", 95, {'enabled': False}
        )
        
        print(f"✅ 处理结果: {'成功' if success else '失败'} - {message}")
        
        # 检查输出
        output_files = os.listdir(temp_dir)
        print(f"📊 输出文件数: {len(output_files)}")
        for file in output_files:
            print(f"📄 文件: {file}")

if __name__ == '__main__':
    print("TIFF重复导出问题调试")
    print("=" * 50)
    
    test_single_tiff_export()
    test_watermark_processor_direct()
    
    print("\n调试完成")
