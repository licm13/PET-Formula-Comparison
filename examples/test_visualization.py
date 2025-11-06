"""
快速测试脚本 - 验证中文字体和增强可视化
Quick Test Script - Verify Chinese Font and Enhanced Visualizations
"""

import matplotlib.pyplot as plt
from pet_comparison.analysis.visualization import setup_chinese_font
import numpy as np

# 设置中文字体
font_name = setup_chinese_font()
print(f"\n{'='*60}")
print(f"检测到的中文字体 (Detected Chinese Font): {font_name}")
print(f"{'='*60}\n")

# 创建简单的测试图
fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

ax.plot(x, y1, label='正弦波 (Sine)', linewidth=2, color='blue')
ax.plot(x, y2, label='余弦波 (Cosine)', linewidth=2, color='red')

ax.set_xlabel('时间 (Time)', fontsize=12, fontweight='bold')
ax.set_ylabel('振幅 (Amplitude)', fontsize=12, fontweight='bold')
ax.set_title('中文字体测试 (Chinese Font Test)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# 保存测试图
from pathlib import Path
output_dir = Path(__file__).parent / 'figures'
output_dir.mkdir(exist_ok=True)

save_path = output_dir / 'font_test.png'
plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"✓ 测试图已保存到 (Test figure saved to): {save_path}")

plt.close()

print(f"\n{'='*60}")
print("测试完成！(Test completed!)")
print(f"{'='*60}\n")

# 显示所有可用的中文字体
print("系统中所有可用的中文字体 (Available Chinese fonts):")
import matplotlib.font_manager as fm

chinese_fonts = []
for font in fm.fontManager.ttflist:
    if any(chinese_name in font.name for chinese_name in 
           ['YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong', 'Microsoft', 'Sim', 'Kai']):
        chinese_fonts.append(font.name)

if chinese_fonts:
    for i, font in enumerate(set(chinese_fonts), 1):
        print(f"  {i}. {font}")
else:
    print("  未找到中文字体 (No Chinese fonts found)")

print()
