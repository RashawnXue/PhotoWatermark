# PhotoWatermark Windows 打包指南

## 🎯 概述

本指南详细说明如何为Windows平台打包PhotoWatermark，解决DLL缺失和依赖问题。

## 🛠️ 环境要求

### 基础要求
- **操作系统**: Windows 10 或更高版本
- **Python**: 3.8+ (推荐3.10+)
- **内存**: 至少4GB
- **磁盘空间**: 至少2GB可用空间

### 可选工具
- **ImageMagick**: 用于图标格式转换
- **Inno Setup**: 用于创建安装程序
- **Visual Studio**: 用于编译扩展（如需要）

## 📦 快速打包

### 方法一：使用Python脚本（推荐）

```cmd
# 在项目根目录下
python build_windows.py
```

### 方法二：使用批处理脚本

```cmd
# 在项目根目录下
packaging\build_windows.bat
```

### 方法三：手动打包

```cmd
# 1. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 2. 使用专用配置文件打包
pyinstaller PhotoWatermark_windows.spec
```

## 🔧 详细步骤

### 1. 环境准备

```cmd
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 解决常见问题

#### DLL缺失问题
- 确保在Windows环境下打包
- 使用虚拟环境避免依赖冲突
- 检查Python安装是否完整

#### 模块导入错误
- 在`PhotoWatermark_windows.spec`中添加缺失的模块到`hiddenimports`
- 检查第三方库的依赖

#### 文件路径问题
- 使用相对路径
- 确保资源文件正确打包

### 3. 自定义配置

编辑`PhotoWatermark_windows.spec`文件：

```python
# 添加隐藏导入
hiddenimports = [
    'your_missing_module',
    # ... 其他模块
]

# 添加数据文件
datas = [
    ('path/to/data', 'destination'),
    # ... 其他数据文件
]

# 添加二进制文件
binaries = [
    ('path/to/dll', '.'),
    # ... 其他DLL文件
]
```

## 🧪 测试打包结果

### 本地测试

```cmd
# 运行生成的可执行文件
dist\PhotoWatermark\PhotoWatermark.exe
```

### 在干净环境测试

1. 在没有安装Python的Windows机器上测试
2. 检查所有功能是否正常
3. 测试文件拖拽、导入导出等功能

### 常见测试项目

- [ ] 程序正常启动
- [ ] GUI界面显示正常
- [ ] 文件导入功能
- [ ] 水印添加功能
- [ ] 图片导出功能
- [ ] 设置保存和加载
- [ ] 模板管理功能

## 📋 故障排除

### 问题：找不到Python DLL

**解决方案：**
1. 确保在Windows环境下打包
2. 使用完整的Python安装（不是嵌入式版本）
3. 检查PyInstaller版本兼容性

```cmd
# 重新安装PyInstaller
pip uninstall pyinstaller
pip install pyinstaller==5.13.2
```

### 问题：模块导入失败

**解决方案：**
1. 在spec文件中添加隐藏导入
2. 检查模块是否正确安装

```python
hiddenimports = [
    'tkinterdnd2',
    'piexif',
    'PIL.ImageTk',
    # 添加其他缺失的模块
]
```

### 问题：资源文件缺失

**解决方案：**
1. 检查datas配置
2. 确保路径正确

```python
datas = [
    ('src/templates', 'src/templates'),
    ('assets', 'assets'),
]
```

### 问题：程序启动慢

**解决方案：**
1. 使用目录模式而非单文件模式
2. 排除不必要的模块
3. 优化导入结构

## 🚀 创建安装程序

### 使用Inno Setup

1. 安装Inno Setup
2. 打开`packaging/PhotoWatermark_installer.iss`
3. 编译生成安装程序

```cmd
# 命令行编译（如果安装了Inno Setup命令行工具）
iscc packaging\PhotoWatermark_installer.iss
```

### 安装程序特性

- 自动检测系统要求
- 创建桌面快捷方式
- 注册文件关联
- 支持卸载
- 多语言支持

## 📊 优化建议

### 减小文件大小

1. 排除不必要的模块
2. 使用UPX压缩
3. 优化资源文件

### 提高启动速度

1. 使用目录模式
2. 延迟导入非关键模块
3. 优化初始化代码

### 提高兼容性

1. 静态链接依赖
2. 包含Visual C++ Redistributable
3. 支持多个Windows版本

## 📝 发布清单

- [ ] 在多个Windows版本上测试
- [ ] 检查所有功能正常
- [ ] 创建安装程序
- [ ] 准备用户文档
- [ ] 设置自动更新机制
- [ ] 代码签名（可选）

## 🔗 相关资源

- [PyInstaller官方文档](https://pyinstaller.readthedocs.io/)
- [Inno Setup官网](https://jrsoftware.org/isinfo.php)
- [Windows应用程序认证](https://docs.microsoft.com/en-us/windows/apps/get-started/)

## 💡 提示

1. 始终在目标平台上测试
2. 保持依赖版本的一致性
3. 定期更新打包配置
4. 考虑使用CI/CD自动化打包
5. 为用户提供详细的安装说明
