import numpy as np

def calc_critical_power(p1min, p3min, p5min, p12min, eps: float = 1.0):
    """
    Coaching-stabile CP/W′-Berechnung (monoton):
    - CP steigt, wenn 3/5 steigen (oder bleibt am Cap)
    - CP niemals > 12min - eps
    - 1min fließt NICHT in CP, nur in W′

    Idee:
    1) CP wird als aerober Anker aus (12,5,3) gemittelt (monoton),
       dann hart gecappt auf <= P12 - eps.
    2) W′ wird danach bei fixem CP per Least Squares aus 3/5/12 geschätzt,
       plus optional 1min als zusätzlicher W′-Anker.
    """

    # --- Eingaben bereinigen ---
    P12 = float(p12min) if (p12min is not None and float(p12min) > 0) else None
    P5  = float(p5min)  if (p5min  is not None and float(p5min)  > 0) else None
    P3  = float(p3min)  if (p3min  is not None and float(p3min)  > 0) else None
    P1  = float(p1min)  if (p1min  is not None and float(p1min)  > 0) else None

    # Mindestens 2 Punkte für irgendwas Sinnvolles
    pts_available = [x for x in [P3, P5, P12] if x is not None]
    if len(pts_available) < 2:
        return 0.0, 0.0

    # --- 1) CP als monotoner aerober Anker ---
    # Gewichtung: 12min dominiert, 5min unterstützt, 3min minimal (damit CP mit 3/5 steigen kann, aber nicht überreagiert)
    w12, w5, w3 = 0.75, 0.20, 0.05

    num = 0.0
    den = 0.0
    if P12 is not None:
        num += w12 * P12
        den += w12
    if P5 is not None:
        num += w5 * P5
        den += w5
    if P3 is not None:
        num += w3 * P3
        den += w3

    cp = num / den if den > 0 else 0.0

    # Hard cap: CP darf nie über 12min liegen
    if P12 is not None:
        cp = min(cp, P12 - float(eps))

    cp = max(0.0, float(cp))

    # --- 2) W′ bei fixem CP schätzen (3/5/12), ohne CP zu verändern ---
    pts = []
    if P3 is not None:  pts.append((180.0, P3))
    if P5 is not None:  pts.append((300.0, P5))
    if P12 is not None: pts.append((720.0, P12))

    t = np.array([t for t, _ in pts], dtype=float)
    P = np.array([p for _, p in pts], dtype=float)

    inv_t = 1.0 / t
    den_wp = float(np.sum(inv_t ** 2))
    wp = 0.0
    if den_wp > 0:
        wp = float(np.sum((P - cp) * inv_t) / den_wp)
    wp = max(0.0, wp)

    # --- 3) 1min nur als W′-Anker (optional) ---
    if P1 is not None:
        wp_1 = (P1 - cp) * 60.0
        if wp_1 > 0:
            wp = 0.7 * wp + 0.3 * wp_1

    return round(cp, 1), round(wp, 1)


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
