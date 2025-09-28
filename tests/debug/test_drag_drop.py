#!/usr/bin/env python3
"""
测试拖拽功能的简单脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tkinterdnd2 import TkinterDnD
    from src.gui.widgets.drag_drop import DragDropFrame
    
    def on_files_dropped(files):
        print(f"✅ 拖拽成功！收到文件: {files}")
        for file in files:
            if os.path.exists(file):
                print(f"  - {file} (存在)")
            else:
                print(f"  - {file} (不存在)")
    
    # 创建测试窗口
    root = TkinterDnD.Tk()
    root.title('拖拽功能测试')
    root.geometry('500x400')
    
    # 创建拖拽组件
    drag_frame = DragDropFrame(root, on_files_dropped)
    drag_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    print("🚀 拖拽测试窗口已启动")
    print("请拖拽一些图片文件到窗口中测试功能")
    print("按Ctrl+C或关闭窗口退出")
    
    root.mainloop()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装 tkinterdnd2: pip install tkinterdnd2")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
