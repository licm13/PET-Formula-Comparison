"""
最终验证脚本 - 检查所有更新是否成功
Final Validation Script - Check all updates
"""

import os
from pathlib import Path
from pet_comparison.analysis.visualization import setup_chinese_font
import matplotlib.pyplot as plt

print("=" * 70)
print("PET-Formula-Comparison 可视化更新验证")
print("Visualization Updates Validation")
print("=" * 70)
print()

# 1. 检查中文字体
print("1. 检查中文字体 (Checking Chinese Font)...")
font_name = setup_chinese_font()
if font_name:
    print(f"   ✓ 成功: {font_name}")
else:
    print("   ⚠ 警告: 未找到中文字体，使用默认字体")
print()

# 2. 检查输出目录
print("2. 检查输出目录 (Checking Output Directory)...")
figures_dir = Path(__file__).parent / 'figures'
if figures_dir.exists():
    print(f"   ✓ 目录存在: {figures_dir}")
else:
    print(f"   ✗ 目录不存在: {figures_dir}")
print()

# 3. 检查生成的图表文件
print("3. 检查生成的图表 (Checking Generated Figures)...")
expected_files = [
    'pet_timeseries.png',
    'pet_boxplot.png', 
    'pet_correlation.png',
    'pet_differences.png',
    'co2_sensitivity_enhanced.png',
    'co2_relative_change.png',
    'font_test.png'
]

found_files = []
missing_files = []

for filename in expected_files:
    filepath = figures_dir / filename
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"   ✓ {filename:35s} ({size_kb:>7.1f} KB)")
        found_files.append(filename)
    else:
        print(f"   ✗ {filename:35s} (未找到)")
        missing_files.append(filename)
print()

# 4. 检查脚本文件
print("4. 检查脚本文件 (Checking Script Files)...")
script_files = [
    'basic_comparison.py',
    'co2_sensitivity.py',
    'test_visualization.py'
]

for filename in script_files:
    filepath = Path(__file__).parent / filename
    if filepath.exists():
        print(f"   ✓ {filename}")
    else:
        print(f"   ✗ {filename} (未找到)")
print()

# 5. 检查文档文件
print("5. 检查文档文件 (Checking Documentation)...")
doc_files = [
    'README_VISUALIZATION.md',
    'UPDATE_SUMMARY.md',
    'QUICK_START.md'
]

for filename in doc_files:
    filepath = Path(__file__).parent / filename
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"   ✓ {filename:30s} ({size_kb:>5.1f} KB)")
    else:
        print(f"   ✗ {filename} (未找到)")
print()

# 6. 检查模块更新
print("6. 检查模块更新 (Checking Module Updates)...")
try:
    from pet_comparison.analysis.visualization import (
        plot_timeseries,
        plot_box_comparison,
        plot_correlation_matrix,
        plot_differences_heatmap
    )
    print("   ✓ 所有可视化函数可用")
    
    # 检查函数签名是否包含 save_path 参数
    import inspect
    sig = inspect.signature(plot_timeseries)
    if 'save_path' in sig.parameters:
        print("   ✓ 函数支持 save_path 参数")
    else:
        print("   ⚠ 函数可能未更新")
except ImportError as e:
    print(f"   ✗ 导入错误: {e}")
print()

# 7. 总结
print("=" * 70)
print("验证总结 (Validation Summary)")
print("=" * 70)
print(f"中文字体: {'✓ 可用' if font_name else '⚠ 不可用'}")
print(f"输出目录: {'✓ 存在' if figures_dir.exists() else '✗ 缺失'}")
print(f"生成图表: {len(found_files)}/{len(expected_files)} 个文件")
print(f"缺失图表: {len(missing_files)} 个")

if missing_files:
    print(f"\n缺失的文件:")
    for f in missing_files:
        print(f"  - {f}")
    print("\n建议: 运行以下命令生成缺失的图表:")
    if 'font_test.png' in missing_files:
        print("  python test_visualization.py")
    if any(f.startswith('pet_') for f in missing_files):
        print("  python basic_comparison.py")
    if any(f.startswith('co2_') for f in missing_files):
        print("  python co2_sensitivity.py")

print()

# 8. 状态判断
all_critical_present = all(
    f in found_files for f in [
        'pet_timeseries.png',
        'pet_boxplot.png',
        'pet_correlation.png',
        'pet_differences.png'
    ]
)

if all_critical_present and font_name:
    print("🎉 状态: 所有核心功能正常工作！")
    print("   Status: All core features working!")
elif all_critical_present:
    print("⚠️  状态: 核心功能正常，但中文字体可能有问题")
    print("   Status: Core features OK, but Chinese font may have issues")
else:
    print("❌ 状态: 部分功能未完成，请检查上述缺失项")
    print("   Status: Some features incomplete, please check missing items")

print()
print("=" * 70)
print("验证完成 (Validation Complete)")
print("=" * 70)
