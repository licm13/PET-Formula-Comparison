
"""
Synthetic data generator to emulate multi-process evaluation.

中文：本模块生成“类物理”的随机数据，包括若干流域、经纬度/气象序列、
并基于 Budyko 关系合成 AET 和简化水量平衡生成 Q。
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from .radiation import Ra_extraterrestrial
from .formulas import compute_daily_pet
from .budyko import budyko_phi

@dataclass
class Catchment:
    id: str
    lat: float
    lon: float
    elev_km: float

def random_catchments(N=20, seed=42):
    rng = np.random.default_rng(seed)
    lats = rng.uniform(-45, 60, size=N)    # avoid extreme polar for simplicity
    lons = rng.uniform(-120, 120, size=N)
    elev = rng.uniform(0.0, 2.0, size=N)
    return [Catchment(f"C{i:03d}", float(lats[i]), float(lons[i]), float(elev[i])) for i in range(N)]

def random_meteo(T=730, seed=123):
    """Generate daily Tmean/Tmax/Tmin and P (mm)."""
    rng = np.random.default_rng(seed)
    t = np.arange(T)
    # seasonal signal
    base = 15 + 10*np.sin(2*np.pi*t/365.0)
    noise = rng.normal(0, 3.0, size=T)
    Tmean = base + noise
    dT = rng.uniform(6, 14, size=T)
    Tmax = Tmean + dT/2
    Tmin = Tmean - dT/2
    # precipitation: intermittent
    P = rng.gamma(shape=0.6, scale=4.0, size=T)
    mask = rng.random(T) < 0.35
    P = P * mask
    return pd.DataFrame({"Tmean":Tmean, "Tmax":Tmax, "Tmin":Tmin, "P":P})

def make_pet_series(catchment: Catchment, met_df: pd.DataFrame, formula: str):
    """
    Compute daily PET for a catchment using a given formula.
    OPTIMIZED: Vectorized calculation instead of itertuples loop
    """
    doy = np.tile(np.arange(1, 366), int(np.ceil(len(met_df)/365)))[:len(met_df)]

    # Extract arrays once instead of iterating
    tmean = met_df['Tmean'].values
    tmax = met_df['Tmax'].values
    tmin = met_df['Tmin'].values

    # Vectorized computation using np.vectorize for compatibility
    # This is more efficient than explicit Python loops
    def _daily_pet_calculator(d, tm, tx, tn):
        return compute_daily_pet(formula, catchment.lat, int(d), tm, tx, tn)
    compute_pet_vectorized = np.vectorize(_daily_pet_calculator)

    return compute_pet_vectorized(doy, tmean, tmax, tmin)

def synthesize_observations(P: np.ndarray, PET_true: np.ndarray, rng):
    """Create pseudo-observations for PET/AET/Q."""
    # PET_obs = PET_true + noise (multiplicative)
    PET_obs = PET_true * rng.normal(1.0, 0.1, size=len(PET_true))
    PET_obs = PET_obs.clip(min=0.0)
    # AET via Budyko with random "ecosystem parameter" through PET/P
    P_clip = P + 1e-6
    phi = budyko_phi(PET_true / P_clip)
    AET_true = phi * P_clip
    AET_obs = AET_true * rng.normal(1.0, 0.1, size=len(P_true:=P_clip))
    AET_obs = AET_obs.clip(min=0.0)
    # Streamflow as residual with noise (very simplified water balance)
    Q_true = (P_clip - AET_true).clip(min=0.0)
    Q_obs = Q_true * rng.normal(1.0, 0.15, size=len(Q_true))
    Q_obs = Q_obs.clip(min=0.0)
    return PET_obs, AET_obs, Q_obs
