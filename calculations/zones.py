
import pandas as pd

def _vlamax_shift(vlamax: float) -> float:
    v = max(0.2, min(float(vlamax), 1.0))
    return ((0.6 - v) / 0.4) * 0.05  # ±5%

def _apply_shift(band, shift):
    lo, hi = band
    return (lo*(1+shift), hi*(1+shift))

def _ensure_fatmax_inside_ga1(ga1_pct, fatmax_pct_cp, margin=0.02):
    lo, hi = ga1_pct
    if fatmax_pct_cp is None:
        return ga1_pct
    if fatmax_pct_cp < lo:
        lo = min(lo, max(0.45, fatmax_pct_cp - margin))
    if fatmax_pct_cp > hi:
        hi = max(hi, min(0.85, fatmax_pct_cp + margin))
    return (lo, hi)

def calc_zones(cp, hfmax, fatmax_w, vlamax):
    cp = float(cp)
    fatmax_pct_cp = None if cp <= 0 or fatmax_w is None else float(fatmax_w)/cp

    base = {
        "GA1": (0.60, 0.75),
        "GA2": (0.75, 0.90),
        "EB":  (0.90, 1.05),
        "SB":  (1.05, 1.20),
        "R":   (1.20, 1.50),
    }
    s = _vlamax_shift(vlamax)
    ga1 = _apply_shift(base["GA1"], s)
    ga1 = _ensure_fatmax_inside_ga1(ga1, fatmax_pct_cp)
    ga2 = _apply_shift(base["GA2"], s)
    eb  = _apply_shift(base["EB"],  s)
    sb  = _apply_shift(base["SB"],  s)
    r   = base["R"]

    ordered = [("GA1", ga1), ("GA2", ga2), ("EB", eb), ("SB", sb), ("R", r)]
    rows = []
    for name, (lo, hi) in ordered:
        lo_w = lo * cp; hi_w = hi * cp
        rows.append({"Zone": name, "Leistung (W)": f"{lo_w:.0f}–{hi_w:.0f}", "Prozent CP": f"{lo*100:.1f}%–{hi*100:.1f}%"})
    return pd.DataFrame(rows)

def calc_ga1_zone(fatmax_w, cp, vlamax):
    cp = float(cp)
    s = _vlamax_shift(vlamax)
    lo_pct, hi_pct = (0.60*(1+s), 0.75*(1+s))
    fatmax_pct_cp = None if cp <= 0 or fatmax_w is None else float(fatmax_w)/cp
    lo_pct, hi_pct = _ensure_fatmax_inside_ga1((lo_pct, hi_pct), fatmax_pct_cp)
    return lo_pct*cp, hi_pct*cp, lo_pct*100, hi_pct*100
