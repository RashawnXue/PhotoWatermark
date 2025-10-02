# PhotoWatermark - 专业图片水印工具

一个功能强大的图片水印工具，支持多种水印类型和丰富的自定义选项。提供命令行界面和现代化图形用户界面，支持实时预览、批量处理、模板管理等专业功能。

## ✨ 特性

### 🎯 多种水印类型
- 📅 **EXIF时间水印**: 自动提取图片EXIF信息中的拍摄时间
- 📝 **自定义文本水印**: 任意文本内容，支持多行文本和特殊字符
- 🖼️ **图片水印**: 支持Logo、图标等图片水印，可调整大小和透明度

### 🎨 丰富的样式选项
- 🔤 **字体控制**: 系统字体选择、大小调节、粗体/斜体样式
- 🎨 **颜色设置**: 字体颜色、透明度、阴影效果、描边效果
- 📍 **位置控制**: 九宫格预设位置、自定义坐标、边距调节
- 🔄 **旋转功能**: 任意角度旋转，实时预览效果

### 🖥️ 现代化界面
- 🎯 **实时预览**: 参数调整即时显示效果，支持多图片切换预览
- 🖱️ **拖拽操作**: 直接拖拽文件导入，预览窗口内拖拽定位水印
- 📱 **响应式布局**: 自适应窗口大小，支持缩放和滚动
- 🎛️ **直观控制**: 滑块、颜色选择器、实时坐标显示

### ⚙️ 专业功能
- 💾 **模板管理**: 保存/加载水印配置模板，快速应用预设样式
- 📁 **批量处理**: 支持整个目录的批量处理，递归子目录
- 📊 **进度显示**: 详细的处理进度和统计信息
- 🔧 **配置持久化**: 自动保存上次会话设置，程序重启恢复状态

### 💻 双重界面
- 🖥️ **图形用户界面**: 直观的拖拽操作和可视化设置（推荐）
- 💻 **命令行界面**: 适合批量处理和自动化脚本
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
- 👁️ **实时预览**: 水印效果实时显示，支持多图片切换预览
- 🖱️ **交互式定位**: 在预览窗口内直接拖拽水印到目标位置
- ⚙️ **可视化设置**: 直观的水印参数配置界面
- 🎨 **多种水印类型**: 支持时间、文本、图片三种水印类型
- 💾 **模板管理**: 保存和加载水印配置模板
- 📤 **灵活导出**: 自定义输出目录、文件命名和格式
- 📊 **实时进度**: 处理进度条和状态显示

### 💻 命令行版本

```bash
# 处理单张图片（默认EXIF时间水印）
python main.py /path/to/photo.jpg

# 处理整个目录
python main.py /path/to/photos

# 递归处理子目录
python main.py /path/to/photos --recursive
```

### 多种水印类型

```bash
# EXIF时间水印（默认）
python main.py /path/to/photos --watermark-type timestamp

# 自定义文本水印
python main.py /path/to/photos --watermark-type text --text "© 2024 My Photos"

# 图片水印
python main.py /path/to/photos --watermark-type image --image-path /path/to/logo.png
```

### 自定义样式

```bash
# 自定义颜色和位置
python main.py /path/to/photos -c red -p top-left

# 设置字体大小和透明度
python main.py /path/to/photos -s 32 -a 0.7

# 设置边距和日期格式
python main.py /path/to/photos -m 30 -f "DD MMM YYYY"

# 添加阴影和描边效果
python main.py /path/to/photos --shadow --stroke-width 2 --stroke-color black
```

### 预览模式

```bash
# 预览水印效果（不保存文件）
python main.py /path/to/photos --preview
```

### 使用配置文件

```bash
# 使用预定义配置模板
python main.py /path/to/photos --config src/templates/elegant_config.json

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

2. **选择水印类型**
   - **时间水印**: 自动提取EXIF拍摄时间
   - **文本水印**: 输入自定义文本内容
   - **图片水印**: 选择Logo或图标文件

3. **预览和调整**
   - 在"预览"标签页实时查看水印效果
   - 支持多图片切换预览
   - 直接在预览窗口拖拽调整水印位置
   - 使用九宫格快速定位或精确坐标输入

4. **样式配置**
   - **字体设置**: 字体、大小、粗体/斜体
   - **颜色效果**: 字体颜色、透明度、阴影、描边
   - **位置控制**: 预设位置或自定义坐标
   - **旋转角度**: 任意角度旋转水印

5. **模板管理**
   - 保存当前配置为模板以便复用
   - 加载预设模板或自定义模板
   - 程序自动保存上次会话设置

6. **导出设置**
   - 点击"导出图片"按钮
   - 选择输出目录（不能与原图目录相同）
   - 设置文件命名规则（原名/前缀/后缀）
   - 选择输出格式（JPEG/PNG）
   - 调整图片质量和尺寸

7. **开始处理**
   - 点击"导出"开始处理
   - 查看实时进度和状态
   - 处理完成后查看结果统计

#### GUI快捷键
- `Ctrl+O`: 导入文件
- `Ctrl+Shift+O`: 导入文件夹
- `Ctrl+E`: 导出图片
- `Ctrl+S`: 保存模板
- `Ctrl+L`: 加载模板
- `Ctrl+A`: 全选图片
- `Ctrl+D`: 清空列表
- `Ctrl+Q`: 退出应用

### 💻 命令行参数

```
python main.py [OPTIONS] INPUT_PATH

参数:
  INPUT_PATH                    输入图片文件或目录路径

基本选项:
  -o, --output DIR             输出目录 (默认: INPUT_PATH_watermark)
  --watermark-type CHOICE      水印类型: timestamp|text|image (默认: timestamp)
  --recursive                  递归处理子目录
  --preview                    预览模式，不保存文件
  -v, --verbose                详细输出
  --help                       显示帮助信息

文本水印选项:
  --text TEXT                  自定义文本内容 (用于text类型)
  -s, --font-size INT          字体大小 (默认: 自适应图片尺寸)
  -c, --color TEXT             字体颜色 (默认: white)
  -a, --alpha FLOAT            透明度 0.0-1.0 (默认: 0.8)
  --font-path PATH             自定义字体文件路径
  --bold                       粗体字体
  --italic                     斜体字体
  --shadow                     启用阴影效果
  --shadow-color TEXT          阴影颜色 (默认: black)
  --stroke-width INT           描边宽度 (默认: 0)
  --stroke-color TEXT          描边颜色 (默认: black)

图片水印选项:
  --image-path PATH            水印图片路径 (用于image类型)
  --scale-mode CHOICE          缩放模式: percentage|fixed_size (默认: percentage)
  --scale-percentage FLOAT     缩放百分比 0.1-2.0 (默认: 0.1)

位置和旋转选项:
  -p, --position CHOICE        水印位置 (默认: bottom-right)
  -m, --margin INT             边距像素 (默认: 20)
  --rotation FLOAT             旋转角度 -180到180 (默认: 0)

输出选项:
  --output-format [JPEG|PNG]   输出图片格式 (默认: JPEG)
  --quality INT                JPEG输出质量 1-100 (默认: 95)

配置管理:
  --config FILE                使用配置文件
  --save-config FILE           保存当前配置到文件
  -f, --format CHOICE          日期格式 (默认: YYYY-MM-DD, 仅timestamp类型)
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

### 水印类型说明

#### 📅 时间水印 (timestamp)
- 自动提取图片EXIF信息中的拍摄时间
- 支持多种日期格式显示
- 适用于有EXIF信息的JPEG和TIFF图片

#### 📝 文本水印 (text)
- 支持任意自定义文本内容
- 支持多行文本（换行符分隔）
- 丰富的字体样式选择
- 阴影和描边效果增强可读性

#### 🖼️ 图片水印 (image)
- 支持PNG、JPEG等常见图片格式
- 自动处理透明背景
- 灵活的缩放模式
- 支持旋转和翻转效果

## 📁 项目结构

```
PhotoWatermark/
├── src/                       # 主程序包
│   ├── core/                  # 核心功能模块
│   │   ├── config.py          # 配置管理和数据模型
│   │   ├── exif_reader.py     # EXIF信息读取
│   │   ├── watermark.py       # 多类型水印处理器
│   │   ├── image_processor.py # 图像处理主模块
│   │   └── template_manager.py # 模板管理器
│   ├── gui/                   # 图形界面模块
│   │   ├── widgets/           # UI组件
│   │   │   ├── drag_drop.py   # 拖拽组件
│   │   │   ├── thumbnail.py   # 缩略图列表
│   │   │   ├── progress.py    # 进度对话框
│   │   │   ├── preview.py     # 实时预览组件
│   │   │   └── export_confirm.py # 导出确认对话框
│   │   ├── main_window.py     # 主窗口（含实时预览）
│   │   ├── file_manager.py    # 文件管理器
│   │   └── export_dialog.py   # 导出设置对话框
│   ├── utils/                 # 工具函数
│   │   ├── file_utils.py      # 文件操作工具
│   │   ├── color_utils.py     # 颜色处理工具
│   │   └── font_manager.py    # 字体管理器
│   ├── templates/             # 配置模板
│   │   ├── default_config.json
│   │   ├── elegant_config.json
│   │   └── minimal_config.json
│   ├── cli.py                 # 命令行界面
│   ├── __main__.py            # 模块入口
│   └── __init__.py
├── tests/                     # 测试用例
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   ├── debug/                 # 调试脚本
│   ├── fixtures/              # 测试数据
│   └── run_tests.py           # 测试运行脚本
├── docs/                      # 文档目录
│   ├── prd/                   # 产品需求文档
│   │   ├── v1.0-photo-watermark-core.md
│   │   ├── v2.0-gui-file-processing.md
│   │   ├── v2.1-watermark-types.md
│   │   ├── v2.2-watermark-layout-preview.md
│   │   └── v2.3-configuration-management.md
│   └── FONT_FEATURES.md       # 字体功能说明
├── packaging/                 # 打包脚本
│   ├── build_app.sh          # 应用构建脚本
│   └── README.md             # 打包说明
├── assets/                   # 应用资源
│   └── icon.png              # 应用图标
├── main.py                   # 命令行程序入口
├── gui_main.py               # GUI程序入口
├── requirements.txt          # 依赖文件
└── README.md                 # 说明文档
```

## 🧪 测试

运行测试用例：

```bash
# 运行完整测试套件
python tests/run_tests.py

# 运行单元测试
python -m unittest discover tests/unit

# 运行集成测试
python -m unittest discover tests/integration

# 运行特定测试
python -m unittest tests.unit.test_config
```

## 📝 使用示例

### 🖥️ GUI界面示例

1. **启动应用**
   ```bash
   python gui_main.py
   ```

2. **多种水印类型快速上手**
   - **时间水印**: 拖拽照片 → 选择时间水印 → 实时预览 → 导出
   - **文本水印**: 输入自定义文本 → 调整字体样式 → 预览效果 → 导出
   - **图片水印**: 选择Logo文件 → 调整大小位置 → 预览效果 → 导出

3. **实时预览功能**
   - 导入多张图片后，在预览窗口切换查看不同图片的水印效果
   - 直接在预览图上拖拽水印到合适位置
   - 使用九宫格快速定位或精确坐标输入
   - 实时调整旋转角度、透明度等参数

### 💻 命令行示例

#### 示例1: 基本时间水印

```bash
python main.py ./sample_photos
```

这将：
- 处理 `./sample_photos` 目录下的所有图片
- 自动提取EXIF拍摄时间作为水印
- 使用默认样式（白色文字，右下角，透明度0.8）
- 将结果保存到 `./sample_photos_watermark/` 目录

#### 示例2: 自定义文本水印

```bash
python main.py ./photos --watermark-type text --text "© 2024 My Studio" -c "rgb(255,255,0)" -p center -s 36 --shadow
```

这将：
- 创建自定义文本水印 "© 2024 My Studio"
- 使用黄色文字，居中位置，36像素字体
- 添加阴影效果增强可读性

#### 示例3: 图片Logo水印

```bash
python main.py ./photos --watermark-type image --image-path ./logo.png --scale-percentage 0.15 -p top-right -a 0.7
```

这将：
- 使用logo.png作为图片水印
- 缩放到原图15%大小
- 放置在右上角，透明度0.7

#### 示例4: 高级文本效果

```bash
python main.py ./photos --watermark-type text --text "PROFESSIONAL\nPHOTOGRAPHY" --bold --stroke-width 3 --stroke-color black --rotation 45
```

这将：
- 创建多行文本水印
- 粗体字体，黑色描边
- 45度角旋转效果

#### 示例5: 使用模板配置

```bash
# 保存当前配置为模板
python main.py ./photos --text "My Watermark" --bold --shadow --save-config my_template.json

# 使用保存的模板
python main.py ./new_photos --config my_template.json

# 使用内置优雅模板
python main.py ./photos --config src/templates/elegant_config.json
```

#### 示例6: 预览和调试

```bash
python main.py ./photos --preview --verbose
```

这将：
- 预览所有水印效果但不保存文件
- 显示详细的处理信息和错误诊断

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
