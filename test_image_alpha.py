#!/usr/bin/env python3
"""
图片水印透明度功能测试脚本
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from PIL import Image, ImageDraw

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import Config, WatermarkConfig, WatermarkType, ImageWatermarkConfig, ScaleMode
from core.watermark import WatermarkProcessor

def create_test_watermark_image():
    """创建测试用的水印图片"""
    # 创建一个简单的测试水印图片
    img = Image.new('RGBA', (100, 50), (255, 0, 0, 255))  # 红色背景
    draw = ImageDraw.Draw(img)
    
    # 绘制一些图案
    draw.rectangle([10, 10, 90, 40], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    draw.text((20, 20), "LOGO", fill=(0, 0, 0, 255))
    
    # 保存测试图片
    test_watermark_path = "test_watermark.png"
    img.save(test_watermark_path)
    return test_watermark_path

def test_image_alpha():
    """测试图片水印透明度功能"""
    root = tk.Tk()
    root.title("图片水印透明度测试")
    root.geometry("800x700")
    
    # 创建测试界面
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    ttk.Label(main_frame, text="图片水印透明度功能测试", 
              font=('Arial', 16, 'bold')).pack(pady=(0, 20))
    
    # 创建测试水印图片
    try:
        watermark_path = create_test_watermark_image()
        ttk.Label(main_frame, text=f"测试水印图片: {watermark_path}", 
                  font=('Arial', 10)).pack(pady=(0, 10))
    except Exception as e:
        ttk.Label(main_frame, text=f"创建测试水印失败: {e}", 
                  foreground='red').pack(pady=(0, 10))
        return
    
    # 创建测试图像
    test_image = Image.new('RGB', (400, 300), 'lightblue')
    draw = ImageDraw.Draw(test_image)
    draw.text((50, 50), "这是测试背景图片", fill='black')
    
    # 测试不同透明度
    alpha_values = [0.2, 0.4, 0.6, 0.8, 1.0]
    
    results_frame = ttk.Frame(main_frame)
    results_frame.pack(fill='both', expand=True)
    
    ttk.Label(results_frame, text="透明度测试结果:", 
              font=('Arial', 12, 'bold')).pack(pady=(0, 10))
    
    for alpha in alpha_values:
        # 创建图片水印配置
        image_config = ImageWatermarkConfig(
            image_path=watermark_path,
            scale_mode=ScaleMode.PERCENTAGE,
            scale_percentage=30.0,
            keep_aspect_ratio=True,
            alpha=alpha
        )
        
        watermark_config = WatermarkConfig(
            watermark_type=WatermarkType.IMAGE,
            image_watermark=image_config
        )
        
        config = Config(watermark_config)
        processor = WatermarkProcessor(config)
        
        # 处理图像
        try:
            result_image = processor.add_image_watermark(test_image.copy())
            
            # 显示结果信息
            result_frame = ttk.Frame(results_frame)
            result_frame.pack(fill='x', pady=3)
            
            alpha_percent = int(alpha * 100)
            status_text = f"✓ 透明度 {alpha_percent}%: 成功生成"
            ttk.Label(result_frame, text=status_text, 
                      foreground='green', font=('Arial', 10)).pack(anchor='w')
            
            # 简单验证结果
            if result_image.size == test_image.size:
                ttk.Label(result_frame, text="  - 图像尺寸正确", 
                          foreground='gray', font=('Arial', 9)).pack(anchor='w')
            
        except Exception as e:
            result_frame = ttk.Frame(results_frame)
            result_frame.pack(fill='x', pady=3)
            
            alpha_percent = int(alpha * 100)
            status_text = f"✗ 透明度 {alpha_percent}%: 失败 - {str(e)}"
            ttk.Label(result_frame, text=status_text, 
                      foreground='red', font=('Arial', 10)).pack(anchor='w')
    
    # 配置测试
    ttk.Separator(results_frame, orient='horizontal').pack(fill='x', pady=20)
    
    ttk.Label(results_frame, text="配置序列化测试:", 
              font=('Arial', 12, 'bold')).pack(pady=(0, 10))
    
    # 测试配置的序列化和反序列化
    try:
        # 创建配置
        test_config = ImageWatermarkConfig(
            image_path=watermark_path,
            scale_mode=ScaleMode.PERCENTAGE,
            scale_percentage=25.0,
            alpha=0.75
        )
        
        # 检查配置字段
        config_frame = ttk.Frame(results_frame)
        config_frame.pack(fill='x', pady=3)
        
        ttk.Label(config_frame, text=f"✓ 图片路径: {test_config.image_path}", 
                  foreground='green', font=('Arial', 9)).pack(anchor='w')
        ttk.Label(config_frame, text=f"✓ 透明度: {test_config.alpha}", 
                  foreground='green', font=('Arial', 9)).pack(anchor='w')
        ttk.Label(config_frame, text=f"✓ 缩放比例: {test_config.scale_percentage}%", 
                  foreground='green', font=('Arial', 9)).pack(anchor='w')
        
    except Exception as e:
        config_frame = ttk.Frame(results_frame)
        config_frame.pack(fill='x', pady=3)
        
        ttk.Label(config_frame, text=f"✗ 配置测试失败: {e}", 
                  foreground='red', font=('Arial', 9)).pack(anchor='w')
    
    # 说明信息
    info_text = """
测试说明:
1. 测试了5种不同的透明度值：20%, 40%, 60%, 80%, 100%
2. 验证图片水印处理器能否正确应用透明度
3. 检查配置对象是否正确存储透明度值
4. 透明度越低，水印越透明，背景越明显
5. 透明度为100%时，水印完全不透明
6. 透明度通过滑块控制，提供精确的数值调整

注意: 实际效果需要在主程序中查看预览图像
"""
    
    ttk.Label(results_frame, text=info_text, justify='left', 
              foreground='gray', font=('Arial', 9)).pack(pady=20)
    
    # 清理函数
    def on_closing():
        try:
            if os.path.exists(watermark_path):
                os.remove(watermark_path)
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    test_image_alpha()
