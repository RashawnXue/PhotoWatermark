#!/usr/bin/env python3
"""
导出确认对话框测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import tkinter as tk
    from src.gui.widgets.export_confirm import ExportConfirmDialog
    
    def test_export_confirm():
        """测试导出确认对话框"""
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 模拟文件列表
        test_files = [
            "/Users/test/photo1.jpg",
            "/Users/test/photo2.png", 
            "/Users/test/subfolder/photo3.jpg"
        ]
        
        # 模拟导出配置
        test_config = {
            'output_dir': '/Users/test/output',
            'naming_rule': {'type': 'suffix', 'value': '_watermarked'},
            'output_format': 'JPEG',
            'quality': 90,
            'resize': {
                'enabled': True,
                'type': 'width',
                'width': 1920,
                'height': 1080,
                'percentage': 100,
                'keep_ratio': True
            }
        }
        
        def on_confirm():
            print("✅ 用户确认导出")
            root.quit()
        
        # 创建并显示确认对话框
        confirm_dialog = ExportConfirmDialog(
            root,
            test_files,
            test_config,
            on_confirm=on_confirm
        )
        
        print("🚀 显示导出确认对话框...")
        result = confirm_dialog.show()
        
        if result is True:
            print("✅ 用户确认导出")
        elif result == 'modify':
            print("🔧 用户选择修改设置")
        else:
            print("❌ 用户取消导出")
            
        root.destroy()
        
    if __name__ == '__main__':
        print("导出确认对话框测试")
        print("=" * 30)
        test_export_confirm()
        print("测试完成")
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在图形界面环境中运行此测试")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
