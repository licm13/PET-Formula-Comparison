# 可视化增强说明 (Visualization Enhancements)

## 更新内容 (Updates)

本次更新对所有示例脚本进行了重大改进，增强了可视化效果并添加了完整的中文支持。

### 主要改进 (Main Improvements)

#### 1. 统一输出目录 (Unified Output Directory)
- **新路径**: 所有图表现在统一保存到 `examples/figures/` 目录
- **自动创建**: 如果目录不存在，会自动创建
- **便于管理**: 所有可视化输出集中管理，方便查找和使用

#### 2. 中文字体支持 (Chinese Font Support)
- **自动检测**: 系统自动检测并使用Windows常用中文字体
- **优先顺序**:
  1. Microsoft YaHei (微软雅黑) - 推荐
  2. SimHei (黑体)
  3. SimSun (宋体)
  4. KaiTi (楷体)
  5. FangSong (仿宋)
- **双语标签**: 所有图表标签都包含中英文对照
- **负号修复**: 解决了matplotlib中文字体负号显示问题

#### 3. 增强的可视化复杂度 (Enhanced Visualization Complexity)

##### 时间序列图 (Time Series Plot)
**文件**: `pet_timeseries.png`

增强内容:
- 主时间序列图：多条线使用不同线型和颜色
- 月平均对比图：显示季节性模式
- 公式间极差图：展示不同公式之间的差异范围
- 布局：3行网格布局，更全面展示数据

##### 箱线图 (Box Plot)
**文件**: `pet_boxplot.png`

增强内容:
- 带凹口的箱线图，显示均值（红色菱形）
- 彩色填充，每个公式不同颜色
- 统计表格：包含均值、标准差、最小值、最大值
- 表格样式：带颜色的表头和交替行颜色

##### 相关性矩阵 (Correlation Matrix)
**文件**: `pet_correlation.png`

增强内容:
- 热图：使用RdYlGn配色方案，更直观
- 平均相关系数柱状图：显示每个公式与其他公式的平均相关性
- 参考线：标注高相关性阈值（0.9）
- 加粗的数值标注

##### 差异热图 (Differences Heatmap)
**文件**: `pet_differences.png`

增强内容:
- 主热图：显示配对差异矩阵
- 平均差异柱状图：显示每个公式与其他公式的平均差异
- 统计摘要文本框：包含最大/最小差异、平均差异、标准差
- 自动识别差异最大的公式对

##### CO2敏感性分析 (CO2 Sensitivity Analysis)
**文件**: `co2_sensitivity_enhanced.png`, `co2_relative_change.png`

增强内容:
- 多面板布局：6个单独公式图 + 1个综合对比图
- 置信区间：显示数值的变化范围
- 百分比变化标注：每个子图显示相对变化
- 参考线：标注基准CO2浓度（380 ppm）
- 绝对值与相对变化对比：双子图显示

## 使用方法 (Usage)

### 运行基本对比示例
```bash
cd examples
python basic_comparison.py
```

生成的图表：
- `figures/pet_timeseries.png` - 时间序列综合对比
- `figures/pet_boxplot.png` - 分布箱线图和统计表
- `figures/pet_correlation.png` - 相关性矩阵和相似度分析
- `figures/pet_differences.png` - 差异热图和统计摘要

### 运行CO2敏感性分析
```bash
cd examples
python co2_sensitivity.py
```

生成的图表：
- `figures/co2_sensitivity_enhanced.png` - CO2敏感性多面板分析
- `figures/co2_relative_change.png` - 绝对值和相对变化对比

## 技术细节 (Technical Details)

### 字体配置
```python
from pet_comparison.analysis.visualization import setup_chinese_font

# 自动设置中文字体
font_name = setup_chinese_font()
print(f"使用的字体: {font_name}")  # 输出: Microsoft YaHei
```

### 自定义保存路径
所有可视化函数现在支持 `save_path` 参数：
```python
from pathlib import Path

output_dir = Path("my_figures")
output_dir.mkdir(exist_ok=True)

fig = plot_timeseries(data, save_path=output_dir / "my_timeseries.png")
```

### 图表分辨率
所有图表默认保存为：
- **DPI**: 300 (高分辨率，适合出版)
- **格式**: PNG（支持透明背景）
- **背景**: 白色（`facecolor='white'`）
- **边距**: 紧凑布局（`bbox_inches='tight'`）

## 图表说明 (Chart Descriptions)

### 1. 时间序列图 (Time Series)
- **用途**: 观察PET值随时间的变化趋势
- **特点**: 包含日值、月平均、以及公式间差异范围
- **适用场景**: 长期趋势分析、季节性模式识别

### 2. 箱线图 (Box Plot)
- **用途**: 比较不同公式的分布特征
- **特点**: 显示中位数、四分位数、异常值
- **适用场景**: 统计分析、离群值检测

### 3. 相关性矩阵 (Correlation Matrix)
- **用途**: 分析公式间的相关性
- **特点**: 热图 + 平均相关系数柱状图
- **适用场景**: 公式相似度评估、冗余分析

### 4. 差异热图 (Differences Heatmap)
- **用途**: 量化公式间的差异大小
- **特点**: 包含统计摘要和差异排名
- **适用场景**: 公式选择、不确定性评估

### 5. CO2敏感性分析 (CO2 Sensitivity)
- **用途**: 评估不同公式对CO2变化的响应
- **特点**: 多面板展示、百分比变化标注
- **适用场景**: 气候变化影响评估、未来情景分析

## 配色方案 (Color Schemes)

- **时间序列**: tab20 (支持多条线区分)
- **箱线图**: Set3 (柔和、易区分)
- **相关性**: RdYlGn (红-黄-绿，直观显示相关强度)
- **差异热图**: YlOrRd (黄-橙-红，强调差异大小)

## 故障排除 (Troubleshooting)

### 中文显示为方块
如果中文显示不正常，请确保系统安装了中文字体。Windows系统通常已预装。

### 图片未生成
确保有写入权限：
```bash
# Windows PowerShell
New-Item -ItemType Directory -Force -Path "examples\figures"
```

### 内存不足
如果处理大数据集时内存不足，可以减少数据点或分批处理：
```python
# 减少时间步长
data = generate_synthetic_data(n_days=180)  # 从365减少到180
```

## 后续改进计划 (Future Improvements)

- [ ] 添加交互式图表（使用Plotly）
- [ ] 支持导出为矢量格式（SVG, PDF）
- [ ] 添加更多统计图表类型
- [ ] 支持自定义配色方案
- [ ] 添加动画支持（时间序列动画）

## 参考文献 (References)

- Matplotlib中文字体配置: https://matplotlib.org/stable/tutorials/text/text_props.html
- Seaborn可视化指南: https://seaborn.pydata.org/tutorial.html
- 科学可视化最佳实践: https://github.com/rougier/scientific-visualization-book

---

**版本**: 1.0  
**更新日期**: 2025-11-06  
**作者**: PET-Formula-Comparison Team
