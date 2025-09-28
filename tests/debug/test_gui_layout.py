#!/usr/bin/env python3
"""
GUI布局测试脚本 - 检查导出按钮是否显示
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import tkinter as tk
    from src.gui.main_window import MainWindow
    
    def test_gui_layout():
        """测试GUI布局和按钮显示"""
        print("🚀 启动GUI布局测试...")
        
        # 创建主窗口
        app = MainWindow()
        
        # 检查工具栏按钮
        print("\n📋 检查工具栏按钮...")
        
        def find_buttons(widget, buttons_found=None):
            if buttons_found is None:
                buttons_found = []
                
            for child in widget.winfo_children():
                if isinstance(child, tk.Button) or str(type(child)).endswith("Button'>"):
                    try:
                        text = child.cget('text')
                        state = child.cget('state')
                        buttons_found.append(f"按钮: '{text}' (状态: {state})")
                    except:
                        buttons_found.append(f"按钮: {type(child).__name__}")
                        
                # 递归查找子组件
                find_buttons(child, buttons_found)
                
            return buttons_found
        
        buttons = find_buttons(app.root)
        
        print(f"找到 {len(buttons)} 个按钮:")
        for i, button in enumerate(buttons, 1):
            print(f"  {i}. {button}")
            
        # 检查导出按钮是否存在
        export_buttons = [b for b in buttons if '导出' in b]
        if export_buttons:
            print(f"\n✅ 找到导出按钮: {export_buttons}")
        else:
            print("\n❌ 没有找到导出按钮")
            
        # 显示窗口5秒钟以便视觉检查
        print("\n👀 显示窗口5秒钟以便视觉检查...")
        print("请检查工具栏是否有'导出图片'按钮")
        
        def close_after_delay():
            app.root.after(5000, app.root.quit)
            
        close_after_delay()
        app.root.mainloop()
        app.root.destroy()
        
        print("✅ GUI布局测试完成")
        
    if __name__ == '__main__':
        print("GUI布局测试")
        print("=" * 30)
        test_gui_layout()
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在图形界面环境中运行此测试")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
