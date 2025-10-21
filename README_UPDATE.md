
# Performance Analyzer v1.9.9c — Neutral • Dynamic Zones + PDF (in-memory first)

## Neu
- PDF-Export **im Speicher** (keine Dateirechte nötig). Fallback auf Dateisystem `exports/`.
- Dynamische Zonen (GA1–R) abhängig von **CP + VLamax (+ FatMax)**.

## Installation
1. Dateien in Projekt kopieren:
   - `app.py` ersetzen
   - `calculations/zones.py` anlegen/ersetzen
   - `pdf_export.py` ins Projekt-Root
2. `requirements.txt` ergänzen:
   reportlab>=4.0.0
3. Abhängigkeiten installieren:
   pip install -r requirements.txt
4. Start:
   streamlit run app.py
