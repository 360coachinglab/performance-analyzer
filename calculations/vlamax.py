
def calc_vlamax(ffm, avg20, peak20, sprint_dur_s, gender):
    """Präzise VLamax-Schätzung basierend auf Regressionsmodell (18.10.2025)
    Berücksichtigt FFM, ØWatt, PeakWatt, Sprintdauer und Geschlecht.
    Formel:
    VLamax = 0.698
            - 0.0056 * FFM
            + 0.0011 * Watt Durchschnitt
            + 0.0001 * Watt Peak
            + 0.0040 * Sprintdauer
            - 0.1347 * Geschlecht (1=Mann, 0=Frau)
    Rückgabe: mmol/l/s
    """
    # Geschlecht in numerische Form bringen
    gnum = 1 if str(gender).lower().startswith("m") else 0

    # Berechnung
    vlamax = (
        0.698
        - 0.0056 * float(ffm)
        + 0.0011 * float(avg20)
        + 0.0001 * float(peak20)
        + 0.0040 * float(sprint_dur_s)
        - 0.1347 * gnum
    )
    # Sicherheitsbegrenzung
    return max(0.2, min(0.9, round(vlamax, 3)))
