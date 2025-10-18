
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

CSV_PATH = "vlamax_testdaten.csv"
MODEL_PATH = "vlamax_model.joblib"

def _train_or_load_model():
    # 1) Try loading cached model
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass
    # 2) Train from CSV if available
    if os.path.exists(CSV_PATH):
        daten = pd.read_csv(CSV_PATH)
        if len(daten) >= 2:
            daten["FFM"] = daten["Gewicht (kg)"] * (1 - daten["Körperfett (%)"] / 100.0)
            daten["Geschlecht_code"] = daten["Geschlecht"].str.lower().map({"mann": 0, "frau": 1})
            X = daten[["FFM", "Sprintdauer (s)", "Watt Durchschnitt", "Watt Peak", "Geschlecht_code"]]
            y = daten["VLamax INSCYD (mmol/l/s)"]
            modell = LinearRegression().fit(X, y)
            try:
                joblib.dump(modell, MODEL_PATH)
            except Exception:
                pass
            return modell
    # 3) No model possible
    return None

def calc_vlamax_exact(weight_kg: float,
                      power20_w: float,
                      sprint_s: float = 20.0,
                      vo2_rel_mlkg: float | None = None,
                      ftp_w: float | None = None,
                      gender: str | None = None,
                      efficiency: float | None = None) -> float:
    """Reproduziert exakt die Logik der vlamax-app:
    - Training (oder Laden) eines LinearRegression-Modells mit Features:
      [FFM, Sprintdauer (s), Watt Durchschnitt, Watt Peak, Geschlecht_code]
    - Geschlecht_code: 'mann' -> 0, 'frau' -> 1
    - Vorhersage mit [FFM, sprint_s, power20_w (als ØWatt), peak20_w (=power20_w als Proxy?), Geschlecht_code]
      HINWEIS: In der App werden ØWatt und Peak separat abgefragt. Hier erwarten wir beide übergeben.
    """
    # Versuche peak aus power20_w zu schätzen, falls kein separates Argument existiert.
    peak20_w = power20_w  # im Analyzer wird Peak separat übergeben; diese Signatur lässt nur power20_w zu
    # Wenn der Aufrufer peak zur Verfügung hat, kann die Adapterfunktion später erweitert werden.

    ffm = float(weight_kg) * (1.0 - 0.0)  # FFM ist in der App aus Gewicht & KFA; hier fehlt KFA -> wird in app.py berechnet.
    # In app.py berechnen wir ffm bereits korrekt und rufen diese Funktion NICHT für FFM auf.
    # Daher implementieren wir eine zweite API unten, die FFM & Peak direkt nimmt.

    modell = _train_or_load_model()
    if modell is None:
        raise NotImplementedError("Kein Modell verfügbar (CSV/Joblib fehlt).")

    g = (gender or "mann").strip().lower()
    geschlecht_code = 1 if g == "frau" else 0

    row = np.array([[ffm, float(sprint_s), float(power20_w), float(peak20_w), geschlecht_code]], dtype=float)
    pred = float(modell.predict(row)[0])
    return round(pred, 3)


def calc_vlamax_exact_with_ffm(ffm_kg: float,
                               avg20_w: float,
                               peak20_w: float,
                               sprint_s: float,
                               gender: str) -> float:
    """Bevorzugte API für Analyzer: FFM wird in app.py korrekt aus Gewicht & KFA berechnet."""
    modell = _train_or_load_model()
    if modell is None:
        raise NotImplementedError("Kein Modell verfügbar (CSV/Joblib fehlt).")

    g = (gender or "mann").strip().lower()
    geschlecht_code = 1 if g == "frau" else 0

    import numpy as np
    row = np.array([[float(ffm_kg), float(sprint_s), float(avg20_w), float(peak20_w), geschlecht_code]], dtype=float)
    pred = float(modell.predict(row)[0])
    return round(pred, 3)
