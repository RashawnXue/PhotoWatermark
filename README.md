# PhotoWatermark - 基于EXIF拍摄时间的图片水印工具

一个强大的图片水印工具，能够自动读取图片的EXIF信息中的拍摄时间，并将其作为水印添加到图片上。提供命令行界面和图形用户界面两种使用方式，支持批量处理、多种样式配置和预览功能。

## ✨ 特性

### 核心功能
- 🕐 **自动提取拍摄时间**: 从图片EXIF信息中自动提取拍摄日期
- 🎨 **丰富的样式选项**: 支持字体大小、颜色、透明度、位置等自定义设置
- 📁 **批量处理**: 支持单张图片或整个目录的批量处理
- 🔍 **预览功能**: 在实际处理前预览水印效果
- ⚙️ **配置文件**: 支持保存和加载自定义配置
- 📊 **进度显示**: 清晰的处理进度和统计信息

### 界面选择
- 💻 **命令行界面**: 适合批量处理和自动化脚本
- 🖥️ **图形用户界面**: 直观的拖拽操作和可视化设置
- 🌈 **友好交互**: 彩色终端输出和现代化GUI设计

## 📦 安装

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 验证安装

```bash
# 验证命令行版本
python main.py --help

# 验证GUI版本
python gui_main.py
```

## 🚀 快速开始

### 🖥️ 图形界面版本（推荐）

```bash
# 启动GUI应用
python gui_main.py
```

**GUI功能特性：**
- 📂 **拖拽导入**: 直接拖拽图片文件或文件夹到应用窗口
- 🖼️ **缩略图预览**: 网格或列表视图显示导入的图片
- ⚙️ **可视化设置**: 直观的水印参数配置界面
- 📤 **灵活导出**: 自定义输出目录、文件命名和格式
- 📊 **实时进度**: 处理进度条和状态显示

### 💻 命令行版本

```bash
# 处理单张图片
python main.py /path/to/photo.jpg

# 处理整个目录
python main.py /path/to/photos

# 递归处理子目录
python main.py /path/to/photos --recursive
```

### 自定义样式

```bash
# 自定义颜色和位置
python main.py /path/to/photos -c red -p top-left

# 设置字体大小和透明度
python main.py /path/to/photos -s 32 -a 0.7

# 设置边距和日期格式
python main.py /path/to/photos -m 30 -f "DD MMM YYYY"
```

### 预览模式

```bash
# 预览水印效果（不保存文件）
python main.py /path/to/photos --preview
```

### 使用配置文件

```bash
# 使用预定义配置
python main.py /path/to/photos --config photo_watermark/templates/elegant_config.json

# 保存当前配置
python main.py /path/to/photos -c white -s 24 --save-config my_config.json
```

## 📖 详细用法

### 🖥️ GUI界面使用

#### 启动应用
```bash
python gui_main.py
```

#### 基本操作流程
1. **导入图片**
   - 拖拽文件/文件夹到应用窗口
   - 点击"选择文件"或"选择文件夹"按钮
   - 支持批量导入和递归子目录

2. **预览和选择**
   - 在"图片列表"标签页查看缩略图
   - 切换网格视图或列表视图
   - 选择要处理的图片（默认处理全部）

3. **配置水印**
   - 在左侧设置面板调整基本参数
   - 字体颜色、位置、透明度等
   - 点击"高级设置"进行更多配置

4. **导出设置**
   - 点击"导出图片"按钮
   - 选择输出目录（不能与原图目录相同）
   - 设置文件命名规则（原名/前缀/后缀）
   - 选择输出格式（JPEG/PNG）
   - 调整图片质量和尺寸

5. **开始处理**
   - 点击"导出"开始处理
   - 查看实时进度和状态
   - 处理完成后查看结果统计

#### GUI快捷键
- `Ctrl+O`: 导入文件
- `Ctrl+Shift+O`: 导入文件夹
- `Ctrl+E`: 导出图片
- `Ctrl+A`: 全选图片
- `Ctrl+L`: 清空列表
- `Ctrl+Q`: 退出应用

### 💻 命令行参数

```
python main.py [OPTIONS] INPUT_PATH

参数:
  INPUT_PATH                    输入图片文件或目录路径

选项:
  -o, --output DIR             输出目录 (默认: INPUT_PATH_watermark)
  -s, --font-size INT          字体大小 (默认: 自适应图片尺寸)
  -c, --color TEXT             字体颜色 (默认: white)
  -a, --alpha FLOAT            透明度 0.0-1.0 (默认: 0.8)
  -p, --position CHOICE        水印位置 (默认: bottom-right)
  -m, --margin INT             边距像素 (默认: 20)
  -f, --format CHOICE          日期格式 (默认: YYYY-MM-DD)
  --font-path PATH             自定义字体文件路径
  --output-format [JPEG|PNG]   输出图片格式 (默认: JPEG)
  --quality INT                JPEG输出质量 1-100 (默认: 95)
  --recursive                  递归处理子目录
  --preview                    预览模式，不保存文件
  --config FILE                使用配置文件
  --save-config FILE           保存当前配置到文件
  -v, --verbose                详细输出
  --no-banner                  不显示程序横幅
  --help                       显示帮助信息
```

### 水印位置选项

- `top-left`: 左上角
- `top-center`: 顶部居中
- `top-right`: 右上角
- `center-left`: 左侧居中
- `center`: 居中
- `center-right`: 右侧居中
- `bottom-left`: 左下角
- `bottom-center`: 底部居中
- `bottom-right`: 右下角 (默认)

### 日期格式选项

- `YYYY-MM-DD`: 2024-03-15 (默认)
- `YYYY/MM/DD`: 2024/03/15
- `DD-MM-YYYY`: 15-03-2024
- `DD/MM/YYYY`: 15/03/2024
- `MMM DD, YYYY`: Mar 15, 2024
- `DD MMM YYYY`: 15 Mar 2024

### 颜色格式支持

- **颜色名称**: white, black, red, green, blue, yellow, cyan, magenta, gray, orange, purple, brown, pink, lime, navy, teal, silver, gold
- **十六进制**: #FF0000, #ff0000, FF0000
- **RGB格式**: rgb(255,0,0), RGB(255, 0, 0)
- **逗号分隔**: 255,0,0

## 📁 项目结构

```
PhotoWatermark/
├── photo_watermark/           # 主程序包
│   ├── core/                  # 核心功能模块
│   │   ├── config.py          # 配置管理
│   │   ├── exif_reader.py     # EXIF信息读取
│   │   ├── watermark.py       # 水印处理
│   │   └── image_processor.py # 图像处理主模块
│   ├── gui/                   # 图形界面模块
│   │   ├── widgets/           # UI组件
│   │   │   ├── drag_drop.py   # 拖拽组件
│   │   │   ├── thumbnail.py   # 缩略图列表
│   │   │   └── progress.py    # 进度对话框
│   │   ├── main_window.py     # 主窗口
│   │   ├── file_manager.py    # 文件管理器
│   │   └── export_dialog.py   # 导出设置对话框
│   ├── utils/                 # 工具函数
│   │   ├── file_utils.py      # 文件操作工具
│   │   └── color_utils.py     # 颜色处理工具
│   ├── templates/             # 配置模板
│   │   ├── default_config.json
│   │   ├── elegant_config.json
│   │   └── minimal_config.json
│   ├── tests/                 # 测试用例
│   │   ├── test_config.py
│   │   └── test_color_utils.py
│   ├── cli.py                 # 命令行界面
│   ├── __main__.py            # 模块入口
│   └── __init__.py
├── docs/                      # 文档目录
│   └── prd/                   # 产品需求文档
│       ├── README.md          # PRD索引
│       ├── v1.0-photo-watermark-core.md
│       └── v2.0-gui-file-processing.md
├── main.py                    # 命令行程序入口
├── gui_main.py                # GUI程序入口
├── run_tests.py               # 测试运行脚本
├── requirements.txt           # 依赖文件
└── README.md                  # 说明文档
```

## 🧪 测试

运行测试用例：

```bash
python run_tests.py
```

或者使用unittest：

```bash
python -m unittest discover photo_watermark/tests
```

## 📝 使用示例

### 🖥️ GUI界面示例

1. **启动应用**
   ```bash
   python gui_main.py
   ```

2. **快速处理流程**
   - 拖拽图片文件夹到应用窗口
   - 在左侧面板调整水印设置
   - 点击"导出图片"按钮
   - 选择输出目录和文件格式
   - 开始处理并查看进度

### 💻 命令行示例

#### 示例1: 基本水印

```bash
python main.py ./sample_photos
```

这将：
- 处理 `./sample_photos` 目录下的所有图片
- 使用默认样式（白色文字，右下角，透明度0.8）
- 将结果保存到 `./sample_photos/sample_photos_watermark/` 目录

#### 示例2: 自定义样式

```bash
python main.py ./photos -c "rgb(255,255,0)" -p center -s 36 -a 0.6 -f "DD MMM YYYY"
```

这将：
- 使用黄色文字
- 水印位置居中
- 字体大小36像素
- 透明度0.6
- 日期格式为 "15 Mar 2024"

#### 示例3: 使用配置文件

```bash
# 首先保存配置
python main.py ./photos -c red -s 28 -p top-right --save-config red_style.json

# 然后使用保存的配置
python main.py ./new_photos --config red_style.json
```

#### 示例4: 预览和详细输出

```bash
python main.py ./photos --preview --verbose
```

这将：
- 预览水印效果但不保存文件
- 显示详细的处理信息

## ⚠️ 注意事项

1. **EXIF支持**: 只有JPEG和TIFF格式的图片支持EXIF信息读取
2. **拍摄时间**: 如果图片没有拍摄时间信息，将跳过处理
3. **输出目录**: 默认在输入目录下创建 `原目录名_watermark` 子目录
4. **文件覆盖**: 如果输出文件已存在，将被覆盖
5. **字体支持**: 程序会自动寻找系统字体，也可以指定自定义字体文件

## 🐛 故障排除

### 常见问题

**Q: 提示"无法提取拍摄时间信息"**
A: 检查图片是否包含EXIF信息，可以使用 `--verbose` 选项查看详细错误信息。

**Q: 字体显示异常**
A: 尝试使用 `--font-path` 指定一个有效的字体文件路径。

**Q: 处理速度慢**
A: 对于大量图片，可以降低输出质量或使用PNG格式以提高速度。

**Q: 内存占用过高**
A: 处理超大图片时可能占用较多内存，建议分批处理。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建Issue: [GitHub Issues](https://github.com/your-repo/PhotoWatermark/issues)
- 邮箱: your-email@example.com

---

**PhotoWatermark** - 让你的照片记录时光 📸✨
