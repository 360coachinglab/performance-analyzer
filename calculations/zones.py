import pandas as pd

def calc_zones(ftp, hfmax, fatmax, vlamax):
    z1_upper = 0.75 * fatmax
    z2_upper = 1.05 * fatmax
    z3_upper = (1.35 - 0.3 * vlamax) * fatmax
    z4_lower = max(z2_upper, z3_upper)
    z4_upper = 1.05 * ftp
    if z4_lower >= z4_upper:
        z4_lower = 0.98 * ftp
        z3_upper = min(z3_upper, 0.97 * ftp)
    zones = [
        ("Z1 - Regeneration", 0, z1_upper, "Sehr locker, aktive Erholung"),
        ("Z2 - GA1 (Fettstoffwechsel)", z1_upper, z2_upper, "Fettoxidation dominant"),
        ("Z3 - GA2 (Übergang)", z2_upper, z3_upper, "Mischstoffwechsel"),
        ("Z4 - Schwelle", z3_upper, z4_upper, "MLSS / FTP bis 105%"),
        ("Z5 - VO2max", z4_upper, 1.25 * ftp, "Intensive Reize"),
    ]
    df = pd.DataFrame(zones, columns=["Zone", "von (W)", "bis (W)", "Beschreibung"])
    df["von (W)"] = df["von (W)"].round(0)
    df["bis (W)"] = df["bis (W)"].round(0)
    return df

def calc_ga1_zone(fatmax, ftp, vlamax):
    ga1_min = fatmax * (0.85 + 0.10 * vlamax)
    ga1_max = fatmax * (1.10 - 0.20 * vlamax)
    ga1_min = round(ga1_min, 1)
    ga1_max = round(ga1_max, 1)
    ga1_pct_min = round(ga1_min / ftp * 100, 1)
    ga1_pct_max = round(ga1_max / ftp * 100, 1)
    return ga1_min, ga1_max, ga1_pct_min, ga1_pct_max
