import numpy as np

def calc_critical_power(p1min, p3min, p5min, p12min):
    """
    Berechnet Critical Power (CP) und W′ basierend auf 1-, 3-, 5- und 12-min All-Out-Tests.
    - Regression nach Modell P = W′/t + CP
    - längere Intervalle werden stärker gewichtet
    - CP liegt immer unterhalb der längsten getesteten Leistung (12-min)
    """

    # Eingabepunkte (Zeit in s, Leistung in W)
    raw_pts = [
        (60,  p1min),
        (180, p3min),
        (300, p5min),
        (720, p12min)
    ]
    pts = [(t, p) for t, p in raw_pts if p is not None and p > 0]

    if len(pts) < 2:
        cp_est = round((p5min or 0) * 0.9, 1)
        w_est  = round(((p1min or 0) - cp_est) * 15, 1)
        return cp_est, w_est

    t = np.array([t for t, _ in pts], dtype=float)
    P = np.array([p for _, p in pts], dtype=float)

    # Gewichtung: längere Intervalle stärker (aerob relevanter)
    weights = (t / np.max(t)) ** 2.0

    inv_t = 1.0 / t
    X = np.vstack([inv_t, np.ones_like(inv_t)]).T
    W = np.diag(weights)

    # Regression: P = a*(1/t) + b
    beta = np.linalg.pinv(X.T @ W @ X) @ (X.T @ W @ P)
    a, b = beta[0], beta[1]

    cp = float(b)
    wp = float(a)

    # CP darf nie >= längster Testleistung (12min)
    P_long = float(P[t.argmax()])
    if cp >= P_long:
        cp = P_long - 1.0

    cp = max(0, cp)
    wp = max(0, wp)

    return round(cp, 1), round(wp, 1)


def corrected_ftp(cp: float, vlamax: float = None) -> float:
    """
    FTP-Berechnung (metabolisch modelliert)
    ---------------------------------------
    - basiert auf CP (aerob)
    - stark abhängig von VLamax (anaerob)
    - liefert Trainings-FTP für TrainingPeaks
    """

    if vlamax is None:
        factor = 0.97
    elif vlamax <= 0.30:
        factor = 0.99   # Dieseltyp
    elif vlamax <= 0.45:
        factor = 0.975  # Allrounder
    elif vlamax <= 0.60:
        factor = 0.95   # Mischtyp
    elif vlamax <= 0.75:
        factor = 0.93   # Sprinter
    else:
        factor = 0.91   # sehr anaerob

    ftp = cp * factor
    return round(ftp, 1)
