import pandas as pd

def calc_zones(ftp, hfmax, fatmax, vlamax):
    """
    Erstellt metabolisch adaptierte Trainingszonen basierend auf FatMax und VLamax.
    """
    # Dynamische Grenzen in Abhängigkeit von VLamax
    z1_upper = 0.75 * fatmax
    z2_upper = 1.05 * fatmax
    z3_upper = (1.2 - vlamax * 0.3) * fatmax
    z4_upper = ftp

    zones = [
        ("Z1 - Regeneration", 0, z1_upper, "Sehr locker, aktive Erholung"),
        ("Z2 - GA1 (Fettstoffwechsel)", z1_upper, z2_upper, "Fettoxidation dominant"),
        ("Z3 - GA2 (Übergang)", z2_upper, z3_upper, "Mischstoffwechsel"),
        ("Z4 - Schwelle", z3_upper, z4_upper, "MLSS / FTP Bereich"),
        ("Z5 - VO2max", z4_upper, ftp * 1.2, "Intensive Reize"),
    ]

    df = pd.DataFrame(zones, columns=["Zone", "von (W)", "bis (W)", "Beschreibung"])
    df["von (W)"] = df["von (W)"].round(0)
    df["bis (W)"] = df["bis (W)"].round(0)
    return df
