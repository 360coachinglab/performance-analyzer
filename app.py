
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
from tabulate import tabulate

from calculations.critical_power import calc_critical_power
from calculations.vo2max import calc_vo2max
from calculations.vlamax_exact import calc_vlamax_exact_with_ffm
from calculations.vlamax import calc_vlamax as calc_vlamax_classic
from calculations.fatmax import calc_fatmax
from calculations.zones import calc_zones, calc_ga1_zone
from utils.athlete_type import determine_athlete_type
from pdf_export import create_analysis_pdf_bytes

st.set_page_config(page_title="Performance Analyzer", page_icon="🚴", layout="wide")
st.sidebar.markdown("**Version:** 1.9.9e (Neutral • SessionState + PDF in-memory)**")

# ---------- helpers ----------
def compute_analysis(inputs: dict):
    gender = inputs['gender']
    weight = inputs['weight']
    bodyfat = inputs['bodyfat']
    hfmax = inputs['hfmax']
    p1min = inputs.get('p1min') or 0
    p3min = inputs.get('p3min') or 0
    p5min = inputs['p5min']
    p12min = inputs['p12min']
    sprint_dur = inputs['sprint_dur']
    avg20 = inputs['avg20']
    peak20 = inputs['peak20']

    p1 = None if p1min == 0 else p1min
    p3 = None if p3min == 0 else p3min

    cp, w_prime = calc_critical_power(p20s=peak20, p1min=p1, p3min=p3, p5min=p5min, p12min=p12min)
    vo2_abs, vo2_rel = calc_vo2max(p5min, weight, gender, method="B")
    ffm = weight * (1 - bodyfat / 100)

    try:
        vlamax = calc_vlamax_exact_with_ffm(ffm, avg20, peak20, sprint_dur, gender)
        model_used = "Exact-App"
    except Exception:
        vlamax = calc_vlamax_classic(ffm, avg20, peak20, sprint_dur, gender)
        model_used = "Classic-Fallback"

    fatmax_w, fatmax_pct_ftp, zone_label = calc_fatmax(vo2_rel, vlamax, cp)
    zones_df = calc_zones(cp, hfmax, fatmax_w, vlamax)
    ga1_min, ga1_max, ga1_pct_min, ga1_pct_max = calc_ga1_zone(fatmax_w, cp, vlamax)
    athlete_type = determine_athlete_type(vo2_rel, vlamax, cp, weight)

    pts = []
    if peak20: pts.append((20, peak20))
    if p1 is not None: pts.append((60, p1))
    if p3 is not None: pts.append((180, p3))
    if p5min: pts.append((300, p5min))
    if p12min: pts.append((720, p12min))

    return {
        "cp": cp, "w_prime": w_prime,
        "vo2_abs": vo2_abs, "vo2_rel": vo2_rel,
        "vlamax": vlamax, "model_used": model_used,
        "fatmax_w": fatmax_w, "zones_df": zones_df,
        "ga1_min": ga1_min, "ga1_max": ga1_max,
        "ga1_pct_min": ga1_pct_min, "ga1_pct_max": ga1_pct_max,
        "athlete_type": athlete_type, "pts": pts
    }

# ---------- UI ----------
st.title("Performance Analyzer")
st.markdown("#### Leistungsdiagnostik & physiologische Analyse (neutral)")

with st.form("input_form"):
    st.header("📥 Eingabe der Testdaten")
    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox("Geschlecht", ["Mann", "Frau"], key="gender")
        weight = st.number_input("Körpergewicht (kg)", 40.0, 140.0, 70.0, key="weight")
        bodyfat = st.number_input("Körperfett (%)", 3.0, 40.0, 15.0, step=0.1, key="bodyfat")
    with col2:
        hfmax = st.number_input("HFmax", 100, 220, 190, key="hfmax")
        p1min = st.number_input("Power 1min (W)", 0, 2000, 0, help="Optional – 0 falls unbekannt", key="p1min")
        p3min = st.number_input("Power 3min (W)", 0, 2000, 0, help="Optional – 0 falls unbekannt", key="p3min")
        p5min = st.number_input("Power 5min (W)", 100, 2000, 350, key="p5min")
        p12min = st.number_input("Power 12min (W)", 100, 2000, 300, key="p12min")
    with col3:
        athlete_name = st.text_input("Athletenname", placeholder="Name eingeben", key="athlete_name")
        sprint_dur = st.number_input("Sprintdauer (s)", 10, 30, 20, key="sprint_dur")
        avg20 = st.number_input("20s Ø-Leistung (W)", 200, 2500, 650, key="avg20")
        peak20 = st.number_input("20s Peak-Leistung (W)", 300, 3000, 900, key="peak20")

    submitted = st.form_submit_button("Analyse starten 🚀")

if submitted:
    if not athlete_name.strip():
        st.warning("Bitte **Athletenname** eingeben.")
    else:
        inputs = dict(
            gender=gender, weight=weight, bodyfat=bodyfat, hfmax=hfmax,
            p1min=p1min, p3min=p3min, p5min=p5min, p12min=p12min,
            sprint_dur=sprint_dur, avg20=avg20, peak20=peak20
        )
        st.session_state["inputs"] = inputs
        st.session_state["athlete_name"] = athlete_name
        st.session_state["results"] = compute_analysis(inputs)
        st.success("Analyse berechnet – siehe unten.")

# ---------- show results if available ----------
if "results" in st.session_state:
    athlete_name = st.session_state.get("athlete_name", "")
    r = st.session_state["results"]

    st.subheader("🔢 Leistungskennzahlen")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CP", f"{r['cp']:.0f} W")
    m2.metric("W′", f"{r['w_prime']:.0f} J")
    m3.metric("VO₂max rel.", f"{r['vo2_rel']:.1f} ml/min/kg")
    m4.metric(f"VLaMax ({r['model_used']})", f"{r['vlamax']:.3f} mmol/l/s")
    st.caption("VO₂: Formel B = 7 + 10.8 × (P5/kg)")

    st.subheader("📊 Ergebnisse")
    df = pd.DataFrame({
        "Parameter": [
            "Datum", "Name", "CP", "W′", "VO₂max (l/min)", "VO₂max rel. (ml/min/kg)",
            "VLaMax", "FatMax (W)", "FatMax (%CP)",
            "Empf. GA1-Zone (W)", "Empf. GA1-Zone (%CP)", "Athletentyp"
        ],
        "Wert": [
            str(date.today()), athlete_name, r['cp'], r['w_prime'], round(r['vo2_abs'],2), round(r['vo2_rel'],1),
            round(r['vlamax'],3), f"{round(r['fatmax_w'],1)}", f"{round((r['fatmax_w']/r['cp'])*100,1)} %",
            f"{int(r['ga1_min'])}–{int(r['ga1_max'])}", f"{round(r['ga1_pct_min'],1)}–{round(r['ga1_pct_max'],1)} %", r['athlete_type']
        ]
    })
    st.markdown(tabulate(df, headers='keys', tablefmt='github', showindex=False))

    st.subheader("🏁 Trainingszonen (dynamisch: CP + VLamax + FatMax)")
    st.dataframe(r['zones_df'], use_container_width=True)
    st.markdown(r['zones_df'].to_markdown(index=False))

    st.subheader("🎯 Dashboard Visuals")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**VLamax Gauge**")
        fig, ax = plt.subplots(figsize=(4,2))
        ax.barh([0], [r['vlamax']], height=0.4)
        ax.set_xlim(0,1); ax.set_yticks([]); ax.set_xlabel("mmol/l/s")
        ax.text(min(max(r['vlamax'],0),1), 0, f"{r['vlamax']:.2f}", va="center", ha="center")
        st.pyplot(fig)
    with c2:
        st.markdown("**VO₂max Gauge**")
        fig, ax = plt.subplots(figsize=(4,2))
        lo, hi = 40, 80
        val = max(lo, min(hi, r['vo2_rel']))
        ax.barh([0], [val-lo], height=0.4)
        ax.set_xlim(0, hi-lo); ax.set_yticks([]); ax.set_xlabel("ml/min/kg (40–80)")
        ax.text(val-lo, 0, f"{r['vo2_rel']:.1f}", va="center", ha="center")
        st.pyplot(fig)

    st.markdown("**FatMax & Zonen (W)**")
    fig, ax = plt.subplots(figsize=(8,1.5))
    ga1_lo, ga1_hi = r['ga1_min'], r['ga1_max']
    ga2_lo, ga2_hi = ga1_lo if ga1_lo < ga1_hi else ga1_hi, 0.90*r['cp']
    ax.hlines(0, ga1_lo, ga1_hi, linewidth=10)
    ax.hlines(0, ga2_lo, ga2_hi, linewidth=10)
    ax.plot([r['fatmax_w']], [0], marker="o")
    ax.set_xlim(0, r['cp']*1.1); ax.set_yticks([]); ax.set_xlabel("Watt")
    st.pyplot(fig)

    st.subheader("📈 Critical Power Kurve")
    t_pts = np.array([t for t,_ in r['pts']], dtype=float) if r['pts'] else np.array([ ])
    p_pts = np.array([p for _,p in r['pts']], dtype=float) if r['pts'] else np.array([ ])
    fig, ax = plt.subplots()
    t_curve = np.linspace(15, 1200, 200)
    p_curve = r['cp'] + (r['w_prime'] / t_curve)
    ax.plot(t_curve, p_curve, label="CP-Modell")
    if r['pts']:
        ax.scatter(t_pts, p_pts, label="Messpunkte")
    ax.set_xscale("log")
    ax.set_xlabel("Dauer (s) (log)"); ax.set_ylabel("Leistung (W)")
    ax.legend()
    st.pyplot(fig)

    # ----- Export (stable, session-based) -----
    st.subheader("📄 Export")
    if st.button("PDF exportieren"):
        try:
            pdf_bytes = create_analysis_pdf_bytes(
                athlete_name, r['vo2_rel'], r['vlamax'], r['cp'], r['w_prime'], r['fatmax_w'],
                (r['ga1_min'], r['ga1_max']), (r['ga1_max'], 0.90*r['cp']), pts=r['pts']
            )
            st.success("PDF erstellt.")
            st.download_button(
                "📄 PDF herunterladen",
                data=pdf_bytes,
                file_name=f"{athlete_name or 'analyse'}_{date.today().isoformat()}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF-Erstellung fehlgeschlagen: {e}")
