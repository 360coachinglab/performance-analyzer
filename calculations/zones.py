
# calculations/zones.py
import pandas as pd

def calc_zones(cp, hfmax, fatmax_w, vlamax):
    ga1_base = (0.55, 0.70)
    ga2_base = (0.70, 0.90)
    v = max(0.2, min(float(vlamax), 1.0))
    scale = (0.6 - v) / 0.4
    shift = 0.10 * scale
    def shift_band(band):
        lo, hi = band
        return (lo*(1+shift), hi*(1+shift))
    ga1_pct = shift_band(ga1_base)
    ga2_pct = shift_band(ga2_base)
    ga1_w = (ga1_pct[0]*cp, ga1_pct[1]*cp)
    ga2_w = (ga2_pct[0]*cp, ga2_pct[1]*cp)
    zones = [
        {"Zone": "GA1", "Leistung (W)": f"{ga1_w[0]:.0f}–{ga1_w[1]:.0f}", "Prozent CP": f"{ga1_pct[0]*100:.1f}%–{ga1_pct[1]*100:.1f}%"},
        {"Zone": "GA2", "Leistung (W)": f"{ga2_w[0]:.0f}–{ga2_w[1]:.0f}", "Prozent CP": f"{ga2_pct[0]*100:.1f}%–{ga2_pct[1]*100:.1f}%"}
    ]
    return pd.DataFrame(zones)

def calc_ga1_zone(fatmax_w, cp, vlamax):
    v = max(0.2, min(float(vlamax), 1.0))
    scale = (0.6 - v) / 0.4
    shift = 0.10 * scale
    lo_pct, hi_pct = 0.55*(1+shift), 0.70*(1+shift)
    return lo_pct*cp, hi_pct*cp, lo_pct*100, hi_pct*100
