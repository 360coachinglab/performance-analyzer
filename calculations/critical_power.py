import numpy as np

def _best_wprime_for_cp(cp, t, P):
    """
    Für festen CP ist das Modell linear in W':
    P ≈ W'/t + CP  ->  (P-CP) ≈ W'/t
    Least-Squares-Lösung für W' (>=0):
    W' = sum((P-CP)/t) / sum(1/t^2)
    """
    inv_t = 1.0 / t
    num = np.sum((P - cp) * inv_t)
    den = np.sum(inv_t ** 2)
    wp = num / den if den > 0 else 0.0
    return max(0.0, float(wp))

def calc_cp_and_wprime_capped(p1min=None, p3min=None, p5min=None, p12min=None, eps=1.0):
    """
    Bereinigt + capped:
    - CP nur aus 3/5/12min (1min NICHT für CP)
    - CP wird begrenzt: CP <= p12min - eps
    - W' aus (3/5/12)-Fit, optional mit 1min als W'-Anker (ohne CP zu ändern)
    """

    # CP-Punkte (>=3min)
    raw_pts = [(180, p3min), (300, p5min), (720, p12min)]
    pts = [(t, p) for t, p in raw_pts if p is not None and p > 0]

    if len(pts) < 2:
        # Fallback (ohne 1min für CP)
        if p12min and p12min > 0:
            cp = min(0.98 * p12min, p12min - eps)
        elif p5min and p5min > 0:
            cp = 0.90 * p5min
        elif p3min and p3min > 0:
            cp = 0.85 * p3min
        else:
            return 0.0, 0.0

        cp = max(0.0, float(cp))

        # W' primär aus 1min, sonst aus 3min
        if p1min and p1min > 0:
            wp = max(0.0, (float(p1min) - cp) * 60.0)
        elif p3min and p3min > 0:
            wp = max(0.0, (float(p3min) - cp) * 180.0)
        else:
            wp = 0.0

        return round(cp, 1), round(wp, 1)

    t = np.array([t for t, _ in pts], dtype=float)
    P = np.array([p for _, p in pts], dtype=float)

    # Cap-Grenze (wenn 12min vorhanden, sonst max(P))
    p_long = float(p12min) if (p12min is not None and p12min > 0) else float(np.max(P))
    cp_max = max(0.0, p_long - float(eps))

    # 1D-Suche nach CP in [0, cp_max] (robust, schnell)
    grid = np.linspace(0.0, cp_max, 501)

    best_cp = 0.0
    best_wp = 0.0
    best_sse = float("inf")

    for cp in grid:
        wp = _best_wprime_for_cp(cp, t, P)
        pred = wp / t + cp
        sse = float(np.sum((P - pred) ** 2))
        if sse < best_sse:
            best_sse = sse
            best_cp = float(cp)
            best_wp = float(wp)

    cp = max(0.0, best_cp)
    wp = max(0.0, best_wp)

    # 1min nur als W'-Anker (ohne CP anzufassen)
    if p1min is not None and p1min > 0:
        wp_1min = (float(p1min) - cp) * 60.0
        if wp_1min > 0:
            # Moderat beimischen, damit 1min nicht alles kapert
            wp = 0.7 * wp + 0.3 * wp_1min

    return round(cp, 1), round(wp, 1)
