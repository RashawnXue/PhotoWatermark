#!/usr/bin/env python3
"""
PhotoWatermark GUI应用启动入口

基于tkinter的图形界面版本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import MainWindow


def main():
    """主函数"""
    try:
        # 创建并运行主窗口
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\\n用户中断程序")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
