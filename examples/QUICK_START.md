# 快速使用指南 (Quick Start Guide)

## 🎨 可视化功能已全面升级！

### 主要改进

✅ **中文字体支持** - 所有图表完美显示中文  
✅ **统一输出路径** - `examples/figures/` 目录  
✅ **增强的可视化** - 更多信息，更美观的图表  
✅ **双语标签** - 中英文对照，便于交流

---

## 🚀 快速开始

### 1. 运行基本对比示例

```bash
cd examples
python basic_comparison.py
```

**生成图表**:
- `figures/pet_timeseries.png` - 时间序列综合分析
- `figures/pet_boxplot.png` - 分布统计对比
- `figures/pet_correlation.png` - 相关性分析
- `figures/pet_differences.png` - 差异量化分析

**特点**: 
- 3层时间序列图（主图+月平均+极差）
- 箱线图+统计表格
- 相关性热图+相似度柱状图
- 差异热图+统计摘要

---

### 2. 运行CO2敏感性分析

```bash
cd examples
python co2_sensitivity.py
```

**生成图表**:
- `figures/co2_sensitivity_enhanced.png` - 多面板敏感性分析
- `figures/co2_relative_change.png` - 绝对值与相对变化对比

**特点**:
- 6个单独公式子图 + 1个综合对比图
- 置信区间显示
- 百分比变化标注
- 参考线标注

---

### 3. 测试中文字体

```bash
cd examples
python test_visualization.py
```

**输出**:
- 显示检测到的中文字体
- 生成测试图表验证中文显示
- 列出系统所有可用中文字体

---

## 📊 图表说明

### 时间序列图 (Time Series)
**用途**: 观察PET随时间变化  
**包含**: 主时间序列 + 月平均 + 公式间极差  
**适合**: 长期趋势、季节性分析

### 箱线图 (Box Plot)
**用途**: 比较分布特征  
**包含**: 箱线图 + 统计表（均值、标准差、最值）  
**适合**: 统计分析、离群值检测

### 相关性矩阵 (Correlation Matrix)
**用途**: 分析公式相关性  
**包含**: 热图 + 平均相关系数柱状图  
**适合**: 相似度评估、冗余分析

### 差异热图 (Differences Heatmap)
**用途**: 量化公式差异  
**包含**: 差异矩阵 + 统计摘要  
**适合**: 公式选择、不确定性评估

### CO2敏感性 (CO2 Sensitivity)
**用途**: 评估CO2响应  
**包含**: 多子图 + 综合对比 + 百分比标注  
**适合**: 气候变化影响评估

---

## 🎯 自定义使用

### 修改输出路径

```python
from pathlib import Path

# 自定义输出目录
OUTPUT_DIR = Path("my_figures")
OUTPUT_DIR.mkdir(exist_ok=True)

# 在绘图函数中指定路径
fig = plot_timeseries(data, save_path=OUTPUT_DIR / "my_plot.png")
```

### 检查中文字体

```python
from pet_comparison.analysis.visualization import setup_chinese_font

# 设置并获取字体名称
font = setup_chinese_font()
print(f"使用的字体: {font}")
```

### 调整图表大小

```python
# 默认尺寸
fig = plot_timeseries(data, figsize=(16, 10))

# 自定义尺寸
fig = plot_timeseries(data, figsize=(20, 12))
```

---

## 📁 文件结构

```
examples/
├── basic_comparison.py          # 基本对比示例
├── co2_sensitivity.py          # CO2敏感性分析
├── test_visualization.py       # 字体测试脚本
├── README_VISUALIZATION.md     # 详细文档
├── UPDATE_SUMMARY.md           # 更新总结
├── QUICK_START.md             # 本文件
└── figures/                    # 所有图表输出
    ├── pet_timeseries.png
    ├── pet_boxplot.png
    ├── pet_correlation.png
    ├── pet_differences.png
    ├── co2_sensitivity_enhanced.png
    ├── co2_relative_change.png
    └── font_test.png
```

---

## 🔧 故障排除

### 中文显示为方块？
**原因**: 系统缺少中文字体  
**解决**: Windows系统通常已安装，重启Python环境

### 图片未生成？
**原因**: 没有写入权限  
**解决**: 
```bash
# 手动创建目录
mkdir figures
```

### 内存不足？
**原因**: 数据量太大  
**解决**: 减少数据点
```python
data = generate_synthetic_data(n_days=180)  # 减少到180天
```

---

## 💡 提示

1. **高分辨率**: 所有图表默认300 DPI，适合出版
2. **批量生成**: 运行脚本即可生成所有图表
3. **版本控制**: 建议将 `figures/` 目录加入 `.gitignore`
4. **格式转换**: 如需PDF格式，修改保存路径后缀为 `.pdf`

---

## 📚 更多信息

- **详细文档**: `README_VISUALIZATION.md`
- **更新日志**: `UPDATE_SUMMARY.md`
- **API文档**: `../docs/API_REFERENCE.md`
- **科学背景**: `../docs/SCIENTIFIC_BACKGROUND.md`

---

## ✨ 示例输出

运行 `basic_comparison.py` 后:

```
======================================================================
生成可视化图表 (GENERATING VISUALIZATIONS)
======================================================================

1. 时间序列对比 (Time series comparison)...
   已保存: figures/pet_timeseries.png

2. 箱线图对比 (Box plot comparison)...
   已保存: figures/pet_boxplot.png

3. 相关性矩阵 (Correlation matrix)...
   已保存: figures/pet_correlation.png

4. 差异热图 (Differences heatmap)...
   已保存: figures/pet_differences.png

======================================================================
Analysis complete!
======================================================================
```

---

## 🎨 配色方案

- **时间序列**: tab20 (20种颜色，清晰区分)
- **箱线图**: Set3 (柔和色彩)
- **相关性**: RdYlGn (红-黄-绿，直观)
- **差异**: YlOrRd (黄-橙-红，强调大小)

---

**版本**: 1.0  
**日期**: 2025-11-06  
**状态**: ✅ 已完成并测试
