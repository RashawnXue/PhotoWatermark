#!/usr/bin/env python3
"""
测试模板命名问题

检查模板名称清理逻辑是否导致不同名称映射到相同文件名
"""

import sys
import os
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.template_manager import TemplateManager
from src.core.config import WatermarkConfig, WatermarkType


def test_name_sanitization():
    """测试名称清理逻辑"""
    print("=== 测试模板名称清理逻辑 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tm = TemplateManager(temp_dir)
        
        # 测试各种名称
        test_names = [
            "模板1",
            "模板2", 
            "Template A",
            "Template B",
            "测试@模板",
            "测试#模板",
            "My Template (v1)",
            "My Template (v2)",
            "特殊字符!@#$%^&*()",
            "另一个特殊字符!@#$%^&*()"
        ]
        
        sanitized_names = []
        file_paths = []
        
        for name in test_names:
            sanitized = tm._sanitize_name(name)
            filepath = tm._template_filepath(name)
            sanitized_names.append(sanitized)
            file_paths.append(filepath)
            print(f"'{name}' -> '{sanitized}' -> '{os.path.basename(filepath)}'")
        
        # 检查是否有重复的文件路径
        unique_paths = set(file_paths)
        if len(unique_paths) != len(file_paths):
            print("\n❌ 发现文件路径冲突！")
            for i, path1 in enumerate(file_paths):
                for j, path2 in enumerate(file_paths[i+1:], i+1):
                    if path1 == path2:
                        print(f"冲突: '{test_names[i]}' 和 '{test_names[j]}' 都映射到 '{path1}'")
            return False
        else:
            print("\n✓ 没有文件路径冲突")
            return True


def test_actual_template_saving():
    """测试实际保存多个模板"""
    print("\n=== 测试实际保存多个模板 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tm = TemplateManager(temp_dir)
        
        # 创建不同的模板
        templates_to_save = [
            ("文本模板1", "这是第一个文本模板"),
            ("文本模板2", "这是第二个文本模板"),
            ("英文模板A", "English template A"),
            ("英文模板B", "English template B"),
            ("特殊模板@", "特殊字符模板"),
        ]
        
        # 保存所有模板
        for i, (name, desc) in enumerate(templates_to_save):
            config = WatermarkConfig()
            config.watermark_type = WatermarkType.TEXT
            config.text_watermark.text = f"Template {i+1}: {name}"
            
            try:
                tm.save_template(name, config, desc)
                print(f"✓ 保存模板 '{name}' 成功")
            except Exception as e:
                print(f"❌ 保存模板 '{name}' 失败: {e}")
                return False
        
        # 检查保存的模板数量
        templates = tm.list_templates()
        print(f"\n保存的模板数量: {len(templates)}")
        print(f"期望的模板数量: {len(templates_to_save)}")
        
        if len(templates) != len(templates_to_save):
            print("❌ 模板数量不匹配！")
            print("实际保存的模板:")
            for template in templates:
                print(f"  - {template['name']}: {template['description']}")
            return False
        
        # 验证每个模板都能正确加载
        for name, desc in templates_to_save:
            try:
                loaded_config = tm.load_template(name)
                print(f"✓ 加载模板 '{name}' 成功")
            except Exception as e:
                print(f"❌ 加载模板 '{name}' 失败: {e}")
                return False
        
        print("✓ 所有模板都能正确保存和加载")
        return True


def main():
    """运行测试"""
    print("开始测试模板命名问题...")
    
    success = True
    success &= test_name_sanitization()
    success &= test_actual_template_saving()
    
    if success:
        print("\n✅ 模板命名测试通过")
    else:
        print("\n❌ 模板命名测试失败")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
