"""
命令行界面模块

提供友好的命令行参数解析和程序入口。
"""

import os
import sys
from typing import Optional
import click
from colorama import init, Fore, Style

from .core.config import Config, WatermarkConfig, Position, DateFormat
from .core.image_processor import ImageProcessor
from .utils.color_utils import get_available_colors, parse_color

# 初始化colorama
init()


def print_banner():
    """打印程序横幅"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    PhotoWatermark v1.0.0                    ║
║              基于EXIF拍摄时间的图片水印工具                  ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_success(message: str):
    """打印成功信息"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """打印错误信息"""
    print(f"{Fore.RED}✗ 错误: {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{Fore.YELLOW}⚠ 警告: {message}{Style.RESET_ALL}")


def print_info(message: str):
    """打印信息"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def validate_color(ctx, param, value):
    """验证颜色参数"""
    if value is None:
        return value
    
    parsed_color = parse_color(value)
    if parsed_color is None:
        available_colors = list(get_available_colors().keys())
        raise click.BadParameter(
            f"无效的颜色格式: {value}\\n"
            f"支持的格式:\\n"
            f"  - 颜色名称: {', '.join(available_colors[:10])}...\\n"
            f"  - 十六进制: #FF0000, ff0000\\n"
            f"  - RGB: rgb(255,0,0) 或 255,0,0"
        )
    
    return value


def validate_position(ctx, param, value):
    """验证位置参数"""
    if value is None:
        return value
    
    try:
        return Position(value)
    except ValueError:
        valid_positions = [pos.value for pos in Position]
        raise click.BadParameter(
            f"无效的位置: {value}\\n"
            f"支持的位置: {', '.join(valid_positions)}"
        )


def validate_date_format(ctx, param, value):
    """验证日期格式参数"""
    if value is None:
        return value
    
    try:
        return DateFormat(value)
    except ValueError:
        valid_formats = [fmt.value for fmt in DateFormat]
        raise click.BadParameter(
            f"无效的日期格式: {value}\\n"
            f"支持的格式: {', '.join(valid_formats)}"
        )


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', 
              help='输出目录 (默认: INPUT_PATH_watermark)')
@click.option('-s', '--font-size', type=int,
              help='字体大小 (默认: 自适应图片尺寸)')
@click.option('-c', '--color', default='white', callback=validate_color,
              help='字体颜色 (默认: white)')
@click.option('-a', '--alpha', type=float, default=0.8,
              help='透明度 0.0-1.0 (默认: 0.8)')
@click.option('-p', '--position', default='bottom-right', callback=validate_position,
              help='水印位置 (默认: bottom-right)')
@click.option('-m', '--margin', type=int, default=20,
              help='边距像素 (默认: 20)')
@click.option('-f', '--format', 'date_format', default='YYYY-MM-DD', 
              callback=validate_date_format,
              help='日期格式 (默认: YYYY-MM-DD)')
@click.option('--font-path', type=click.Path(exists=True),
              help='自定义字体文件路径')
@click.option('--output-format', type=click.Choice(['JPEG', 'PNG'], case_sensitive=False),
              default='JPEG', help='输出图片格式 (默认: JPEG)')
@click.option('--quality', type=click.IntRange(1, 100), default=95,
              help='JPEG输出质量 1-100 (默认: 95)')
@click.option('--recursive', is_flag=True,
              help='递归处理子目录')
@click.option('--preview', is_flag=True,
              help='预览模式，不保存文件')
@click.option('--config', 'config_file', type=click.Path(exists=True),
              help='使用配置文件')
@click.option('--save-config', 'save_config_file', type=click.Path(),
              help='保存当前配置到文件')
@click.option('-v', '--verbose', is_flag=True,
              help='详细输出')
@click.option('--no-banner', is_flag=True,
              help='不显示程序横幅')
def main(input_path: str, output_dir: Optional[str], font_size: Optional[int],
         color: str, alpha: float, position: Position, margin: int,
         date_format: DateFormat, font_path: Optional[str], 
         output_format: str, quality: int, recursive: bool, preview: bool,
         config_file: Optional[str], save_config_file: Optional[str],
         verbose: bool, no_banner: bool):
    """
    PhotoWatermark - 基于EXIF拍摄时间的图片水印工具
    
    INPUT_PATH: 输入图片文件或目录路径
    
    示例:
    
        # 基本使用
        python -m photo_watermark /path/to/photos
        
        # 自定义样式
        python -m photo_watermark /path/to/photos -c red -s 24 -p top-left
        
        # 使用配置文件
        python -m photo_watermark /path/to/photos --config my_style.json
        
        # 预览效果
        python -m photo_watermark /path/to/photos --preview
        
        # 递归处理
        python -m photo_watermark /path/to/photos --recursive
    """
    
    # 显示横幅
    if not no_banner:
        print_banner()
    
    try:
        # 验证透明度范围
        if not 0.0 <= alpha <= 1.0:
            print_error("透明度必须在 0.0 到 1.0 之间")
            sys.exit(1)
        
        # 创建配置对象
        config = Config()
        
        # 如果指定了配置文件，先加载配置
        if config_file:
            try:
                config.load_from_file(config_file)
                print_info(f"已加载配置文件: {config_file}")
            except Exception as e:
                print_error(f"加载配置文件失败: {e}")
                sys.exit(1)
        
        # 更新配置参数（命令行参数优先）
        if font_size is not None:
            config.config.font_size = font_size
        config.config.font_color = color
        config.config.font_alpha = alpha
        config.config.position = position
        config.config.margin = margin
        config.config.date_format = date_format
        if font_path:
            config.config.font_path = font_path
        config.config.output_format = output_format.upper()
        config.config.output_quality = quality
        config.config.recursive = recursive
        config.config.preview_mode = preview
        config.config.verbose = verbose
        
        # 保存配置文件
        if save_config_file:
            try:
                config.save_to_file(save_config_file)
                print_success(f"配置已保存到: {save_config_file}")
            except Exception as e:
                print_error(f"保存配置文件失败: {e}")
                sys.exit(1)
        
        # 显示当前配置
        if verbose:
            print_info("当前配置:")
            print(f"  输入路径: {input_path}")
            print(f"  输出目录: {output_dir or '自动生成'}")
            print(f"  字体大小: {config.config.font_size or '自适应'}")
            print(f"  字体颜色: {config.config.font_color}")
            print(f"  透明度: {config.config.font_alpha}")
            print(f"  位置: {config.config.position.value}")
            print(f"  边距: {config.config.margin}px")
            print(f"  日期格式: {config.config.date_format.value}")
            print(f"  输出格式: {config.config.output_format}")
            if config.config.output_format == 'JPEG':
                print(f"  输出质量: {config.config.output_quality}")
            print(f"  递归处理: {'是' if config.config.recursive else '否'}")
            print(f"  预览模式: {'是' if config.config.preview_mode else '否'}")
            print()
        
        # 创建图像处理器
        processor = ImageProcessor(config)
        
        # 验证输入路径
        if not processor.validate_input_path(input_path):
            sys.exit(1)
        
        # 开始处理
        if preview:
            print_info("预览模式 - 不会保存文件")
        
        print_info("开始处理图片...")
        processor.process_images(input_path, output_dir)
        
        print_success("处理完成!")
        
    except KeyboardInterrupt:
        print_warning("\\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print_error(f"程序运行出错: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.group()
def cli():
    """PhotoWatermark 工具集"""
    pass


@cli.command()
def colors():
    """显示所有可用的颜色名称"""
    print_info("可用的颜色名称:")
    colors_dict = get_available_colors()
    for name, rgb in colors_dict.items():
        print(f"  {name:<12} RGB{rgb}")


@cli.command()
def positions():
    """显示所有可用的位置选项"""
    print_info("可用的水印位置:")
    for pos in Position:
        print(f"  {pos.value}")


@cli.command()
def formats():
    """显示所有可用的日期格式"""
    print_info("可用的日期格式:")
    for fmt in DateFormat:
        print(f"  {fmt.value}")


if __name__ == '__main__':
    # 如果直接运行cli.py，执行主命令
    main()
