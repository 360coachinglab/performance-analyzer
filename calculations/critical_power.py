import numpy as np

def calc_critical_power(p20s, p5min, p12min, p1min=None, p3min=None):
    """
    Berechnet Critical Power (CP) und W′ basierend auf einer linearen Regression
    von Leistung vs. 1/Zeit (P = W′/t + CP).
    
    Nutzt alle verfügbaren Leistungsdaten (20s, 1min, 3min, 5min, 12min),
    und fällt automatisch auf einfachere Näherung zurück, wenn weniger Punkte vorhanden sind.
    """

    # Eingabepunkte sammeln
    points = [
        (20, p20s),
        (60, p1min) if p1min else None,
        (180, p3min) if p3min else None,
        (300, p5min),
        (720, p12min)
    ]
    points = [p for p in points if p is not None and p[1] is not None]

    # Sicherheit: mindestens 2 Punkte nötig
    if len(points) < 2:
        cp = round(p5min * 0.9, 1)
        w_prime = round((p20s - cp) * 15, 1)
        return cp, w_prime

    # Arrays vorbereiten
    t = np.array([p[0] for p in points], dtype=float)
    p = np.array([p[1] for p in points], dtype=float)
    inv_t = 1.0 / t

    # Lineare Regression: P = a*(1/t) + b
    a, b = np.polyfit(inv_t, p, 1)
    w_prime = round(a, 1)  # Steigung = W′
    cp = round(b, 1)       # Achsenabschnitt = CP

    return cp, w_prime


def corrected_ftp(cp: float, vlamax: float) -> float:
    """
    Gibt den empfohlenen FTP-Wert für TrainingPeaks basierend auf VLamax zurück.
    Niedrige VLamax → CP ≈ FTP,
    hohe VLamax → FTP deutlich unter CP.
    """

    if vlamax <= 0.3:
        factor = 1.00
    elif vlamax <= 0.5:
        factor = 0.98
    elif vlamax <= 0.7:
        factor = 0.95
    else:
        factor = 0.93

    return round(cp * factor, 1)
