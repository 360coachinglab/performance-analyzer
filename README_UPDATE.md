
# Performance Analyzer v1.9.9b — Neutral • Dynamic Zones + PDF

## Neu
- Dynamische Zonen (GA1–R) abhängig von **CP + VLamax (+ FatMax)**
- Neutraler PDF-Export (lokale Speicherung + Download-Button)

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

## Nutzung
- Nach der Analyse → **PDF exportieren** klicken  
- Datei wird unter `exports/<Athletenname>_<YYYY-MM-DD>.pdf` gespeichert  
- Direkt danach erscheint der **Download-Button**
