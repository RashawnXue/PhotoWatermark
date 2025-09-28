#!/usr/bin/env python3
"""
导出按钮功能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import tkinter as tk
    from src.gui.main_window import MainWindow
    
    def test_export_button():
        """测试导出按钮的启用/禁用逻辑"""
        print("🚀 启动导出按钮功能测试...")
        
        # 创建主窗口
        app = MainWindow()
        
        def find_export_button():
            """查找导出按钮"""
            for widget in app.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        try:
                            if hasattr(child, 'cget') and child.cget('text') == '导出图片':
                                return child
                        except:
                            continue
            return None
        
        export_button = find_export_button()
        
        if export_button:
            print("✅ 找到导出按钮")
            
            # 检查初始状态
            initial_state = export_button.cget('state')
            print(f"📋 初始状态: {initial_state}")
            
            # 模拟添加文件
            print("📁 模拟添加测试文件...")
            test_files = [
                "tests/fixtures/test_images/photo1.jpg",
                "tests/fixtures/test_images/photo2.jpg"
            ]
            
            # 检查测试文件是否存在
            existing_files = []
            for file_path in test_files:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
                    
            if existing_files:
                print(f"📷 找到 {len(existing_files)} 个测试图片文件")
                
                # 添加文件到缩略图列表
                app.thumbnail_list.add_files(existing_files)
                
                # 检查按钮状态是否更新
                updated_state = export_button.cget('state')
                print(f"📋 更新后状态: {updated_state}")
                
                if updated_state == 'normal':
                    print("✅ 导出按钮已正确启用")
                    
                    # 测试点击导出按钮
                    print("🖱️  测试点击导出按钮...")
                    try:
                        # 这里不实际执行，只是验证命令存在
                        command = export_button.cget('command')
                        if command:
                            print("✅ 导出按钮命令已绑定")
                        else:
                            print("❌ 导出按钮命令未绑定")
                    except Exception as e:
                        print(f"⚠️  无法获取按钮命令: {e}")
                        
                else:
                    print("❌ 导出按钮未能正确启用")
                    
            else:
                print("⚠️  没有找到测试图片文件，无法测试按钮启用")
                
        else:
            print("❌ 没有找到导出按钮")
            
        print("\n👀 显示窗口3秒钟...")
        app.root.after(3000, app.root.quit)
        app.root.mainloop()
        app.root.destroy()
        
        print("✅ 导出按钮功能测试完成")
        
    if __name__ == '__main__':
        print("导出按钮功能测试")
        print("=" * 30)
        test_export_button()
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在图形界面环境中运行此测试")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
