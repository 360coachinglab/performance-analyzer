
# Performance Analyzer v1.9.4 Update

## Änderungen
- Automatische Auswahl zwischen **Kona-Calibrated** und **Classic** VLamax-Modell
- Neue Version in Sidebar (1.9.4)
- Präzisere VLamax-Schätzung mit deinem kalibrierten Modell (R² = 0.97)
- Fallback bleibt Classic, falls Kona-Modell-Eingaben fehlen

## Nutzung
Einfach alte `app.py` und `calculations/vlamax*.py` ersetzen, dann starten:
```bash
streamlit run app.py
```
