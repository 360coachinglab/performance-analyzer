import numpy as np

def calc_critical_power(p1min=None, p3min=None, p5min=None, p12min=None):
    """
    Klassische CP/W′ Schätzung:
      P(t) = CP + W′/t

    - CP-Fit aus verfügbaren Punkten >= 3 min (3/5/12), 3min und/oder 5min optional
    - mind. 2 Punkte aus (3/5/12) für echte Regression
    - 1min NICHT für CP, nur optional als W′-Anker
    - Falls zu wenig CP-Punkte: Fallback CP aus 12min (damit App nicht crasht)
    """

    def valid(x):
        return x is not None and float(x) > 0

    P1  = float(p1min)  if valid(p1min)  else None
    P3  = float(p3min)  if valid(p3min)  else None
    P5  = float(p5min)  if valid(p5min)  else None
    P12 = float(p12min) if valid(p12min) else None

    # CP-Punkte (>=3min)
    pts = []
    if P3 is not None:  pts.append((180.0, P3))
    if P5 is not None:  pts.append((300.0, P5))
    if P12 is not None: pts.append((720.0, P12))

    # --- Wenn <2 CP-Punkte: stabiler Fallback (sonst cp=0 und App knallt) ---
    if len(pts) < 2:
        if P12 is None:
            return 0.0, 0.0  # wirklich nicht genug Daten

        # Fallback: CP aus 12min leicht konservativ
        cp = max(0.0, 0.98 * P12)

        # W′: wenn 1min da, nutze es; sonst 0
        wp = 0.0
        if P1 is not None:
            wp_1 = (P1 - cp) * 60.0
            if wp_1 > 0:
                wp = wp_1

        return round(cp, 1), round(max(0.0, wp), 1)

    # --- Klassischer Fit: P = a*(1/t) + b ---
    t = np.array([tt for tt, _ in pts], dtype=float)
    P = np.array([pp for _, pp in pts], dtype=float)

    inv_t = 1.0 / t
    X = np.vstack([inv_t, np.ones_like(inv_t)]).T
    a, b = np.linalg.lstsq(X, P, rcond=None)[0]

    wp = max(0.0, float(a))
    cp = max(0.0, float(b))

    # 1min nur als W′-Anker (ohne CP zu ändern)
    if P1 is not None:
        wp_1 = (P1 - cp) * 60.0
        if wp_1 > 0:
            wp = 0.7 * wp + 0.3 * wp_1

    return round(cp, 1), round(wp, 1)


def corrected_ftp(cp: float, vlamax: float = None) -> float:
    """
    FTP als praxisnahe 60-min-Leistung aus CP,
    abhängig von der anaeroben Prägung (VLamax).
    """

    if vlamax is None:
        factor = 0.97
    else:
        # Stützstellen: (VLamax, FTP/CP)
        anchors = [
            (0.30, 0.99),   # sehr diesel
            (0.45, 0.975),
            (0.60, 0.95),
            (0.75, 0.91),   # stark anaerob
            (0.90, 0.885),
            (1.10, 0.87),
        ]

        # Clamp
        v = max(anchors[0][0], min(anchors[-1][0], float(vlamax)))

        # Lineare Interpolation
        for (v0, f0), (v1, f1) in zip(anchors, anchors[1:]):
            if v0 <= v <= v1:
                t = (v - v0) / (v1 - v0)
                factor = f0 + t * (f1 - f0)
                break

    return round(cp * factor, 1)



#def corrected_ftp(cp: float, vlamax: float = None) -> float:
#    if vlamax is None:
#        factor = 0.97
#    elif vlamax <= 0.30:
#        factor = 0.99
#    elif vlamax <= 0.45:
#        factor = 0.975
#    elif vlamax <= 0.60:
#        factor = 0.95
#    elif vlamax <= 0.75:
#        factor = 0.93
#    else:
#        factor = 0.91
#    return round(cp * factor, 1)
