def calc_fatmax(vo2_rel, vlamax):
    fatmax_rel = max(0.0, (vo2_rel / 100) * (1 - (vlamax * 1.5)))
    fatmax_w = fatmax_rel * 10
    return fatmax_w
