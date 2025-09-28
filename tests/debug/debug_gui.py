#!/usr/bin/env python3
"""
调试版本的GUI应用 - 专门用于测试拖拽功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tkinterdnd2 import TkinterDnD
    from src.gui.widgets.drag_drop import DragDropFrame
    import tkinter as tk
    from tkinter import ttk
    
    class DebugMainWindow:
        def __init__(self):
            self.root = TkinterDnD.Tk()
            self.root.title("PhotoWatermark 拖拽调试")
            self.root.geometry("600x500")
            
            # 创建界面
            self._create_widgets()
            
        def _create_widgets(self):
            # 标题
            title_label = tk.Label(
                self.root, 
                text="拖拽功能调试窗口", 
                font=('Arial', 16, 'bold')
            )
            title_label.pack(pady=10)
            
            # 拖拽区域
            self.drag_drop = DragDropFrame(self.root, self._on_files_dropped)
            self.drag_drop.pack(fill='both', expand=True, padx=20, pady=20)
            
            # 结果显示区域
            result_frame = ttk.LabelFrame(self.root, text="拖拽结果")
            result_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            # 文本框显示结果
            self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
            self.result_text.configure(yscrollcommand=scrollbar.set)
            
            self.result_text.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # 清空按钮
            clear_btn = ttk.Button(
                self.root, 
                text="清空结果", 
                command=self._clear_results
            )
            clear_btn.pack(pady=10)
            
            # 初始消息
            self._log("调试窗口已启动，请拖拽文件到上方区域测试")
            
        def _on_files_dropped(self, file_paths):
            """拖拽文件回调"""
            self._log(f"\\n=== 拖拽事件 ===")
            self._log(f"收到 {len(file_paths)} 个路径:")
            
            for i, path in enumerate(file_paths, 1):
                exists = os.path.exists(path)
                is_file = os.path.isfile(path) if exists else False
                is_dir = os.path.isdir(path) if exists else False
                
                self._log(f"{i}. {path}")
                self._log(f"   存在: {exists}, 文件: {is_file}, 目录: {is_dir}")
                
                if is_dir:
                    # 列出目录中的文件
                    try:
                        files = os.listdir(path)
                        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'))]
                        self._log(f"   目录包含 {len(image_files)} 个图片文件")
                    except Exception as e:
                        self._log(f"   读取目录失败: {e}")
            
            self._log("=== 拖拽事件结束 ===\\n")
            
        def _log(self, message):
            """记录消息到结果区域"""
            self.result_text.insert(tk.END, message + "\\n")
            self.result_text.see(tk.END)
            print(message)  # 同时输出到控制台
            
        def _clear_results(self):
            """清空结果"""
            self.result_text.delete(1.0, tk.END)
            
        def run(self):
            self.root.mainloop()
    
    if __name__ == "__main__":
        print("启动拖拽调试窗口...")
        app = DebugMainWindow()
        app.run()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保安装了tkinterdnd2: pip install tkinterdnd2")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
