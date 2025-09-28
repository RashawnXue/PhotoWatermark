"""
文件操作工具函数
"""

import os
import shutil
from typing import List, Optional
from pathlib import Path


def ensure_dir_exists(dir_path: str) -> None:
    """确保目录存在，如果不存在则创建"""
    os.makedirs(dir_path, exist_ok=True)


def get_safe_filename(filename: str) -> str:
    """获取安全的文件名（移除非法字符）"""
    # 移除或替换文件名中的非法字符
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    return safe_name


def get_unique_filename(filepath: str) -> str:
    """如果文件已存在，生成唯一的文件名"""
    if not os.path.exists(filepath):
        return filepath
    
    base, ext = os.path.splitext(filepath)
    counter = 1
    
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    
    return f"{base}_{counter}{ext}"


def copy_file_with_metadata(src: str, dst: str) -> None:
    """复制文件并保持元数据"""
    shutil.copy2(src, dst)


def get_file_size_mb(filepath: str) -> float:
    """获取文件大小（MB）"""
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)


def list_files_by_extension(directory: str, extensions: List[str], 
                          recursive: bool = False) -> List[str]:
    """按扩展名列出文件"""
    files = []
    extensions = [ext.lower() for ext in extensions]
    
    if recursive:
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if any(filename.lower().endswith(ext) for ext in extensions):
                    files.append(filepath)
    
    return sorted(files)


def validate_output_directory(output_dir: str, create_if_not_exists: bool = True) -> bool:
    """验证输出目录"""
    if os.path.exists(output_dir):
        if not os.path.isdir(output_dir):
            return False
        # 检查是否可写
        return os.access(output_dir, os.W_OK)
    else:
        if create_if_not_exists:
            try:
                os.makedirs(output_dir, exist_ok=True)
                return True
            except OSError:
                return False
        return False
