
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import date

from calculations.critical_power import calc_critical_power
from calculations.vo2max import calc_vo2max
from calculations.vlamax import calc_vlamax
from calculations.vlamax_kona_calibrated import calc_vlamax_kona_calibrated
from calculations.fatmax import calc_fatmax
from calculations.zones import calc_zones, calc_ga1_zone
from utils.athlete_type import determine_athlete_type

st.set_page_config(page_title="360 Coaching Lab – Performance Analyzer", page_icon="🚴", layout="wide")

# Sidebar
st.sidebar.markdown("### 🧬 360 Coaching Lab")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="🚴 Performance Analyzer")
st.sidebar.page_link("pages/Dashboards.py", label="📊 Dashboards")
st.sidebar.page_link("pages/Analyse_Overview.py", label="📈 Analyse-Übersicht")
st.sidebar.markdown("---")
st.sidebar.markdown("**Version:** 1.9.4**")

st.title("🚴 360 Coaching Lab – Performance Analyzer")
st.markdown("#### Leistungsdiagnostik & physiologische Analyse")

athlete_name = st.text_input("Athletenname", placeholder="Name eingeben")

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
    if not athlete_name.strip():
        st.warning("Bitte **Athletenname** eingeben, damit der Test gespeichert werden kann.")
        st.stop()

    ftp, w_prime = calc_critical_power(p5min, p12min, peak20)
    vo2_abs, vo2_rel = calc_vo2max(p5min, weight, gender)
    ffm = weight * (1 - bodyfat / 100)

    try:
        vlamax = calc_vlamax_kona_calibrated(ffm, avg20, peak20, sprint_dur, vo2_rel, p5min, p12min, gender)
        model_used = "Kona-Calibrated"
    except Exception:
        vlamax = calc_vlamax(ffm, avg20, peak20, sprint_dur, gender)
        model_used = "Classic-Fallback"

    fatmax_w, fatmax_pct_ftp, zone_label = calc_fatmax(vo2_rel, vlamax, ftp)
    zones = calc_zones(ftp, hfmax, fatmax_w, vlamax)
    ga1_min, ga1_max, ga1_pct_min, ga1_pct_max = calc_ga1_zone(fatmax_w, ftp, vlamax)
    athlete_type = determine_athlete_type(vo2_rel, vlamax, ftp, weight)

    # Metrics
    st.subheader("🔢 Leistungskennzahlen")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("FTP / CP", f"{ftp:.0f} W")
    m2.metric("VO₂max rel.", f"{vo2_rel:.1f} ml/min/kg")
    m3.metric("FatMax", f"{fatmax_w:.0f} W")
    m4.metric(f"VLaMax ({model_used})", f"{vlamax:.3f} mmol/l/s")

    st.subheader("📊 Ergebnisse")
    df = pd.DataFrame({
        "Parameter": [
            "Datum", "Name", "FTP/CP", "W′", "VO₂max (l/min)", "VO₂max rel. (ml/min/kg)",
            "VLaMax", "FatMax (W)", "FatMax (%FTP)",
            "Empf. GA1-Zone (W)", "Empf. GA1-Zone (%FTP)", "Athletentyp"
        ],
        "Wert": [
            str(date.today()), athlete_name, ftp, w_prime, round(vo2_abs,2), round(vo2_rel,1),
            round(vlamax,3), f"{round(fatmax_w,1)}", f"{round(fatmax_pct_ftp,1)} %",
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
    ax.plot(durations, powers, marker="o", color="#3CB371")
    ax.set_xlabel("Dauer (s)")
    ax.set_ylabel("Leistung (W)")
    ax.set_title("Leistungsprofil")
    st.pyplot(fig)

    # Save data
    save_row = {
        "Datum": str(date.today()),
        "Name": athlete_name,
        "Geschlecht": gender,
        "Gewicht (kg)": weight,
        "Körperfett (%)": bodyfat,
        "VO2max rel (ml/min/kg)": round(vo2_rel,1),
        "VO2max abs (l/min)": round(vo2_abs,2),
        "FTP (W)": ftp,
        "VLamax (mmol/l/s)": round(vlamax,3),
        "FatMax (W)": round(fatmax_w,1),
        "Athletentyp": athlete_type,
    }
    data_dir = Path("data"); data_dir.mkdir(exist_ok=True)
    csv_path = data_dir / "athleten_daten.csv"
    try:
        if csv_path.exists():
            old = pd.read_csv(csv_path)
            new = pd.concat([old, pd.DataFrame([save_row])], ignore_index=True)
        else:
            new = pd.DataFrame([save_row])
        new.to_csv(csv_path, index=False)
        st.success(f"Datensatz gespeichert → {csv_path}")
    except Exception as e:
        st.warning(f"Konnte CSV nicht schreiben: {e}")

    st.success("Analyse abgeschlossen ✅")
