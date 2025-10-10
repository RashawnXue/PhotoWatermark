# Windows打包快速修复指南

## 🚨 错误解决

如果遇到 `NameError: name '__file__' is not defined` 错误，请按以下步骤操作：

### 方法一：使用简化版配置文件（推荐）

```cmd
# 使用简化版spec文件
pyinstaller PhotoWatermark_windows_simple.spec
```

### 方法二：使用自动化脚本

```cmd
# 使用Python脚本（自动选择最佳配置）
python build_windows.py

# 或使用批处理脚本
packaging\build_windows.bat
```

### 方法三：手动修复原配置文件

如果你想继续使用 `PhotoWatermark_windows.spec`，确保文件开头是这样的：

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# 获取项目根目录 - 使用当前工作目录
ROOT_DIR = Path(os.getcwd())
```

## 🔧 完整的Windows打包流程

### 1. 环境准备

```cmd
# 确保在项目根目录
cd PhotoWatermark

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 验证环境

```cmd
# 运行验证脚本
python verify_windows_build.py
```

### 3. 开始打包

选择以下任一方法：

**方法A - 自动化脚本（最简单）：**
```cmd
python build_windows.py
```

**方法B - 简化配置文件：**
```cmd
pyinstaller PhotoWatermark_windows_simple.spec
```

**方法C - 批处理脚本：**
```cmd
packaging\build_windows.bat
```

### 4. 测试结果

```cmd
# 测试生成的程序
dist\PhotoWatermark\PhotoWatermark.exe
```

## 🐛 常见问题解决

### 问题1：`__file__` 未定义
**解决方案**：使用 `PhotoWatermark_windows_simple.spec`

### 问题2：找不到模块
**解决方案**：检查 `hiddenimports` 列表，添加缺失的模块

### 问题3：资源文件缺失
**解决方案**：确保 `src/templates` 和 `assets` 目录存在

### 问题4：DLL缺失
**解决方案**：使用我们提供的完整配置文件

## 📋 检查清单

打包前请确认：

- [ ] Python 3.8+ 已安装
- [ ] 所有依赖已安装 (`pip install -r requirements.txt`)
- [ ] PyInstaller已安装 (`pip install pyinstaller`)
- [ ] 项目文件完整（`src/`, `assets/`, `gui_main.py`）
- [ ] 在项目根目录执行命令

## 🎯 推荐流程

1. **验证环境**：`python verify_windows_build.py`
2. **自动打包**：`python build_windows.py`
3. **测试程序**：运行生成的exe文件
4. **在目标机器测试**：确保在没有Python的Windows机器上能运行

## 💡 提示

- 使用虚拟环境可以避免依赖冲突
- 简化版配置文件更稳定，推荐使用
- 如果遇到问题，先运行验证脚本检查环境
- 生成的程序在 `dist/PhotoWatermark/` 目录中

## 📞 获取帮助

如果仍有问题：

1. 运行 `python verify_windows_build.py` 检查环境
2. 查看 `packaging/WINDOWS_BUILD_GUIDE.md` 详细指南
3. 检查PyInstaller输出的错误信息
4. 确保在Windows环境下打包（不是WSL或虚拟机）
