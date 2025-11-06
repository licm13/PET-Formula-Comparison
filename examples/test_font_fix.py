"""
测试脚本 - 验证字体和图表生成
Test Script - Verify Font and Chart Generation
"""

import matplotlib.pyplot as plt
import matplotlib
from pet_comparison.analysis.visualization import setup_chinese_font
import numpy as np
from pathlib import Path

print("=" * 70)
print("Font and Visualization Test")
print("=" * 70)
print()

# 1. 测试字体配置
print("1. Testing font configuration...")
font_name = setup_chinese_font(force=True)
print(f"   Font configured: {font_name}")
print(f"   matplotlib font.sans-serif: {matplotlib.rcParams['font.sans-serif']}")
print(f"   matplotlib font.family: {matplotlib.rcParams['font.family']}")
print(f"   matplotlib axes.unicode_minus: {matplotlib.rcParams['axes.unicode_minus']}")
print()

# 2. 生成测试图表
print("2. Generating test charts...")
output_dir = Path(__file__).parent / 'figures'
output_dir.mkdir(exist_ok=True)

# 测试1: 简单文本
fig, ax = plt.subplots(figsize=(10, 6))
x = np.linspace(0, 10, 100)
y = np.sin(x)

ax.plot(x, y, 'b-', linewidth=2, label='Sine Wave')
ax.set_xlabel('X-axis', fontsize=12, fontweight='bold')
ax.set_ylabel('Y-axis', fontsize=12, fontweight='bold')
ax.set_title('Font Test - English Only', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

save_path = output_dir / 'test_english.png'
plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"   ✓ Saved: {save_path}")
plt.close()

# 测试2: CO2标签测试
fig, ax = plt.subplots(figsize=(10, 6))
co2_values = [280, 350, 380, 450, 550, 700]
pet_values = [5.2, 5.15, 5.1, 5.0, 4.85, 4.6]

ax.plot(co2_values, pet_values, 'ro-', linewidth=2, markersize=8)
ax.axvline(x=380, color='red', linestyle='--', alpha=0.6, label='Reference')
ax.set_xlabel('CO2 Concentration (ppm)', fontsize=12, fontweight='bold')
ax.set_ylabel('PET (mm/day)', fontsize=12, fontweight='bold')
ax.set_title('CO2 Sensitivity Test', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

save_path = output_dir / 'test_co2.png'
plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"   ✓ Saved: {save_path}")
plt.close()

# 测试3: 复杂布局
fig = plt.figure(figsize=(12, 8))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# 子图1
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(x, np.sin(x), 'b-', linewidth=2)
ax1.set_title('Subplot 1: Sine', fontsize=11, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 子图2
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(x, np.cos(x), 'r-', linewidth=2)
ax2.set_title('Subplot 2: Cosine', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 子图3
ax3 = fig.add_subplot(gs[1, :])
ax3.plot(x, np.sin(x), 'b-', linewidth=2, label='Sin')
ax3.plot(x, np.cos(x), 'r-', linewidth=2, label='Cos')
ax3.set_xlabel('X-axis', fontsize=11, fontweight='bold')
ax3.set_ylabel('Y-axis', fontsize=11, fontweight='bold')
ax3.set_title('Subplot 3: Combined', fontsize=11, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

plt.suptitle('Multi-panel Layout Test', fontsize=14, fontweight='bold')

save_path = output_dir / 'test_layout.png'
plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"   ✓ Saved: {save_path}")
plt.close()

print()

# 3. 检查生成的文件
print("3. Checking generated files...")
test_files = ['test_english.png', 'test_co2.png', 'test_layout.png']
all_exist = True
for filename in test_files:
    filepath = output_dir / filename
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"   ✓ {filename:25s} ({size_kb:>6.1f} KB)")
    else:
        print(f"   ✗ {filename:25s} (Missing)")
        all_exist = False

print()

# 4. 总结
print("=" * 70)
print("Test Summary")
print("=" * 70)
print(f"Font system: {font_name if font_name else 'Default'}")
print(f"Test files: {'All generated ✓' if all_exist else 'Some missing ✗'}")
print(f"Status: {'SUCCESS' if all_exist and font_name else 'PARTIAL'}")
print()

print("Note: All text labels are in English to avoid font display issues.")
print("This ensures consistent display across different systems.")
print("=" * 70)
