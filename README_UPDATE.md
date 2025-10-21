
# Performance Analyzer v1.9.9d — Neutral • Dynamic Zones + PDF (in-memory)

## Fixes
- Matplotlib auf **Agg**-Backend gestellt (headless sicher).
- Diagramme als **in-memory PNG** eingebettet (kein Temp-Verzeichnis mehr nötig).
- PDF-Export nur noch **im Speicher** → zuverlässiger Download-Button.

## Installation
Ergänze/prüfe in `requirements.txt`:
matplotlib>=3.7
reportlab>=4.0.0
tabulate
pandas
numpy
streamlit

Starten:
streamlit run app.py
