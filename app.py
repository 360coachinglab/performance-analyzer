import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from calculations.critical_power import calc_critical_power
from calculations.vo2max import calc_vo2max
from calculations.vlamax import calc_vlamax
from calculations.fatmax import calc_fatmax
from calculations.zones import calc_zones, calc_ga1_zone
from utils.athlete_type import determine_athlete_type

st.set_page_config(page_title="360 Coaching Lab – Performance Analyzer", page_icon="🚴", layout="wide")

st.title("🚴 360 Coaching Lab – Performance Analyzer")
st.markdown("#### Leistungsdiagnostik & physiologische Analyse")
st.sidebar.markdown("**Version:** 1.7 – VLamax empirisch (LOOCV-optimiert)**")

st.header("📥 Eingabe der Testdaten")
col1, col2, col3 = st.columns(3)
with col1:
    gender = st.selectbox("Geschlecht", ["Mann", "Frau"])
    weight = st.number_input("Körpergewicht (kg)", 40.0, 120.0, 70.0)
    bodyfat = st.number_input("Körperfett (%)", 3.0, 40.0, 15.0)
with col2:
    hfmax = st.number_input("HFmax", 100, 220, 190)
    p5min = st.number_input("Power 5min (W)", 100, 800, 350)
    p12min = st.number_input("Power 12min (W)", 100, 700, 300)
with col3:
    sprint_dur = st.number_input("Sprintdauer (s)", 10, 30, 20)
    avg20 = st.number_input("20s Ø-Leistung (W)", 200, 1500, 650)
    peak20 = st.number_input("20s Peak-Leistung (W)", 300, 1800, 900)

if st.button("Analyse starten 🚀"):
    ftp, w_prime = calc_critical_power(p5min, p12min, peak20)
    vo2_abs, vo2_rel = calc_vo2max(p5min, weight, gender)
    ffm = weight * (1 - bodyfat / 100)
    vlamax = calc_vlamax(ffm=ffm, avg20=avg20, peak20=peak20, sprint_dur_s=sprint_dur, gender=gender)
    fatmax_w, fatmax_pct_ftp, zone_label = calc_fatmax(vo2_rel, vlamax, ftp)
    zones = calc_zones(ftp, hfmax, fatmax_w, vlamax)
    ga1_min, ga1_max, ga1_pct_min, ga1_pct_max = calc_ga1_zone(fatmax_w, ftp, vlamax)
    athlete_type = determine_athlete_type(vo2_rel, vlamax, ftp, weight)

    st.subheader("📊 Ergebnisse")
    df = pd.DataFrame({
        "Parameter": [
            "FTP/CP", "W′", "VO₂max (l/min)", "VO₂max rel. (ml/min/kg)",
            "VLaMax", "FatMax (W)", "FatMax (%FTP)",
            "Empf. GA1-Zone (W)", "Empf. GA1-Zone (%FTP)", "Athletentyp"
        ],
        "Wert": [
            ftp, w_prime, round(vo2_abs,2), round(vo2_rel,1),
            round(vlamax,3), f"**{round(fatmax_w,1)}**", f"**{round(fatmax_pct_ftp,1)} %**",
            f"{int(ga1_min)}–{int(ga1_max)}", f"{round(ga1_pct_min,1)}–{round(ga1_pct_max,1)} %", athlete_type
        ]
    })
    from tabulate import tabulate
    st.markdown(tabulate(df, headers='keys', tablefmt='github', showindex=False))

    st.subheader("🏁 Trainingszonen (metabolisch)")
    st.dataframe(zones)

    st.subheader("📈 Beispielhafte Powerkurve")
    durations = [20, 60, 300, 720]
    powers = [peak20, (peak20+p5min)/2, p5min, p12min]
    fig, ax = plt.subplots()
    ax.plot(durations, powers, marker="o")
    ax.set_xlabel("Dauer (s)")
    ax.set_ylabel("Leistung (W)")
    ax.set_title("Leistungsprofil")
    st.pyplot(fig)

    st.success("Analyse abgeschlossen ✅")
