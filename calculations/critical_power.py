import numpy as np

def _weighted_linreg(x, y, w):
    """Lineare Regression y = a*x + b mit Gewichten w (stabil, ohne sklearn)."""
    w = np.asarray(w, dtype=float)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    w /= w.sum()

    xw = np.average(x, weights=w)
    yw = np.average(y, weights=w)

    cov = np.average((x - xw) * (y - yw), weights=w)
    var = np.average((x - xw) ** 2, weights=w)

    a = cov / (var + 1e-12)
    b = yw - a * xw
    return a, b

def calc_critical_power(p20s, p5min, p12min, p1min=None, p3min=None):
    """
    Berechnet Critical Power (CP) und W′ basierend auf einer gewichteten Regression
    von Leistung vs. 1/Zeit (P = W′/t + CP).
    - robust gegen fehlende Werte (None)
    - CP ≤ längster bekannter Leistungswert (meist 12-min)
    - längere Dauern werden stärker gewichtet
    """

    # Eingabepunkte sammeln (Zeit in s, Leistung in W)
    raw_pts = [
        (20,  p20s),
        (60,  p1min),
        (180, p3min),
        (300, p5min),
        (720, p12min)
    ]

    # Nur gültige Punkte behalten
    pts = [(t, p) for (t, p) in raw_pts if p is not None and p > 0]

    # Mindestens 2 Punkte nötig
    if len(pts) < 2:
        cp_est = round(p5min * 0.90, 1)
        w_est  = round((p20s - cp_est) * 15, 1)
        return cp_est, w_est

    # Arrays
    t = np.array([t for t, _ in pts], dtype=float)
    P = np.array([p for _, p in pts], dtype=float)

    # Gewichtung: längere Zeiten wichtiger
    w = (t / t.max()) ** 1.5

    inv_t = 1.0 / t
    X = np.vstack([inv_t, np.ones_like(inv_t)]).T
    W = np.diag(w)

    # Weighted Least Squares Regression: P = a*(1/t) + b
    beta = np.linalg.pinv(X.T @ W @ X) @ (X.T @ W @ P)
    a, b = beta[0], beta[1]   # W′, CP

    cp = float(b)
    wp = float(a)

    # Plausibilitäts-Check: CP nicht über längster Leistungswert
    P_longest = P[t.argmax()]  # meist 12-min Leistung
    if cp > P_longest:
        cp = P_longest
    if cp < 0:
        cp = 0.0
    if wp < 0:
        wp = 0.0

    return round(cp, 1), round(wp, 1)



def corrected_ftp(cp: float, vlamax: float) -> float:
    """
    Empfohlener FTP (für TrainingPeaks) abhängig von VLamax.
    Mildere Skalierung, damit der Einfluss nicht „zu stark“ wirkt.
    """
    if vlamax <= 0.30:
        factor = 1.00
    elif vlamax <= 0.50:
        factor = 0.99
    elif vlamax <= 0.70:
        factor = 0.97
    else:
        factor = 0.95
    return round(cp * factor, 1)
