
# Performance Analyzer v1.9.9 – PDF Export Edition (neutral)

## Neu
- PDF-Export in der App (weißes, neutrales Layout) inkl. Kennzahlen, Erklärtexte, Gauges (VO₂, VLamax), FatMax-in-Zonen, CP-Kurve.

## Abhängigkeiten
Bitte `requirements.txt` ergänzen:
reportlab>=4.0.0

(plus vorhanden: streamlit, pandas, numpy, matplotlib, scikit-learn, joblib, tabulate)

## Nutzung
1) Dateien ins Projekt legen.
2) `pip install -r requirements.txt`
3) In `app.py` importieren: `from pdf_export import create_analysis_pdf` (falls noch nicht vorhanden).
4) App starten → Analyse durchführen → **PDF exportieren**.
