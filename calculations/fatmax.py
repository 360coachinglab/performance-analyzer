def calc_fatmax(vo2_rel, vlamax, ftp):
    """Berechnet FatMax (Watt und qualitative Zone) basierend auf VO2max, VLamax und FTP."""
    fatmax_percent_vo2 = 65 - (vlamax * 35) + ((vo2_rel - 60) * 0.5)
    fatmax_percent_vo2 = max(45, min(80, fatmax_percent_vo2))
    fatmax_percent_ftp = (fatmax_percent_vo2 / 100) * 0.85
    fatmax_watt = ftp * fatmax_percent_ftp
    if fatmax_percent_ftp < 0.55:
        zone = "Zone 2 (niedriger GA1)"
    elif fatmax_percent_ftp < 0.70:
        zone = "Zone 2–3 (oberer GA1)"
    else:
        zone = "Zone 3 (GA2)"
    return fatmax_watt, fatmax_percent_vo2, fatmax_percent_ftp * 100, zone
