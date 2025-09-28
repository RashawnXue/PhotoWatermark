#!/usr/bin/env python3
"""
PhotoWatermark 主程序入口

基于EXIF拍摄时间的图片水印工具
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == '__main__':
    main()
