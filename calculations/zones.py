import pandas as pd

def calc_zones(ftp, hfmax, fatmax, vlamax):
    # dynamische metabolische Grenzen
    z1_upper = 0.75 * fatmax
    z2_upper = 1.05 * fatmax
    z3_upper = (1.35 - 0.3 * vlamax) * fatmax  # breiter GA2, abhängig von VLamax

    # Z4 (Schwelle) bis 105% FTP
    z4_lower = max(z2_upper, z3_upper)
    z4_upper = 1.05 * ftp

    # Falls GA2 rechnerisch über 105% FTP reichen würde, deckeln
    if z4_lower >= z4_upper:
        z4_lower = 0.98 * ftp  # min. kleine Z4-Breite
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
