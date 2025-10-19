
# calculations/vo2max.py

def _rel_from_formula_a(p5_watt: float, kg: float) -> float:
    # Formel A: VO2rel [ml/min/kg] = 16.6 + 8.87 * (P5 / kg)
    return 16.6 + 8.87 * (float(p5_watt) / float(kg))

def _rel_from_formula_b(p5_watt: float, kg: float) -> float:
    # Formel B: VO2rel [ml/min/kg] = 7 + 10.8 * (P5 / kg)
    return 7.0 + 10.8 * (float(p5_watt) / float(kg))

def calc_vo2max(p5min_w: float, weight_kg: float, gender: str = "Mann", method: str = "B"):
    """
    Berechnet VO2max absolut (l/min) und relativ (ml/min/kg).

    method:
        "A" -> 16.6 + 8.87 × (P5/kg)
        "B" -> 7 + 10.8 × (P5/kg)  [Standard]
    """
    if weight_kg <= 0:
        raise ValueError("Gewicht muss > 0 sein.")

    method = (method or "B").upper()
    if method == "A":
        vo2_rel = _rel_from_formula_a(p5min_w, weight_kg)
    else:
        vo2_rel = _rel_from_formula_b(p5min_w, weight_kg)

    vo2_abs = (vo2_rel * weight_kg) / 1000.0  # l/min
    return float(vo2_abs), float(vo2_rel)
