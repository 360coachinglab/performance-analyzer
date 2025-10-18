
# Performance Analyzer v1.9.5 – Exact-App Integration

Diese Version reproduziert die Logik deiner vlamax-App:
- Trainiert/Lädt ein **LinearRegression**-Modell aus `vlamax_testdaten.csv`
- Features: **FFM**, **Sprintdauer (s)**, **Watt Durchschnitt**, **Watt Peak**, **Geschlecht_code (mann=0, frau=1)**
- Vorhersage identisch zu deiner App per `calc_vlamax_exact_with_ffm(...)`

## Nutzung
1) Lege `vlamax_testdaten.csv` in dein Projekt-Root (wie in der App).
2) Ersetze `app.py` durch die hier enthaltene Version **oder** importiere nur die Funktion:
   ```python
   from calculations.vlamax_exact import calc_vlamax_exact_with_ffm
   vlamax = calc_vlamax_exact_with_ffm(ffm, avg20, peak20, sprint_dur, gender)
   ```
3) Starte:
   ```bash
   streamlit run app.py
   ```

> Hinweis: Das Modell wird automatisch in `vlamax_model.joblib` gecached (so wie in deiner App).
