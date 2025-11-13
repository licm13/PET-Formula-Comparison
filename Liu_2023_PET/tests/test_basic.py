import sys
import os
import math

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ep_veg import ep_pm_rc, ep_yang, ep_veg
from ep_veg import estimate_g1, estimate_Aww

def test_basic_runs():
    T=20; Rn=15; U2=2; VPD=1.5; LAI=3.0; Ca=420
    g1 = estimate_g1(T_C_mean_above0=15.0, MI=1.0, log_base="ln")
    Aww = estimate_Aww(Ca_ppm=Ca)
    eto = ep_pm_rc(T, Rn, U2, VPD)
    epy = ep_yang(T, Rn, U2, VPD, Ca_ppm=Ca)
    epv = ep_veg(T, Rn, U2, VPD, LAI, Ca, Aww_μmol_m2_s=Aww, g1_kPa05=g1)
    assert eto > 0 and epy > 0 and epv > 0
