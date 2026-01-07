import streamlit as st
st.sidebar.warning("DEBUG: critical_power.py NEW LOADED")


import numpy as np

def _best_wp_for_cp(cp: float, t: np.ndarray, P: np.ndarray) -> float:
    """Least-squares W' für gegebenes CP im Modell P = CP + W'/t, W' >= 0."""
    inv_t = 1.0 / t
    den = float(np.sum(inv_t ** 2))
    if den <= 0:
        return 0.0
    num = float(np.sum((P - cp) * inv_t))
    return max(0.0, num / den)

def calc_critical_power(p1min, p3min, p5min, p12min, eps: float = 1.0):
    """
    Bereinigte CP/W' Berechnung:
    - CP-Fit NUR aus 3/5/12min (1min fließt NICHT in CP)
    - CP-Cap: CP <= p12min - eps
    - 1min wird optional nur zur W'-Schätzung verwendet
    """

    # --- CP-Punkte: nur >= 3min ---
    raw = [(180, p3min), (300, p5min), (720, p12min)]
    pts = [(t, float(p)) for t, p in raw if p is not None and float(p) > 0]

    if len(pts) < 2:
        # Fallback ohne 1min für CP
        if p12min and p12min > 0:
            cp = min(0.98 * float(p12min), float(p12min) - eps)
        elif p5min and p5min > 0:
            cp = 0.90 * float(p5min)
        elif p3min and p3min > 0:
            cp = 0.85 * float(p3min)
        else:
            return 0.0, 0.0

        cp = max(0.0, cp)

        # W' primär aus 1min (wenn da), sonst aus 3min
        if p1min and p1min > 0:
            wp = max(0.0, (float(p1min) - cp) * 60.0)
        elif p3min and p3min > 0:
            wp = max(0.0, (float(p3min) - cp) * 180.0)
        else:
            wp = 0.0

        return round(cp, 1), round(wp, 1)

    t = np.array([t for t, _ in pts], dtype=float)
    P = np.array([p for _, p in pts], dtype=float)

    # CP Cap aus 12min (wenn vorhanden), sonst aus max(P)
    p_long = float(p12min) if (p12min is not None and float(p12min) > 0) else float(np.max(P))
    cp_max = max(0.0, p_long - float(eps))

    # 1D-Grid-Search nach CP in [0, cp_max] (robust & deterministisch)
    grid = np.linspace(0.0, cp_max, 601)

    best_cp, best_wp, best_sse = 0.0, 0.0, float("inf")
    for cp in grid:
        wp = _best_wp_for_cp(float(cp), t, P)
        pred = float(cp) + wp / t
        sse = float(np.sum((P - pred) ** 2))
        if sse < best_sse:
            best_sse, best_cp, best_wp = sse, float(cp), float(wp)

    cp = max(0.0, best_cp)
    wp = max(0.0, best_wp)

    # 1min NUR für W' als Zusatzanker (ohne CP zu ändern)
    if p1min is not None and float(p1min) > 0:
        wp_1 = (float(p1min) - cp) * 60.0
        if wp_1 > 0:
            wp = 0.7 * wp + 0.3 * wp_1

    # Sicherheit: niemals über 12min
    if p12min is not None and float(p12min) > 0:
        cp = min(cp, float(p12min) - float(eps))

    return round(cp, 1), round(wp, 1)


def corrected_ftp(cp: float, vlamax: float = None) -> float:
    """
    Wie bei dir: FTP stark VLamax-abhängig.
    """
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
