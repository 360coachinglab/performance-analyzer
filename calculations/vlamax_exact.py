
# calculations/vlamax_exact.py
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

CSV_PATH = "vlamax_testdaten.csv"
MODEL_PATH = "vlamax_model.joblib"

def _train_or_load_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass
    if os.path.exists(CSV_PATH):
        daten = pd.read_csv(CSV_PATH)
        if len(daten) >= 2:
            daten["FFM"] = daten["Gewicht (kg)"] * (1 - daten["Körperfett (%)"] / 100.0)
            daten["Geschlecht_code"] = daten["Geschlecht"].str.lower().map({"mann": 0, "frau": 1})
            X = daten[["FFM", "Sprintdauer (s)", "Watt Durchschnitt", "Watt Peak", "Geschlecht_code"]]
            y = daten["VLamax INSCYD (mmol/l/s)"]
            model = LinearRegression().fit(X, y)
            try:
                joblib.dump(model, MODEL_PATH)
            except Exception:
                pass
            return model
    return None

def calc_vlamax_exact_with_ffm(ffm_kg: float, avg20_w: float, peak20_w: float, sprint_s: float, gender: str) -> float:
    model = _train_or_load_model()
    if model is None:
        raise RuntimeError("Kein VLamax-Modell verfügbar (CSV/Joblib fehlt).")
    gcode = 1 if str(gender).strip().lower() == "frau" else 0
    row = np.array([[float(ffm_kg), float(sprint_s), float(avg20_w), float(peak20_w), gcode]], dtype=float)
    pred = float(model.predict(row)[0])
    return round(pred, 3)
