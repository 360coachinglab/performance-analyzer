"""calculations/vo2max.py — VO2max estimation (backward compatible)

Your app (app.py) calls:

    vo2_abs, vo2_rel = calc_vo2max(p5min, weight, gender, method="B")

This module keeps that API **unchanged** while adding:
- method="MEAN" (default): mean of Formula A and B
- optional p3min_w for blending (default 70% P5 / 30% P3). Blend only if BOTH P5 and P3 > 0.
- optional p12min_w for plausibility flags (NOT mixed into VO2max)
- fallback: if P5 missing/<=0 but P3 exists -> compute from P3

Formulas (relative, ml/kg/min):
- A: 16.6 + 8.87 * (W/kg)
- B:  7.0 + 10.8 * (W/kg)
- MEAN: (A + B) / 2
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


def _rel_from_formula_a(power_w: float, kg: float) -> float:
    return 16.6 + 8.87 * (float(power_w) / float(kg))


def _rel_from_formula_b(power_w: float, kg: float) -> float:
    return 7.0 + 10.8 * (float(power_w) / float(kg))


def _rel_from_mean(power_w: float, kg: float) -> float:
    a = _rel_from_formula_a(power_w, kg)
    b = _rel_from_formula_b(power_w, kg)
    return (a + b) / 2.0


def _to_abs_l_min(vo2_rel_ml_kg_min: float, kg: float) -> float:
    return (float(vo2_rel_ml_kg_min) * float(kg)) / 1000.0


@dataclass(frozen=True)
class VO2MaxResult:
    vo2_abs_l_min: float
    vo2_rel_ml_kg_min: float
    method: str
    flags: List[str]
    details: Dict[str, Any]


def calc_vo2max_result(
    p5min_w: Optional[float],
    weight_kg: float,
    gender: str = "Mann",
    method: str = "MEAN",
    *,
    p3min_w: Optional[float] = None,
    p12min_w: Optional[float] = None,
    blend_w5: float = 0.7,
) -> VO2MaxResult:
    """Rich result (with flags/details)."""

    if weight_kg <= 0:
        raise ValueError("Gewicht muss > 0 sein.")

    p5_ok = p5min_w is not None and float(p5min_w) > 0
    p3_ok = p3min_w is not None and float(p3min_w) > 0

    if not p5_ok and not p3_ok:
        raise ValueError("Mindestens ein Wert muss vorhanden sein: 5min oder 3min (Watt > 0).")

    m = (method or "MEAN").strip().upper()
    if m == "A":
        rel_fn = _rel_from_formula_a
        m_label = "A"
    elif m == "B":
        rel_fn = _rel_from_formula_b
        m_label = "B"
    else:
        rel_fn = _rel_from_mean
        m_label = "MEAN(A,B)"

    flags: List[str] = []
    details: Dict[str, Any] = {"gender": gender, "method_input": method}

    # Anchor (prefer P5)
    if p5_ok:
        vo2_rel_5 = rel_fn(float(p5min_w), weight_kg)
        details["vo2_rel_5"] = vo2_rel_5
        details["p5min_w"] = float(p5min_w)
        vo2_rel_final = vo2_rel_5
        method_used = f"P5_{m_label}"
    else:
        vo2_rel_3_anchor = rel_fn(float(p3min_w), weight_kg)
        details["vo2_rel_3"] = vo2_rel_3_anchor
        details["p3min_w"] = float(p3min_w)
        vo2_rel_final = vo2_rel_3_anchor
        method_used = f"P3_{m_label}_fallback(no_P5)"
        flags.append("Kein 5min-Wert: VO2max basiert nur auf 3min (Fallback, weniger robust)")

    # Blend only if BOTH present
    if p5_ok and p3_ok:
        w5 = float(blend_w5)
        if not (0.0 <= w5 <= 1.0):
            raise ValueError("blend_w5 muss zwischen 0 und 1 liegen.")
        w3 = 1.0 - w5

        vo2_rel_3 = rel_fn(float(p3min_w), weight_kg)
        details["vo2_rel_3"] = vo2_rel_3
        details["p3min_w"] = float(p3min_w)
        details["blend_w5"] = w5
        details["blend_w3"] = w3
        details["ratio_p3_p5"] = float(p3min_w) / float(p5min_w)

        if float(p3min_w) < float(p5min_w):
            flags.append("P3 < P5: mögliches Daten-/Testproblem (3min war nicht maximal?)")

        vo2_rel_final = w5 * vo2_rel_5 + w3 * vo2_rel_3
        method_used = f"blend(P5_{m_label}*{w5:.2f}+P3_{m_label}*{w3:.2f})"

    # 12-min plausibility (no mixing)
    if p12min_w is not None and float(p12min_w) > 0:
        details["p12min_w"] = float(p12min_w)

        if p5_ok:
            ratio = float(p12min_w) / float(p5min_w)
            details["ratio_p12_p5"] = ratio
            if float(p12min_w) >= float(p5min_w):
                flags.append("P12 >= P5: sehr unwahrscheinlich (Datenfehler oder falsche Zuordnung)")
            if ratio > 0.92:
                flags.append("P12 sehr nah an P5: 5min evtl. nicht maximal oder Pacing sehr konservativ")

        if p3_ok and float(p12min_w) >= float(p3min_w):
            flags.append("P12 >= P3: sehr unwahrscheinlich (Datenfehler oder falsche Zuordnung)")

    vo2_abs = _to_abs_l_min(vo2_rel_final, weight_kg)

    return VO2MaxResult(
        vo2_abs_l_min=float(vo2_abs),
        vo2_rel_ml_kg_min=float(vo2_rel_final),
        method=method_used,
        flags=flags,
        details=details,
    )


def calc_vo2max(
    p5min_w: Optional[float],
    weight_kg: float,
    gender: str = "Mann",
    method: str = "MEAN",
    *,
    p3min_w: Optional[float] = None,
    p12min_w: Optional[float] = None,
    blend_w5: float = 0.7,
) -> Tuple[float, float]:
    """Backward-compatible API used by app.py: returns (vo2_abs_l_min, vo2_rel_ml_kg_min)."""
    r = calc_vo2max_result(
        p5min_w=p5min_w,
        weight_kg=weight_kg,
        gender=gender,
        method=method,
        p3min_w=p3min_w,
        p12min_w=p12min_w,
        blend_w5=blend_w5,
    )
    return r.vo2_abs_l_min, r.vo2_rel_ml_kg_min
