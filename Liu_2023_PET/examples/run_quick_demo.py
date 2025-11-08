import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ep_veg import (
    ep_pm_rc, ep_yang, ep_veg,
    estimate_g1, estimate_Aww,
    budyko_runoff, auto_configure_chinese_fonts
)

# 自动配置中文字体（若可用）
used_font = auto_configure_chinese_fonts()
print(f"[Font] Using: {used_font}")

np.random.seed(42)
N = 365

# 随机合成数据（范围参照 FAO-56/常识）
T = np.random.uniform(5, 30, size=N)             # °C
Rn = np.random.uniform(5, 20, size=N)            # MJ m^-2 d^-1
U2 = np.random.uniform(0.5, 3.5, size=N)         # m s^-1
VPD = np.random.uniform(0.3, 3.0, size=N)        # kPa
LAI = np.random.uniform(1.0, 6.0, size=N)        # –
Ca = np.random.uniform(380, 700, size=N)         # ppm
P = np.random.gamma(shape=1.2, scale=3.0, size=N)  # mm d^-1

# g1 取多年均值近似，用 T 的正温均值 + MI=1.0 估计（仅示例，可替换为更严格算法）
T_mean_above0 = np.maximum(T, 0).mean()
g1 = estimate_g1(T_C_mean_above0=T_mean_above0, MI=1.0, log_base="ln")

# Aww 使用固定 7.5% 斜率（也可传 species="tree"/"grass"/"shrub"）
# OPTIMIZED: Vectorized calculation instead of list comprehension
Aww = np.vectorize(estimate_Aww)(Ca)

# 计算三种 EP
# OPTIMIZED: These functions support vectorization via NumPy broadcasting
# Functions accept scalar or array inputs and return matching outputs
EP_pm = np.vectorize(ep_pm_rc)(T, Rn, U2, VPD)
EP_y = np.vectorize(ep_yang)(T, Rn, U2, VPD, Ca)
EP_v = np.vectorize(lambda t, rn, u2, v, lai, ca, aw: ep_veg(t, rn, u2, v, lai, ca, Aww_μmol_m2_s=aw, g1_kPa05=g1))(
    T, Rn, U2, VPD, LAI, Ca, Aww
)

# Budyko 径流（仅演示）
# OPTIMIZED: Vectorized calculation
Q_pm = np.vectorize(budyko_runoff)(P, EP_pm)
Q_y = np.vectorize(budyko_runoff)(P, EP_y)
Q_v = np.vectorize(budyko_runoff)(P, EP_v)

# 保存数据
import os
os.makedirs("../figures", exist_ok=True)
df = pd.DataFrame({
    "T_C": T, "Rn_MJ_m2_d": Rn, "U2_m_s": U2, "VPD_kPa": VPD, "LAI": LAI, "Ca_ppm": Ca, "P_mm_d": P,
    "EP_PM_RC": EP_pm, "EP_Yang": EP_y, "EP_Veg": EP_v,
    "Q_PM_RC": Q_pm, "Q_Yang": Q_y, "Q_Veg": Q_v,
})
df.to_csv("../figures/synthetic_daily_dataset.csv", index=False, encoding="utf-8")

# 绘图（遵循规则：不指定颜色且每图单独绘制）
plt.figure(figsize=(10,4.5))
plt.plot(EP_pm, label="EP_PM_RC")
plt.plot(EP_y, label="EP_Yang")
plt.plot(EP_v, label="EP_Veg")
plt.title("三种潜在蒸散模型对比 | Comparison of EP models")
plt.xlabel("Day")
plt.ylabel("EP (mm d$^{-1}$)")
plt.legend()
plt.tight_layout()
plt.savefig("../figures/ep_models_timeseries.png", dpi=200)
plt.close()

plt.figure(figsize=(10,4.5))
plt.plot(Q_pm, label="Q_PM_RC")
plt.plot(Q_y, label="Q_Yang")
plt.plot(Q_v, label="Q_Veg")
plt.title("Budyko 径流对比 | Budyko Runoff Comparison")
plt.xlabel("Day")
plt.ylabel("Runoff (mm d$^{-1}$)")
plt.legend()
plt.tight_layout()
plt.savefig("../figures/runoff_timeseries.png", dpi=200)
plt.close()

print("Done. Figures & dataset saved to ../figures/")
