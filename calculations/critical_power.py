import numpy as np

def calc_critical_power(p1min, p3min, p5min, p12min, eps: float = 1.0):
    """
    CP/W' aus 3/5/12 (1/t Modell), 1min nur für W'.
    Danach: CP hart gecappt auf <= P12 - eps.
    """

    # --- Inputs ---
    P1  = float(p1min)  if (p1min  is not None and float(p1min)  > 0) else None
    P3  = float(p3min)  if (p3min  is not None and float(p3min)  > 0) else None
    P5  = float(p5min)  if (p5min  is not None and float(p5min)  > 0) else None
    P12 = float(p12min) if (p12min is not None and float(p12min) > 0) else None

    pts = []
    if P3 is not None:  pts.append((180.0, P3))
    if P5 is not None:  pts.append((300.0, P5))
    if P12 is not None: pts.append((720.0, P12))

    if len(pts) < 2:
        return 0.0, 0.0

    t = np.array([t for t, _ in pts], dtype=float)
    P = np.array([p for _, p in pts], dtype=float)

    # --- Ungewichtete Regression: P = W'/t + CP ---
    inv_t = 1.0 / t
    X = np.vstack([inv_t, np.ones_like(inv_t)]).T
    beta = np.linalg.lstsq(X, P, rcond=None)[0]
    wp_raw, cp_raw = float(beta[0]), float(beta[1])

    cp = max(0.0, cp_raw)
    wp = max(0.0, wp_raw)

    # --- 1min nur als W'-Anker ---
    if P1 is not None:
        wp_1 = (P1 - cp) * 60.0
        if wp_1 > 0:
            wp = 0.7 * wp + 0.3 * wp_1

    # --- Hard cap: CP darf nie über 12min ---
    if P12 is not None:
        cap = P12 - float(eps)
        if cp > cap:
            cp = cap  # hier "klebt" CP dann bewusst an P12


import streamlit as st
st.sidebar.write({
    "DEBUG_p3": p3min, "DEBUG_p5": p5min, "DEBUG_p12": p12min,
    "DEBUG_cp": cp, "DEBUG_wp": wp if "wp" in locals() else None
})



    return round(cp, 1), round(max(0.0, wp), 1)



def corrected_ftp(cp: float, vlamax: float = None) -> float:
    if vlamax is None:
        factor = 0.97
    elif vlamax <= 0.30:
        factor = 0.99
    elif vlamax <= 0.45:
        factor = 0.975
    elif vlamax <= 0.60:
        factor = 0.95
    elif vlamax <= 0.75:
        factor = 0.93
    else:
        factor = 0.91
    return round(cp * factor, 1)

