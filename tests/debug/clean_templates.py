#!/usr/bin/env python3
"""
清理现有模板

删除所有现有的模板文件，为新的模板系统做准备
"""

import sys
import os
import shutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.template_manager import TemplateManager


def clean_templates():
    """清理所有现有模板"""
    print("=== 清理现有模板 ===")
    
    try:
        tm = TemplateManager()
        
        print(f"模板存储目录: {tm.templates_dir}")
        print(f"配置目录: {tm.config_dir}")
        
        # 列出现有模板
        if os.path.exists(tm.templates_dir):
            templates = tm.list_templates()
            print(f"\n发现 {len(templates)} 个现有模板:")
            for template in templates:
                print(f"  - {template['name']}: {template.get('description', '')}")
                print(f"    文件: {template.get('path', '')}")
            
            if templates:
                # 删除所有模板
                for template in templates:
                    try:
                        tm.delete_template(template['name'])
                        print(f"✓ 删除模板 '{template['name']}' 成功")
                    except Exception as e:
                        print(f"❌ 删除模板 '{template['name']}' 失败: {e}")
                
                # 验证删除结果
                remaining_templates = tm.list_templates()
                if not remaining_templates:
                    print("\n✅ 所有模板已成功删除")
                else:
                    print(f"\n⚠️  仍有 {len(remaining_templates)} 个模板未删除:")
                    for template in remaining_templates:
                        print(f"  - {template['name']}")
            else:
                print("\n✓ 没有发现现有模板")
        else:
            print("\n✓ 模板目录不存在，无需清理")
        
        # 检查并清理上次会话文件
        last_session_path = tm._last_session_path()
        if os.path.exists(last_session_path):
            try:
                os.remove(last_session_path)
                print(f"✓ 删除上次会话文件: {last_session_path}")
            except Exception as e:
                print(f"❌ 删除上次会话文件失败: {e}")
        
        # 检查并清理默认模板设置
        default_template_path = tm._default_template_path()
        if os.path.exists(default_template_path):
            try:
                os.remove(default_template_path)
                print(f"✓ 删除默认模板设置: {default_template_path}")
            except Exception as e:
                print(f"❌ 删除默认模板设置失败: {e}")
        
        print("\n=== 清理完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 清理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def clean_template_directory():
    """直接清理模板目录（备用方法）"""
    print("\n=== 直接清理模板目录 ===")
    
    try:
        tm = TemplateManager()
        
        if os.path.exists(tm.templates_dir):
            # 列出目录中的所有文件
            files = os.listdir(tm.templates_dir)
            print(f"模板目录中的文件: {files}")
            
            # 删除所有 .json 文件
            for filename in files:
                if filename.endswith('.json'):
                    filepath = os.path.join(tm.templates_dir, filename)
                    try:
                        os.remove(filepath)
                        print(f"✓ 删除文件: {filename}")
                    except Exception as e:
                        print(f"❌ 删除文件 {filename} 失败: {e}")
            
            # 检查清理结果
            remaining_files = [f for f in os.listdir(tm.templates_dir) if f.endswith('.json')]
            if not remaining_files:
                print("✅ 模板目录清理完成")
            else:
                print(f"⚠️  仍有文件未删除: {remaining_files}")
        else:
            print("✓ 模板目录不存在")
            
        return True
        
    except Exception as e:
        print(f"❌ 直接清理失败: {e}")
        return False


def main():
    """主函数"""
    print("开始清理现有模板...")
    
    # 首先尝试使用模板管理器清理
    success = clean_templates()
    
    # 如果失败，尝试直接清理目录
    if not success:
        print("\n使用备用方法清理...")
        success = clean_template_directory()
    
    if success:
        print("\n" + "="*50)
        print("✅ 模板清理完成！")
        print("现在可以使用修复后的模板系统保存新模板。")
        print("="*50)
    else:
        print("\n❌ 模板清理失败")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
