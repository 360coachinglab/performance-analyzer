import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from calculations.critical_power import calc_critical_power
from calculations.vo2max import calc_vo2max
from calculations.vlamax import calc_vlamax
from calculations.fatmax import calc_fatmax
from calculations.zones import calc_zones
from utils.athlete_type import determine_athlete_type

st.set_page_config(page_title="360 Coaching Lab – Performance Analyzer", page_icon="🚴", layout="wide")

st.title("🚴 360 Coaching Lab – Performance Analyzer")
st.markdown("#### Leistungsdiagnostik & physiologische Analyse")

st.sidebar.image("assets/logo.png", use_container_width=True)
st.sidebar.markdown("**Version:** 1.0.0")

# --- Eingabeformular ---
st.header("📥 Eingabe der Testdaten")

col1, col2, col3 = st.columns(3)
with col1:
    gender = st.selectbox("Geschlecht", ["Mann", "Frau"])
    weight = st.number_input("Körpergewicht (kg)", 40.0, 120.0, 70.0)
    bodyfat = st.number_input("Körperfett (%)", 3.0, 40.0, 15.0)
with col2:
    hfmax = st.number_input("HFmax", 100, 220, 190)
    p20s = st.number_input("Peak Power 20s (W)", 400, 1800, 900)
    p5min = st.number_input("Power 5min (W)", 100, 800, 350)
with col3:
    p12min = st.number_input("Power 12min (W)", 100, 700, 300)
    test_date = st.date_input("Testdatum")
    birth_date = st.date_input("Geburtsdatum")

if st.button("Analyse starten 🚀"):
    ftp, w_prime = calc_critical_power(p5min, p12min, p20s)
    vo2_abs, vo2_rel = calc_vo2max(p5min, weight, gender)
    ffm = weight * (1 - bodyfat / 100)
    vlamax = calc_vlamax(ffm, p20s, ftp, gender)
    fatmax = calc_fatmax(vo2_rel, vlamax)
    zones = calc_zones(ftp, hfmax)
    athlete_type = determine_athlete_type(vo2_rel, vlamax, ftp, weight)

    st.subheader("📊 Ergebnisse")
    df = pd.DataFrame({
        "Parameter": ["FTP/CP", "W′", "VO₂max (l/min)", "VO₂max rel. (ml/min/kg)", "VLaMax", "FatMax (W)", "Athletentyp"],
        "Wert": [ftp, w_prime, round(vo2_abs,2), round(vo2_rel,1), round(vlamax,3), round(fatmax,1), athlete_type]
    })
    st.table(df)

    st.subheader("🏁 Trainingszonen")
    st.dataframe(zones)

    st.subheader("📈 Beispielhafte Powerkurve")
    durations = [20, 60, 300, 720]
    powers = [p20s, (p20s+p5min)/2, p5min, p12min]
    fig, ax = plt.subplots()
    ax.plot(durations, powers, marker="o")
    ax.set_xlabel("Dauer (s)")
    ax.set_ylabel("Leistung (W)")
    ax.set_title("Leistungsprofil")
    st.pyplot(fig)

    st.success("Analyse abgeschlossen ✅")
