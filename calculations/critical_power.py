
# calculations/critical_power.py
import numpy as np

def calc_critical_power(p20s=None, p1min=None, p3min=None, p5min=None, p12min=None):
    data = []
    if p20s is not None: data.append((20.0, float(p20s)))
    if p1min is not None: data.append((60.0, float(p1min)))
    if p3min is not None: data.append((180.0, float(p3min)))
    if p5min is not None: data.append((300.0, float(p5min)))
    if p12min is not None: data.append((720.0, float(p12min)))
    if len(data) < 2:
        raise ValueError("Mindestens zwei Leistungswerte erforderlich (z. B. 5min & 12min).")
    t = np.array([d[0] for d in data], dtype=float)
    p = np.array([d[1] for d in data], dtype=float)
    inv_t = 1.0 / t
    A = np.vstack([np.ones_like(inv_t), inv_t]).T
    coeffs, *_ = np.linalg.lstsq(A, p, rcond=None)
    cp, w_prime = float(coeffs[0]), float(coeffs[1])
    return round(cp, 1), round(w_prime, 1)
