# app.py — 360 Coaching Lab · Performance Analyzer
# Vollständige, lauffähige Streamlit-App mit CP/FTP/W′-Berechnung (VLamax-abhängig)
# und sicherem Startverhalten (zeigt Ergebnisse erst nach „Analyse starten“).

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Externe Berechnungen importieren
# ---------------------------
try:
    from calculations.critical_power import calc_critical_power, corrected_ftp
except Exception as e:
    st.error("Fehlender Import: calculations/critical_power.py. Bitte sicherstellen, dass diese Datei vorhanden ist.")
    st.stop()

# Zonen-Import (optional). Wenn nicht vorhanden, verwenden wir unten einen Fallback.
try:
    from calculations.zones import calc_zones as external_calc_zones
except Exception:
    external_calc_zones = None


# ---------------------------
# Fallback-Zonen (falls calculations/zones.py fehlt)
# ---------------------------
def _fallback_calc_zones(cp: float, vlamax: float = None) -> pd.DataFrame:
    """
    Einfache, CP-basierte Zonen mit leichtem VLamax-Einfluss.
    Ohne HF/FatMax – nur als Fallback, bis calculations/zones.py vorhanden ist.
    """
    v = 0.5 if vlamax is None else float(vlamax)
    # kleine Anpassung: niedrige VLamax → GA-Zonen etwas weiter, hohe → enger
    adj = np.clip((0.5 - v) * 0.18, -0.10, 0.10)
    z1_up = 0.60 + adj
    z2_up = 0.75 + adj
    z3_up = 0.90 + adj
    z4_up = 1.05
    z5_up = 1.25

    zones = [
        ("Z1 – Regeneration", 0.00, z1_up, "Sehr locker, aktive Erholung"),
        ("Z2 – GA1 (Fettstoffwechsel)", z1_up, z2_up, "Fettoxidation dominant"),
        ("Z3 – GA2 (Übergang)", z2_up, z3_up, "Mischstoffwechsel"),
        ("Z4 – Schwelle", z3_up, z4_up, "MLSS/CP bis ~105%"),
        ("Z5 – VO₂max / Anaerob", z4_up, z5_up, "Intensive Reize, Laktattoleranz"),
    ]
    rows = []
    for name, lo, hi, desc in zones:
        rows.append({
            "Zone": name,
            "von (W)": round(cp * lo),
            "bis (W)": round(cp * hi),
            "Beschreibung": desc
        })
    return pd.DataFrame(rows)


# ---------------------------
# Seiten-Layout
# ---------------------------
st.set_page_config(page_title="360 Coaching Lab – Performance Analyzer", layout="wide")
st.title("🚴 360 Coaching Lab – Performance Analyzer")

st.markdown(
    "Gib deine Testleistungen ein (1, 3, 5, 12 min) und optional VLamax & Gewicht. "
    "Die App berechnet **Critical Power (CP)**, **W′** und **FTP** (VLamax-abhängig)."
)


# ---------------------------
# Eingabeformular
# ---------------------------
with st.form("eingaben"):
    c1, c2, c3 = st.columns(3)
    with c1:
        p1min  = st.number_input("1-min Maxleistung (W)", min_value=0, value=0, step=5)
        p3min  = st.number_input("3-min Maxleistung (W)", min_value=0, value=0, step=5)
    with c2:
        p5min  = st.number_input("5-min Maxleistung (W)", min_value=0, value=0, step=5)
        p12min = st.number_input("12-min Maxleistung (W)", min_value=0, value=0, step=5)
    with c3:
        vlamax = st.number_input("VLamax (mmol/l/s)", min_value=0.0, value=0.50, step=0.01, format="%.2f")
        weight = st.number_input("Körpergewicht (kg)", min_value=1.0, value=70.0, step=0.5, format="%.1f")

    submitted = st.form_submit_button("Analyse starten 🚀")

# Session-Container für Ergebnisse
if "results" not in st.session_state:
    st.session_state["results"] = None


# ---------------------------
# Analyse starten
# ---------------------------
if submitted:
    # Rechnen nur mit vorhandenen (>0) Werten
    valid = [x for x in (p1min, p3min, p5min, p12min) if x and x > 0]
    if len(valid) < 2:
        st.error("Bitte mindestens zwei gültige Leistungswerte (z. B. 5 und 12 Minuten) eingeben.")
        st.stop()

    # CP & W′
    cp, w_prime = calc_critical_power(
        p1min=p1min if p1min > 0 else None,
        p3min=p3min if p3min > 0 else None,
        p5min=p5min if p5min > 0 else None,
        p12min=p12min if p12min > 0 else None
    )

    # FTP (stark VLamax-abhängig, CP bleibt aerob)
    ftp = corrected_ftp(cp, vlamax)

    st.session_state["results"] = {
        "cp": cp,
        "w_prime": w_prime,
        "ftp": ftp,
        "vlamax": float(vlamax),
        "weight": float(weight),
    }


# ---------------------------
# Nur anzeigen, wenn Analyse vorhanden ist
# ---------------------------
if st.session_state["results"] is None:
    st.info("Bitte zuerst Daten eingeben und auf **„Analyse starten 🚀“** klicken, um die Ergebnisse zu sehen.")
    st.stop()

# Ergebnisse laden
r = st.session_state["results"]

# ---------------------------
# Kennzahlen: CP / W′ / FTP (W & W/kg) / VLamax
# ---------------------------
st.subheader("⚙️ Leistungskennzahlen")

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Critical Power (CP)", f"{r['cp']:.0f} W", help="Aerobe Dauerleistungsgrenze (MLSS-nah). CP < 12-min-Leistung garantiert.")
    st.metric("W′", f"{r['w_prime']:.0f} J", help="Anaerober Energievorrat oberhalb der CP.")
with m2:
    st.metric("FTP (TrainingPeaks)", f"{r['ftp']:.0f} W", help="60-Minuten-Leistung (VLamax-abhängig). Diesen Wert in TrainingPeaks eintragen.")
    st.metric("FTP (W/kg)", f"{r['ftp']/r['weight']:.2f}", help="Relativer Schwellenwert.")
with m3:
    st.metric("VLamax", f"{r['vlamax']:.3f} mmol/l/s", help="Max. Laktatbildungsrate (beeinflusst FTP und Athletentyp).")

st.info(f"💡 **Hinweis für TrainingPeaks:** Trage **FTP = {r['ftp']:.0f} W** als Schwelle ein. (CP intern: {r['cp']:.0f} W)")

# ---------------------------
# Zonen (CP-basiert)
# ---------------------------
st.subheader("🏁 Trainingszonen (CP-basiert)")
if external_calc_zones:
    try:
        zones_df = external_calc_zones(cp=r["cp"], hfmax=None, fatmax_w=None, vlamax=r["vlamax"])
    except Exception:
        zones_df = _fallback_calc_zones(r["cp"], r["vlamax"])
else:
    zones_df = _fallback_calc_zones(r["cp"], r["vlamax"])

st.dataframe(zones_df, use_container_width=True)

# Optional: kurze Erklärung unter der Tabelle (ohne Watt-/%Werte, die stehen bereits in der Tabelle)
with st.expander("Erklärung der Trainingszonen"):
    st.markdown("""
**Z1 – Regeneration:** sehr locker, fördert Erholung und Durchblutung.  
**Z2 – GA1 (Fettstoffwechsel):** Grundlage; maximale Fettoxidation, lange konstante Einheiten.  
**Z3 – GA2 (Übergang):** moderat, Mischstoffwechsel; verbessert Ermüdungsresistenz.  
**Z4 – Schwelle:** Bereich um CP/MLSS; hohe, aber kontrollierte Intensität.  
**Z5 – VO₂max / Anaerob:** sehr intensiv; kurze Intervalle, Laktattoleranz & maximale O₂-Aufnahme.
""")

# ---------------------------
# (Optional) Mini-Plot: CP-Modellkurve (Power vs. 1/t)
# ---------------------------
with st.expander("Diagnose: CP-Modell (Power vs. 1/t)"):
    # Falls nur zur Visualisierung der Regression gewünscht
    times = []
    powers = []
    for t_val, p_val in [(60, r.get("p1min")), (180, r.get("p3min")), (300, r.get("p5min")), (720, r.get("p12min"))]:
        if p_val is not None:
            times.append(t_val)
            powers.append(p_val)
    # Falls die Originaleingaben nicht gespeichert wurden, zeichnen Dummy-Punkte
    if len(times) >= 2:
        inv_t = [1.0/t for t in times]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(inv_t, powers, s=40)
        ax.set_xlabel("1 / Zeit (1/s)")
        ax.set_ylabel("Leistung (W)")
        ax.set_title("CP-Modell: P = W′/t + CP")
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    else:
        st.write("Zu wenige Punkte für die Modell-Diagramm-Anzeige.")

# Ende
