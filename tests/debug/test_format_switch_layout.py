#!/usr/bin/env python3
"""
测试格式切换时布局是否正确的脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import tkinter as tk
    from src.gui.main_window import MainWindow
    
    def test_format_switch_layout():
        """测试格式切换时的布局行为"""
        print("🚀 启动格式切换布局测试...")
        
        # 创建主窗口
        app = MainWindow()
        
        print("👀 GUI窗口已打开，请测试以下功能:")
        print("\n🎯 测试步骤:")
        print("1. 默认应该选择JPEG格式，质量滑块应该是启用状态")
        print("2. 切换到PNG格式，质量滑块应该变为灰色禁用状态")
        print("3. 切换回JPEG格式，质量滑块应该在原位置恢复启用状态")
        print("4. 多次切换，质量滑块应该始终保持在相同位置")
        
        print("\n✅ 修复效果:")
        print("• 质量滑块不再跳到最下面")
        print("• 布局位置始终保持一致")
        print("• 视觉状态清晰（启用/禁用）")
        
        print("\n⏰ 窗口将保持打开状态供您测试...")
        print("请在左侧设置面板中测试格式切换功能")
        print("关闭窗口或按Ctrl+C结束测试")
        
        try:
            app.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 测试结束")
        finally:
            try:
                app.root.destroy()
            except:
                pass
        
        print("✅ 格式切换布局测试完成")
        
    if __name__ == '__main__':
        print("格式切换布局测试")
        print("=" * 40)
        test_format_switch_layout()
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在图形界面环境中运行此测试")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
