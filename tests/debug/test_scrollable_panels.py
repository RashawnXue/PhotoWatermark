#!/usr/bin/env python3
"""
测试可滚动面板功能的脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import tkinter as tk
    from src.gui.main_window import MainWindow
    
    def test_scrollable_panels():
        """测试可滚动面板功能"""
        print("启动可滚动面板测试...")
        
        # 创建主窗口
        app = MainWindow()
        
        print("GUI窗口已打开，请测试以下功能:")
        print("\n测试步骤:")
        print("1. 左侧设置面板滚动测试:")
        print("   - 将鼠标放在左侧设置面板上")
        print("   - 使用鼠标滚轮上下滚动")
        print("   - 确认可以看到所有设置选项（导入、水印、导出、图片尺寸等）")
        print("   - 右侧应该有滚动条显示")
        
        print("\n2. 导出确认对话框滚动测试:")
        print("   - 导入一些图片")
        print("   - 点击'导出图片'按钮")
        print("   - 在导出确认对话框中使用鼠标滚轮滚动")
        print("   - 确认可以看到所有内容（文件列表、设置预览、按钮等）")
        print("   - 右侧应该有滚动条显示")
        
        print("\n3. 窗口大小测试:")
        print("   - 尝试缩小窗口高度")
        print("   - 确认滚动功能在小窗口中也正常工作")
        print("   - 所有内容都应该可以通过滚动访问")
        
        print("\n滚动功能特点:")
        print("- 支持鼠标滚轮滚动")
        print("- 右侧显示滚动条")
        print("- 跨平台兼容（Windows/Linux/macOS）")
        print("- 内容区域自动调整大小")
        
        print("\n窗口将保持打开状态供您测试...")
        print("关闭窗口结束测试")
        
        try:
            app.root.mainloop()
        except KeyboardInterrupt:
            print("\n测试结束")
        finally:
            try:
                app.root.destroy()
            except:
                pass
        
        print("可滚动面板测试完成")
        
    if __name__ == '__main__':
        print("可滚动面板功能测试")
        print("=" * 40)
        test_scrollable_panels()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在图形界面环境中运行此测试")
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
