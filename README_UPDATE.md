
# Performance Analyzer v1.9.7 – Critical Power Upgrade

## Neu
- Präzisere CP/W′-Berechnung per Monod–Scherrer: P = CP + W'/t
- Unterstützt optional 1‑ und 3‑Minuten-Leistung (werden nur verwendet, wenn eingegeben)
- UI: Neue Felder „Power 1min“ und „Power 3min“

## Einbau
1) Ersetze `calculations/critical_power.py` und (falls gewünscht) `app.py`.
2) Starte:
   ```bash
   streamlit run app.py
   ```
3) Gib 1‑ und 3‑Minuten‑Werte ein, wenn vorhanden – die Berechnung nutzt automatisch alle verfügbaren Punkte.
