import numpy as np

def calc_critical_power(p1min=None, p3min=None, p5min=None, p12min=None):
    """
    Klassische CP/W′ Schätzung (korrektes CP-Modell):
      P(t) = CP + W′/t

    - CP-Fit aus verfügbaren Punkten >= 3 min (3/5/12), wobei 3min und/oder 5min optional sind
    - mind. 2 Punkte notwendig (z.B. 12+3 oder 12+5 oder 3+5)
    - 1 min NICHT für CP, nur optional als W′-Anker
    """

    def _valid(x):
        return x is not None and float(x) > 0

    pts = []
    if _valid(p3min):   pts.append((180.0, float(p3min)))
    if _valid(p5min):   pts.append((300.0, float(p5min)))
    if _valid(p12min):  pts.append((720.0, float(p12min)))

    if len(pts) < 2:
        return 0.0, 0.0

    t = np.array([tt for tt, _ in pts], dtype=float)
    P = np.array([pp for _, pp in pts], dtype=float)

    # Regression: P = a*(1/t) + b  -> a=W′, b=CP
    inv_t = 1.0 / t
    X = np.vstack([inv_t, np.ones_like(inv_t)]).T
    a, b = np.linalg.lstsq(X, P, rcond=None)[0]

    wp = max(0.0, float(a))
    cp = max(0.0, float(b))

    # 1 min optional nur als W′-Anker (ohne CP zu verändern)
    if _valid(p1min):
        wp_1 = (float(p1min) - cp) * 60.0
        if wp_1 > 0:
            wp = 0.7 * wp + 0.3 * wp_1

    return round(cp, 1)
