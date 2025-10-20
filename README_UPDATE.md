
# Performance Analyzer v1.9.8 – Dashboard Edition

## Features
- Critical Power (20s, 1min, 3min, 5min, 12min) – Monod–Scherrer
- GA-Zonen dynamisch: abhängig von CP und VLamax
- Dashboard-Visuals: VLamax-Gauge, VO₂max-Gauge, FatMax in Zonen
- VO₂max (Formel B: 7 + 10.8 × P5/kg)
- Exaktes VLamax-Modell (CSV/Joblib aus deiner vlamax-App)

## Installation
1. Dateien ins Projekt kopieren.
2. Abhängigkeiten installieren (siehe requirements.txt).
3. Starten mit `streamlit run app.py`.

## Hinweise
- `vlamax_testdaten.csv` im Projekt-Root benötigt, damit das VLamax-Modell trainiert/geladen werden kann.
