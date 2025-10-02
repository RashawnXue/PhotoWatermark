#!/usr/bin/env python3
"""
测试多个模板保存功能

验证可以保存多个不同名称的模板，并且它们不会相互覆盖
"""

import sys
import os
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.template_manager import TemplateManager
from src.core.config import WatermarkConfig, WatermarkType, Position


def test_multiple_different_templates():
    """测试保存多个不同的模板"""
    print("=== 测试保存多个不同的模板 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tm = TemplateManager(temp_dir)
        
        # 创建多个不同的模板配置
        templates = [
            {
                'name': '水印模板1',
                'desc': '第一个水印模板',
                'text': '版权所有 © 2024',
                'position': Position.BOTTOM_RIGHT
            },
            {
                'name': '水印模板2', 
                'desc': '第二个水印模板',
                'text': 'Confidential Document',
                'position': Position.TOP_LEFT
            },
            {
                'name': 'English Template',
                'desc': 'English watermark template',
                'text': 'Sample Watermark',
                'position': Position.CENTER
            },
            {
                'name': '特殊字符模板@#$',
                'desc': '包含特殊字符的模板名称',
                'text': '特殊水印',
                'position': Position.BOTTOM_LEFT
            },
            {
                'name': '长模板名称测试这是一个很长的模板名称用来测试系统处理',
                'desc': '测试长名称处理',
                'text': '长名称测试',
                'position': Position.TOP_RIGHT
            }
        ]
        
        # 保存所有模板
        for template_info in templates:
            config = WatermarkConfig()
            config.watermark_type = WatermarkType.TEXT
            config.text_watermark.text = template_info['text']
            config.position = template_info['position']
            
            tm.save_template(template_info['name'], config, template_info['desc'])
            print(f"✓ 保存模板 '{template_info['name']}' 成功")
        
        # 验证所有模板都被保存
        saved_templates = tm.list_templates()
        print(f"\n保存的模板总数: {len(saved_templates)}")
        print(f"期望的模板总数: {len(templates)}")
        
        if len(saved_templates) != len(templates):
            print("❌ 模板数量不匹配！")
            return False
        
        # 验证每个模板的内容
        for template_info in templates:
            try:
                loaded_config = tm.load_template(template_info['name'])
                
                # 验证配置内容
                assert loaded_config.watermark_type == WatermarkType.TEXT
                assert loaded_config.text_watermark.text == template_info['text']
                assert loaded_config.position == template_info['position']
                
                print(f"✓ 验证模板 '{template_info['name']}' 内容正确")
                
            except Exception as e:
                print(f"❌ 验证模板 '{template_info['name']}' 失败: {e}")
                return False
        
        # 验证模板元数据
        for saved_template in saved_templates:
            original_template = next(t for t in templates if t['name'] == saved_template['name'])
            assert saved_template['description'] == original_template['desc']
            assert 'created_at' in saved_template
            assert 'modified_at' in saved_template
            print(f"✓ 验证模板 '{saved_template['name']}' 元数据正确")
        
        print("\n✅ 所有模板都正确保存和验证")
        return True


def test_template_independence():
    """测试模板之间的独立性"""
    print("\n=== 测试模板之间的独立性 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tm = TemplateManager(temp_dir)
        
        # 创建第一个模板
        config1 = WatermarkConfig()
        config1.watermark_type = WatermarkType.TEXT
        config1.text_watermark.text = "原始文本"
        config1.position = Position.BOTTOM_RIGHT
        
        tm.save_template("模板A", config1, "第一个模板")
        print("✓ 保存模板A")
        
        # 创建第二个模板
        config2 = WatermarkConfig()
        config2.watermark_type = WatermarkType.TEXT
        config2.text_watermark.text = "不同的文本"
        config2.position = Position.TOP_LEFT
        
        tm.save_template("模板B", config2, "第二个模板")
        print("✓ 保存模板B")
        
        # 验证两个模板都存在且内容不同
        loaded_a = tm.load_template("模板A")
        loaded_b = tm.load_template("模板B")
        
        assert loaded_a.text_watermark.text == "原始文本"
        assert loaded_a.position == Position.BOTTOM_RIGHT
        
        assert loaded_b.text_watermark.text == "不同的文本"
        assert loaded_b.position == Position.TOP_LEFT
        
        print("✓ 两个模板内容独立且正确")
        
        # 修改第一个模板
        config1_updated = WatermarkConfig()
        config1_updated.watermark_type = WatermarkType.TEXT
        config1_updated.text_watermark.text = "更新后的文本"
        config1_updated.position = Position.CENTER
        
        tm.save_template("模板A", config1_updated, "更新的第一个模板")
        print("✓ 更新模板A")
        
        # 验证只有模板A被更新，模板B保持不变
        loaded_a_updated = tm.load_template("模板A")
        loaded_b_unchanged = tm.load_template("模板B")
        
        assert loaded_a_updated.text_watermark.text == "更新后的文本"
        assert loaded_a_updated.position == Position.CENTER
        
        assert loaded_b_unchanged.text_watermark.text == "不同的文本"
        assert loaded_b_unchanged.position == Position.TOP_LEFT
        
        print("✓ 模板A更新成功，模板B保持不变")
        
        return True


def main():
    """运行所有测试"""
    print("开始测试多个模板保存功能...")
    
    success = True
    success &= test_multiple_different_templates()
    success &= test_template_independence()
    
    if success:
        print("\n" + "="*60)
        print("✅ 多模板保存功能测试全部通过！")
        print("现在可以正确保存多个不同名称的模板，不会相互覆盖。")
        print("="*60)
    else:
        print("\n❌ 多模板保存功能测试失败")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
