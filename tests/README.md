# 测试目录结构

本目录包含 PhotoWatermark 项目的所有测试相关文件。

## 📁 目录结构

```
tests/
├── README.md              # 本文档
├── run_tests.py           # 测试运行脚本
├── unit/                  # 单元测试
│   ├── __init__.py
│   ├── test_color_utils.py
│   └── test_config.py
├── integration/           # 集成测试
│   └── test_file_processing.py
├── debug/                 # 调试工具
│   ├── debug_gui.py       # GUI调试工具
│   └── test_drag_drop.py  # 拖拽功能测试
└── fixtures/              # 测试数据和工具
    ├── create_test_image.py
    ├── test_images/       # 测试图片
    └── test_output/       # 测试输出
```

## 🧪 测试类型说明

### 单元测试 (unit/)
- **目的**: 测试单个模块或函数的功能
- **文件**: `test_*.py`
- **运行**: `python -m unittest discover tests/unit`

### 集成测试 (integration/)
- **目的**: 测试多个模块协同工作
- **文件**: `test_*.py`
- **运行**: `python -m unittest discover tests/integration`

### 调试工具 (debug/)
- **目的**: 用于开发和调试的实用工具
- **文件**: `debug_*.py`, `test_*.py`
- **运行**: 直接执行相应的Python文件

### 测试数据 (fixtures/)
- **目的**: 测试所需的数据文件和辅助工具
- **内容**: 测试图片、输出目录、数据生成脚本

## 🚀 运行测试

### 运行所有测试
```bash
# 使用测试运行脚本
python tests/run_tests.py

# 或使用unittest
python -m unittest discover tests/unit
python -m unittest discover tests/integration
```

### 运行特定测试
```bash
# 单元测试
python -m unittest tests.unit.test_config

# 集成测试
python -m unittest tests.integration.test_file_processing
```

### 使用调试工具
```bash
# GUI调试工具
python tests/debug/debug_gui.py

# 拖拽功能测试
python tests/debug/test_drag_drop.py

# 创建测试图片
python tests/fixtures/create_test_image.py
```

## 📊 测试覆盖范围

### 已有测试
- ✅ 颜色工具函数测试
- ✅ 配置管理测试
- ✅ 文件处理集成测试

### 调试工具
- ✅ GUI界面调试
- ✅ 拖拽功能测试
- ✅ 文件处理流程验证

### 需要补充的测试
- 📋 EXIF读取功能测试
- 📋 水印处理功能测试
- 📋 图片尺寸调整测试
- 📋 导出功能端到端测试

## 🛠️ 添加新测试

### 单元测试
在 `tests/unit/` 目录下创建 `test_模块名.py` 文件。

### 集成测试
在 `tests/integration/` 目录下创建测试文件。

### 调试工具
在 `tests/debug/` 目录下创建调试脚本。

---

**维护者**: PhotoWatermark 开发团队  
**最后更新**: 2025-09-28
