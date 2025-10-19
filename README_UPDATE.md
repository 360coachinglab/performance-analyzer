
# Performance Analyzer v1.9.6 – VO2max Formel B

Diese Version nutzt standardmäßig die realistische **Formel B**:

    VO₂rel [ml/min/kg] = 7 + 10.8 × (P5 / kg)
    VO₂abs [l/min]     = (VO₂rel × kg) / 1000

Formel A bleibt optional im Code enthalten:

    VO₂rel [ml/min/kg] = 16.6 + 8.87 × (P5 / kg)

### Nutzung
Keine Anpassung im UI nötig – die App verwendet automatisch Formel B als Standard.
Wenn du Formel A nutzen möchtest, kannst du im Aufruf manuell setzen:

```python
vo2_abs, vo2_rel = calc_vo2max(p5min_w, weight, method="A")
```
