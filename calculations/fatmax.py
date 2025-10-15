def calc_fatmax(vo2_rel, vlamax, ftp):
    fatmax_pct_ftp = 67.72 + (0.065 * vo2_rel) - (11.42 * vlamax)
    fatmax_pct_ftp = max(55.0, min(85.0, fatmax_pct_ftp))
    fatmax_w = ftp * (fatmax_pct_ftp / 100)
    if fatmax_pct_ftp < 60:
        zone = "Zone 2 (unterer GA1)"
    elif fatmax_pct_ftp < 70:
        zone = "Zone 2–3 (oberer GA1)"
    else:
        zone = "Zone 3 (GA2)"
    return fatmax_w, fatmax_pct_ftp, zone
