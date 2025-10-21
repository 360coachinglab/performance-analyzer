import pandas as pd

def calc_zones(cp, hfmax, fatmax_w, vlamax):
    """
    Berechnet Trainingszonen auf Basis von CP, VLamax und FatMax.
    Gibt eine Pandas-Tabelle mit Zonen, Wattbereichen und Beschreibung zurück.
    """

    cp = float(cp)
    if cp <= 0:
        return pd.DataFrame(columns=["Zone", "von [W]", "bis [W]", "Beschreibung"])

    # --- VLamax-bedingte Verschiebung (Shift) ---
    v = max(0.2, min(float(vlamax), 1.0))
    s = ((0.6 - v) / 0.4) * 0.05  # ±5 %

    # --- Basis-Prozentwerte relativ zu CP ---
    z1_upper = 0.55 * (1 + s)
    z2_upper = 0.75 * (1 + s)
    z3_upper = 0.90 * (1 + s)
    z4_upper = 1.05 * (1 + s)

    # --- FatMax-Korrektur: FatMax immer in Zone 2 (GA1) halten ---
    fatmax_rel = None if fatmax_w is None or cp == 0 else fatmax_w / cp
    if fatmax_rel:
        if fatmax_rel < z1_upper:
            z1_upper = max(0.45, fatmax_rel - 0.01)
        if fatmax_rel > z2_upper:
            z2_upper = min(0.85, fatmax_rel + 0.01)

    # --- Zonen als Wattbereiche (weiterhin dynamisch durch VLamax & FatMax) ---
    zones = [
        ("Z1 - Regeneration", 0, z1_upper * cp, "Sehr locker, aktive Erholung"),
        ("Z2 - GA1 (Fettstoffwechsel)", z1_upper * cp, z2_upper * cp, "Fettoxidation dominant"),
        ("Z3 - GA2 (Übergang)", z2_upper * cp, z3_upper * cp, "Mischstoffwechsel"),
        ("Z4 - Schwelle", z3_upper * cp, z4_upper * cp, "MLSS / CP bis 105%"),
        ("Z5 - VO2max", z4_upper * cp, 1.25 * cp, "Intensive Reize"),
    ]

    df = pd.DataFrame(zones, columns=["Zone", "von [W]", "bis [W]", "Beschreibung"])
    df["von [W]"] = df["von [W]"].round(0).astype(int)
    df["bis [W]"] = df["bis [W]"].round(0).astype(int)

    # --- Prozentwerte (nur zur Anzeige, nicht fix für Berechnung) ---
    df["% von CP"] = [
        f"{round((row['von [W]']/cp)*100):.0f}–{round((row['bis [W]']/cp)*100):.0f} %"
        for _, row in df.iterrows()
    ]

    # Spaltenreihenfolge für schöne Anzeige
    df = df[["Zone", "von [W]", "bis [W]", "% von CP", "Beschreibung"]]
    return df

    # --- Zonen als Wattbereiche ---
    #zones = [
    #    ("Z1 - Regeneration", 0, z1_upper * cp, "Sehr locker, aktive Erholung"),
     #   ("Z2 - GA1 (Fettstoffwechsel)", z1_upper * cp, z2_upper * cp, "Fettoxidation dominant"),
     #   ("Z3 - GA2 (Übergang)", z2_upper * cp, z3_upper * cp, "Mischstoffwechsel"),
    #    ("Z4 - Schwelle", z3_upper * cp, z4_upper * cp, "MLSS / CP bis 105%"),
    #    ("Z5 - VO2max", z4_upper * cp, 1.25 * cp, "Intensive Reize"),
    #]

    # df = pd.DataFrame(zones, columns=["Zone", "von [W]", "bis [W]", "Beschreibung"])
    #df = df[["Zone", "von [W]", "bis [W]", "% von CP", "Beschreibung"]]
    #df["von [W]"] = df["von [W]"].round(0).astype(int)
    #df["bis [W]"] = df["bis [W]"].round(0).astype(int)
    
    # Prozentbereich von CP ergänzen
    #df["% von CP"] = [
    #    f"{round((row['von [W]']/cp)*100):.0f}–{round((row['bis [W]']/cp)*100):.0f} %"
    #    for _, row in df.iterrows()
    #]
    
    #return df

def calc_ga1_zone(fatmax_w, cp, vlamax):
    """Liefert den GA1-Bereich als Watt- und Prozentwerte zurück (FatMax-basiert)."""
    cp = float(cp)
    if cp <= 0:
        return 0, 0, 0, 0

    v = max(0.2, min(float(vlamax), 1.0))
    s = ((0.6 - v) / 0.4) * 0.05  # ±5 %
    lo_pct, hi_pct = (0.55 * (1 + s), 0.75 * (1 + s))

    fatmax_rel = None if fatmax_w is None or cp == 0 else fatmax_w / cp
    if fatmax_rel:
        if fatmax_rel < lo_pct:
            lo_pct = max(0.45, fatmax_rel - 0.01)
        if fatmax_rel > hi_pct:
            hi_pct = min(0.85, fatmax_rel + 0.01)

    return lo_pct * cp, hi_pct * cp, lo_pct * 100, hi_pct * 100
