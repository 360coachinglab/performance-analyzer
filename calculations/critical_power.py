
# calculations/critical_power.py
# Option A: CP is derived ONLY from durations >= 3 minutes (3/5/12min if present).
# W′ is then estimated from short-duration efforts (20s peak and optional 1min).

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple


@dataclass
class CPResult:
    cp: float
    w_prime: float
    cp_method: str
    wprime_method: str


def _work_time_fit(long_points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Linear regression in Work-Time domain: Work = CP*t + W'. Returns (CP, W')."""
    t = [pt[0] for pt in long_points]
    w = [pt[0] * pt[1] for pt in long_points]  # Joules

    t_mean = sum(t) / len(t)
    w_mean = sum(w) / len(w)

    var_t = sum((ti - t_mean) ** 2 for ti in t)
    if var_t <= 0:
        cp = min(pt[1] for pt in long_points)
        w_prime = max(0.0, w_mean - cp * t_mean)
        return cp, w_prime

    cov_tw = sum((ti - t_mean) * (wi - w_mean) for ti, wi in zip(t, w))
    cp = cov_tw / var_t
    w_prime = w_mean - cp * t_mean
    return cp, w_prime


def _clamp_cp(cp: float, long_points: List[Tuple[float, float]]) -> float:
    min_p = min(p for _, p in long_points)
    avg_p = sum(p for _, p in long_points) / len(long_points)

    lo = 0.50 * min_p
    hi = min_p  # never above the weakest long point
    cp = max(lo, min(hi, cp))
    cp = min(cp, avg_p)
    return cp


def _estimate_wprime(cp: float,
                     p20s: Optional[float] = None,
                     p1min: Optional[float] = None) -> Tuple[float, str]:
    """Estimate W′ from short-duration points: max((P-CP)*t)."""
    candidates = []
    if p20s is not None and p20s > 0:
        candidates.append(((p20s - cp) * 20.0, "20s"))
    if p1min is not None and p1min > 0:
        candidates.append(((p1min - cp) * 60.0, "1min"))

    if not candidates:
        return 0.0, "none"

    wj, label = max(candidates, key=lambda x: x[0])
    return max(0.0, wj), f"max((P-CP)*t) from {label}"


def calc_critical_power(
    p5min: float,
    p12min: float,
    p20s: Optional[float] = None,
    p1min: Optional[float] = None,
    p3min: Optional[float] = None,
) -> tuple[float, float]:
    """Return (CP, W′).

    Option A:
    - CP from points >= 3 minutes (3/5/12min).
    - W′ from short points (20s peak, optional 1min): W′ = max((P-CP)*t).
    """
    long_points: List[Tuple[float, float]] = []
    if p3min is not None and p3min > 0:
        long_points.append((180.0, float(p3min)))
    if p5min is not None and p5min > 0:
        long_points.append((300.0, float(p5min)))
    if p12min is not None and p12min > 0:
        long_points.append((720.0, float(p12min)))

    if len(long_points) >= 2:
        cp_raw, _wprime_fit = _work_time_fit(long_points)
        cp = _clamp_cp(cp_raw, long_points)
    else:
        if p12min is not None and p12min > 0:
            cp = 0.95 * float(p12min)
        elif p5min is not None and p5min > 0:
            cp = 0.90 * float(p5min)
        elif p3min is not None and p3min > 0:
            cp = 0.85 * float(p3min)
        else:
            raise ValueError("Not enough data to estimate CP (need at least one of 3/5/12min).")

    w_prime, _ = _estimate_wprime(cp, p20s=p20s, p1min=p1min)

    return round(cp, 1), round(w_prime, 1)


def calc_critical_power_verbose(
    p5min: float,
    p12min: float,
    p20s: Optional[float] = None,
    p1min: Optional[float] = None,
    p3min: Optional[float] = None,
) -> CPResult:
    long_points: List[Tuple[float, float]] = []
    if p3min is not None and p3min > 0:
        long_points.append((180.0, float(p3min)))
    if p5min is not None and p5min > 0:
        long_points.append((300.0, float(p5min)))
    if p12min is not None and p12min > 0:
        long_points.append((720.0, float(p12min)))

    if len(long_points) >= 2:
        cp_raw, _wprime_fit = _work_time_fit(long_points)
        cp = _clamp_cp(cp_raw, long_points)
        cp_method = "work-time fit (>=3min)"
    else:
        if p12min is not None and p12min > 0:
            cp = 0.95 * float(p12min)
            cp_method = "fallback: 0.95 * P12"
        elif p5min is not None and p5min > 0:
            cp = 0.90 * float(p5min)
            cp_method = "fallback: 0.90 * P5"
        elif p3min is not None and p3min > 0:
            cp = 0.85 * float(p3min)
            cp_method = "fallback: 0.85 * P3"
        else:
            raise ValueError("Not enough data to estimate CP (need at least one of 3/5/12min).")

    w_prime, w_method = _estimate_wprime(cp, p20s=p20s, p1min=p1min)
    return CPResult(cp=round(cp, 1), w_prime=round(w_prime, 1), cp_method=cp_method, wprime_method=w_method)
