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

def calc_critical_power(p20s, p5min, p12min, p1min=None, p3min=None,
                        weight_scheme="t2", enforce_bounds=True):
    """
    Berechnet CP und W′ per gewichteter Regression: P = W′/t + CP.

    Punkte:
      - 20 s, (60 s), (180 s), 300 s, 720 s (optional je nachdem, was vorliegt)
    Gewichtung:
      - 'equal' : alle gleich
      - 't'     : Gewicht ∝ t
      - 't2'    : Gewicht ∝ t^2  (empfohlen; lange Dauer zählt stark)
    Schranken (falls enforce_bounds=True):
      - CP <= 0.99 * P12 (falls vorhanden)
      - CP <= 0.97 * P5  (falls vorhanden)
    """

    pts = [
        (20.0, p20s),
        (60.0, p1min) if p1min else None,
        (180.0, p3min) if p3min else None,
        (300.0, p5min),
        (720.0, p12min)
    ]
    pts = [(t, p) for (t, p) in pts if p is not None]

    # Fallback, falls zu wenig Daten:
    if len(pts) < 2:
        cp = round(p5min * 0.90, 1)
        w_prime = round(max(0.0, (p20s - cp)) * 15.0, 1)
        return cp, w_prime

    t = np.array([t for t, _ in pts], dtype=float)
    p = np.array([p for _, p in pts], dtype=float)
    x = 1.0 / t

    if weight_scheme == "equal":
        w = np.ones_like(t)
    elif weight_scheme == "t":
        w = t
    else:  # "t2" (default)
        w = t ** 2

    a, b = _weighted_linreg(x, p, w)
    cp_raw = float(b)
    w_prime_raw = float(a)

    # Schranken: CP darf nicht über langen MMPs liegen
    caps = []
    if p12min is not None:
        caps.append(0.99 * float(p12min))
    if p5min is not None:
        caps.append(0.97 * float(p5min))

    cp_capped = cp_raw
    if caps:
        cp_capped = min(cp_raw, min(caps))

    # Untere Schranke (sehr weich), damit CP nicht „abstürzt“
    if p12min is not None:
        cp_capped = max(0.60 * float(p12min), cp_capped)

    # Final runden
    cp = round(cp_capped, 1)
    w_prime = round(max(0.0, w_prime_raw), 1)

    return cp, w_prime


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
