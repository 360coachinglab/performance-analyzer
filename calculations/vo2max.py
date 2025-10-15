def calc_vo2max(p5min, weight, gender):
    factor = 12.24 if gender == 'Mann' else 11.45
    vo2_rel = (p5min * factor) / weight
    vo2_abs = vo2_rel * weight / 1000
    return vo2_abs, vo2_rel
