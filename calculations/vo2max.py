"""VO2max estimation utilities (field-test based).

- Uses 5-min power as the main anchor.
- VO2max (relative) is computed as the mean of two common linear formulas (A and B).
- If a 3-min value is available, a blended estimate is returned as well (default 60% 5-min, 40% 3-min).
- A 12-min value is used only for plausibility checks (not mixed into VO2max).

All VO2 values are returned as:
- vo2_abs_l_min: absolute VO2max in L/min
- vo2_rel_ml_kg_min: relative VO2max in ml/kg/min
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


def _rel_from_formula_a(power_w: float, kg: float) -> float:
    # VO2max [ml/kg/min] = 16.6 + 8.87 * (W/kg)
    return 16.6 + 8.87 * (float(power_w) / float(kg))


def _rel_from_formula_b(power_w: float, kg: float) -> float:
    # VO2max [ml/kg/min] = 7.0 + 10.8 * (W/kg)
    return 7.0 + 10.8 * (float(power_w) / float(kg))


def _mean_of_formulas(power_w: float, kg: float) -> float:
    """Return mean(Formula A, Formula B) for a given power."""
    a = _rel_from_formula_a(power_w, kg)
    b = _rel_from_formula_b(power_w, kg)
    return (a + b) / 2.0


def _to_abs_l_min(vo2_rel_ml_kg_min: float, kg: float) -> float:
    # ml/kg/min * kg = ml/min -> /1000 = L/min
    return (float(vo2_rel_ml_kg_min) * float(kg)) / 1000.0


@dataclass(frozen=True)
class VO2MaxResult:
    vo2_abs_l_min: float
    vo2_rel_ml_kg_min: float
    method: str
    flags: List[str]
    details: dict


def calc_vo2max(
    weight_kg: float,
    p5min_w: float,
    p3min_w: Optional[float] = None,
    p12min_w: Optional[float] = None,
    blend_w5: float = 0.7,
) -> VO2MaxResult:
    """Estimate VO2max from field test powers.

    Args:
        weight_kg: Athlete body mass in kg (>0).
        p5min_w: 5-min mean maximal power in watts (>0). Used as main anchor.
        p3min_w: Optional 3-min mean maximal power in watts.
        p12min_w: Optional 12-min mean maximal power in watts (plausibility only).
        blend_w5: Weight for 5-min estimate when 3-min is present.
                  3-min weight is (1 - blend_w5).
                  Default 0.7 -> 70% 5-min, 30% 3-min (3-min maximal 30% Einfluss).

    Returns:
        VO2MaxResult with VO2max (abs/rel), flags, and details.
    """

    if weight_kg <= 0:
        raise ValueError("Gewicht muss > 0 sein.")
    if p5min_w <= 0:
        raise ValueError("5min-Wert muss > 0 sein.")

    flags: List[str] = []
    details: dict = {}

    # --- Base: 5-min VO2max from mean(formula A, B)
    vo2_rel_5 = _mean_of_formulas(p5min_w, weight_kg)
    details["vo2_rel_5"] = vo2_rel_5
    details["vo2_abs_5"] = _to_abs_l_min(vo2_rel_5, weight_kg)

    method = "P5_mean(A,B)"
    vo2_rel_final = vo2_rel_5

    # --- Optional: 3-min blended estimate
    if p3min_w is not None:
        if p3min_w <= 0:
            flags.append("P3 invalid (<=0) -> ignored")
        else:
            # plausibility: typically P3 >= P5. If not, likely non-max test or data mismatch
            if p3min_w < p5min_w:
                flags.append("P3 < P5: mögliches Daten-/Testproblem (3min war nicht maximal?)")

            vo2_rel_3 = _mean_of_formulas(p3min_w, weight_kg)
            details["vo2_rel_3"] = vo2_rel_3
            details["vo2_abs_3"] = _to_abs_l_min(vo2_rel_3, weight_kg)

            w5 = float(blend_w5)
            if not (0.0 <= w5 <= 1.0):
                raise ValueError("blend_w5 muss zwischen 0 und 1 liegen.")
            w3 = 1.0 - w5

            vo2_rel_final = w5 * vo2_rel_5 + w3 * vo2_rel_3
            method = f"blend(P5_mean(A,B)*{w5:.2f} + P3_mean(A,B)*{w3:.2f})"
            details["blend_w5"] = w5
            details["blend_w3"] = w3

            # ratios as diagnostics (helpful for debugging/coaching)
            details["ratio_p3_p5"] = float(p3min_w) / float(p5min_w) if p5min_w else None

    # --- Optional: 12-min plausibility checks (do not mix into VO2max)
    if p12min_w is not None:
        if p12min_w <= 0:
            flags.append("P12 invalid (<=0) -> ignored")
        else:
            details["ratio_p12_p5"] = float(p12min_w) / float(p5min_w) if p5min_w else None
            if p12min_w >= p5min_w:
                flags.append("P12 >= P5: sehr unwahrscheinlich (Datenfehler oder falsche Zuordnung)")
            if p3min_w is not None and p3min_w > 0 and p12min_w >= p3min_w:
                flags.append("P12 >= P3: sehr unwahrscheinlich (Datenfehler oder falsche Zuordnung)")

            # soft warning: if 12-min is very close to 5-min, 5-min might not be truly maximal
            # (threshold intentionally conservative)
            if p12min_w / p5min_w > 0.92:
                flags.append("P12 sehr nah an P5: 5min evtl. nicht maximal oder Pacing sehr konservativ")

    vo2_abs_final = _to_abs_l_min(vo2_rel_final, weight_kg)

    return VO2MaxResult(
        vo2_abs_l_min=float(vo2_abs_final),
        vo2_rel_ml_kg_min=float(vo2_rel_final),
        method=method,
        flags=flags,
        details=details,
    )
