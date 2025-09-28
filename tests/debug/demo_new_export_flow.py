#!/usr/bin/env python3
"""
新导出流程演示脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import tkinter as tk
    from src.gui.main_window import MainWindow
    
    def demo_new_export_flow():
        """演示新的导出流程"""
        print("🚀 启动新导出流程演示...")
        print("\n新的导出流程特点:")
        print("1. ✅ 所有导出设置都在左侧面板中")
        print("2. ✅ 设置实时可见和可调整")
        print("3. ✅ 点击'导出图片'直接进入确认阶段")
        print("4. ✅ 无需多个对话框切换")
        
        # 创建主窗口
        app = MainWindow()
        
        print("\n👀 GUI窗口已打开，请观察:")
        print("📋 左侧面板包含完整的导出设置:")
        print("   • 输出目录 (可浏览选择)")
        print("   • 输出格式 (JPEG/PNG)")
        print("   • JPEG质量滑块 (仅JPEG格式显示)")
        print("   • 文件命名规则 (原名/前缀/后缀)")
        
        print("\n🎯 使用步骤:")
        print("1. 导入一些图片 (拖拽或点击导入按钮)")
        print("2. 在左侧面板调整导出设置")
        print("3. 点击工具栏的'导出图片'按钮")
        print("4. 在确认对话框中查看设置并确认")
        
        print("\n⏰ 窗口将保持打开状态供您测试...")
        print("关闭窗口或按Ctrl+C结束演示")
        
        try:
            app.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 演示结束")
        finally:
            try:
                app.root.destroy()
            except:
                pass
        
        print("✅ 新导出流程演示完成")
        
    if __name__ == '__main__':
        print("新导出流程演示")
        print("=" * 40)
        demo_new_export_flow()
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在图形界面环境中运行此演示")
except Exception as e:
    print(f"❌ 演示失败: {e}")
    import traceback
    traceback.print_exc()
