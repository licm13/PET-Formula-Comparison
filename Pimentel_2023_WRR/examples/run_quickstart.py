
"""
Quickstart script / 快速演示脚本

运行：python examples/run_quickstart.py
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from petlab.analysis import run_pipeline
from petlab.plotting import setup_fonts, savefig
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

outdir = Path("outputs")
outdir.mkdir(parents=True, exist_ok=True)

df = run_pipeline(Ncatch=20, T=730)
df.to_csv(outdir / "scores.csv", index=False, encoding="utf-8-sig")

# 简易散点图示：每个流域的三变量RE（示范）
setup_fonts()
fig, ax = plt.subplots(figsize=(7,4.2))
subset = df.drop_duplicates(["catchment","formula"])
for f, g in subset.groupby("formula"):
    ax.scatter(g["RE_PET"], g["RE_Q"], s=36, alpha=0.7, label=f)
ax.axvline(0, color="k", lw=1, alpha=0.3)
ax.axhline(0, color="k", lw=1, alpha=0.3)
ax.set_xlabel("RE_PET (%)")
ax.set_ylabel("RE_Q (%)")
ax.set_title("Formula comparison (RE_PET vs RE_Q) / 三种公式对比")
ax.legend(fontsize=8)
savefig(outdir / "re_scatter.png")
plt.close(fig)

print("Quickstart finished. Outputs saved under outputs/.")
