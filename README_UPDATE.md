
# Performance Analyzer v1.9.6 – Komplett-Update

## Enthalten
- `app.py` – Haupt-App, Version 1.9.6
- `calculations/vo2max.py` – VO2max **Formel B** (7 + 10.8 × P5/kg), Formel A optional
- `calculations/vlamax_exact.py` – **Exact-App** VLamax (LinearRegression, CSV/Joblib)
- `calculations/vlamax.py` – Classic-Fallback

## Voraussetzungen
- `vlamax_testdaten.csv` im Projekt-Root (für Exact-App VLamax)
- Python-Pakete:
  - streamlit, pandas, numpy, scikit-learn, joblib, matplotlib, tabulate

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
