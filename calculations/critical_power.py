import numpy as np

def calc_critical_power(p20s, p5min, p12min, p1min=None, p3min=None, vlamax=None):
    """
    Realistische CP-Berechnung (360 Coaching Lab)
    ------------------------------------------------
    - Gewichtete Regression (längere Intervalle stärker)
    - CP capped bei längster Power (12min)
    - W' aus Modell P = W′/t + CP
    - Optional: VLamax-Korrektur (senkt CP bei hoher, hebt leicht bei niedriger VLamax)
    """

    # Eingabepunkte sammeln (t [s], P [W])
    raw_pts = [
        (20, p20s),
        (60, p1min),
        (180, p3min),
        (300, p5min),
        (720, p12min)
    ]
    pts = [(t, p) for t, p in raw_pts if p is not None and p > 0]

    # Fallback, falls zu wenige Punkte vorhanden
    if len(pts) < 2:
        cp_est = round(p5min * 0.9, 1)
        w_est  = round((p20s - cp_est) * 15, 1)
        return cp_est, w_est

    t = np.array([t for t, _ in pts], dtype=float)
    P = np.array([p for _, p in pts], dtype=float)

    # Gewichtung: lange Intervalle zählen stärker (nahe am steady state)
    weights = (t / np.max(t)) ** 1.8

    # Regression: P = a*(1/t) + b
    inv_t = 1.0 / t
    X = np.vstack([inv_t, np.ones_like(inv_t)]).T
    W = np.diag(weights)

    beta = np.linalg.pinv(X.T @ W @ X) @ (X.T @ W @ P)
    a, b = beta[0], beta[1]

    cp = float(b)
    wp = float(a)

    # CP darf nie höher als längste Power (12min) sein
    cp = min(cp, np.max(P))

    # VLamax-Korrektur: beeinflusst Verhältnis aerobe/anaerobe Kapazität
    if vlamax is not None:
        if vlamax > 0.5:
            cp *= 1 - ((vlamax - 0.5) * 0.05)  # hohe VLamax -> leicht niedrigere CP (~2–3 %)
        elif vlamax < 0.3:
            cp *= 1 + ((0.3 - vlamax) * 0.03)  # niedrige VLamax -> leicht höhere CP

    # Keine negativen Werte
    cp = max(0, cp)
    wp = max(0, wp)

    return round(cp, 1), round(wp, 1)


def corrected_ftp(cp: float, vlamax: float = None) -> float:
    """
    FTP-Berechnung (Hybrid-Modell für Diagnostik & TrainingPeaks)
    -------------------------------------------------------------
    - basiert auf CP
    - berücksichtigt VLamax
    - liefert praxisnahe FTP-Werte für Trainingszonen
    """
    if vlamax is None:
        factor = 0.975  # Standardwert
    elif vlamax <= 0.30:
        factor = 0.99
    elif vlamax <= 0.50:
        factor = 0.975
    elif vlamax <= 0.70:
        factor = 0.95
    else:
        factor = 0.93

    ftp = cp * factor
    return round(ftp, 1)
