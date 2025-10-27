import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
from tabulate import tabulate


#from calculations.critical_power import calc_critical_power
from calculations.critical_power import calc_critical_power, corrected_ftp
from calculations.vo2max import calc_vo2max
from calculations.vlamax_exact import calc_vlamax_exact_with_ffm
from calculations.vlamax import calc_vlamax as calc_vlamax_classic
from calculations.fatmax import calc_fatmax
from calculations.zones import calc_zones, calc_ga1_zone
from utils.athlete_type import determine_athlete_type
from pdf_export import create_analysis_pdf_bytes




st.set_page_config(page_title="Performance Analyzer", page_icon="🚴", layout="wide")
st.sidebar.markdown("**Version:** 1.9.9e4 (Neutral • SessionState + Dynamic Zones + PDF in-memory)**")

# ---------- helpers ----------
def compute_analysis(inputs: dict):
    gender = inputs['gender']
    weight = inputs['weight']
    bodyfat = inputs['bodyfat']
    birth_date = inputs['birth_date']
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
    ftp_corr = corrected_ftp(cp, vlamax) if "vlamax" in locals() else cp
    vo2_abs, vo2_rel = calc_vo2max(p5min, weight, gender, method="B")  # 7 + 10.8*(P5/kg)
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
        "ftp_corr": ftp_corr,
        "weight": weight,
        "birth_date": inputs["birth_date"],
        "w_prime": w_prime,
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
        birth_date = st.date_input("Geburtsdatum", key="birth_date")
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
    


if "results" not in st.session_state or st.session_state["results"] is None:
    st.title("🚴 Performance Analyzer")
    st.write("Willkommen im 360 Coaching Lab Analyzer. \
              Bitte gib deine Daten ein und starte die Analyse, \
              um deine Ergebnisse zu sehen.")












# --- Nur anzeigen, wenn eine Analyse durchgeführt wurde ---
if "results" in st.session_state and st.session_state["results"] is not None:
    r = st.session_state["results"]

    # 🔽 alles, was erst nach Analyse erscheinen soll:
    st.subheader("🎯 Dashboard Visuals")

    # Beispiel: Kennzahlen
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Critical Power", f"{r['cp']:.0f} W")
        st.metric("VO₂max", f"{r['vo2_rel']:.1f} ml/kg/min")
    with c2:
        st.metric("VLamax", f"{r['vlamax']:.3f} mmol/l/s")
        st.metric("FatMax", f"{r['fatmax_w']:.0f} W")

    # Beispiel: Diagramme, Tabellen usw.
    st.subheader("📊 Leistungsdiagramme")
    # (dein weiterer Code für CP-Kurve, FatMax-Kurve, Zonen, usw.)

else:
    # Startseite ohne Analyse
    st.info("Bitte zuerst Daten eingeben und auf **'Analyse starten 🚀'** klicken, um die Ergebnisse anzuzeigen.")






if submitted:
    if not st.session_state["athlete_name"].strip():
        st.warning("Bitte **Athletenname** eingeben.")
    else:
        inputs = dict(
            gender=st.session_state["gender"], weight=st.session_state["weight"], bodyfat=st.session_state["bodyfat"], birth_date=st.session_state["birth_date"],
            hfmax=st.session_state["hfmax"], p1min=st.session_state["p1min"], p3min=st.session_state["p3min"],
            p5min=st.session_state["p5min"], p12min=st.session_state["p12min"],
            sprint_dur=st.session_state["sprint_dur"], avg20=st.session_state["avg20"], peak20=st.session_state["peak20"]
        )
        st.session_state["inputs"] = inputs
        st.session_state["athlete_name_val"] = st.session_state["athlete_name"]
        st.session_state["results"] = compute_analysis(inputs)
        st.success("Analyse berechnet – siehe unten.")

# ---------- show results if available ----------
if "results" in st.session_state:
    athlete_name_val = st.session_state.get("athlete_name_val", "")
    r = st.session_state["results"]











st.subheader("⚙️ Leistungskennzahlen")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Critical Power (CP)",
        f"{r['cp']:.0f} W",
        help="Aerobe Dauerleistungsgrenze / MLSS"
    )
    st.metric(
        "W′",
        f"{r['w_prime']:.0f} J",
        help="Anaerober Energievorrat oberhalb der CP"
    )

with col2:
    st.metric(
        "Functional Threshold Power (FTP)",
        f"{r['ftp']:.0f} W",
        help="Praxiswert für 60-Minuten-Leistung, abhängig von VLamax"
    )
    st.metric(
        "FTP (W/kg)",
        f"{r['ftp'] / float(inputs.get('weight', 70)):.2f}",
        help="Relativer Schwellenwert"
    )

with col3:
    st.metric(
        "VLamax",
        f"{vlamax:.3f} mmol/l/s",
        help="Maximale Laktatbildungsrate – beeinflusst FTP deutlich stärker als CP"
    )

# --- Hinweis für TrainingPeaks ---
st.info(
    f"""
    💡 **Hinweis für TrainingPeaks:**  
    Verwende für die Trainingszonen in TrainingPeaks die hier berechnete  
    **Functional Threshold Power (FTP) = {r['ftp']:.0f} W**.  
    Dieser Wert berücksichtigt deine VLamax und bildet deine reale 60-min-Schwelle ab.
    """
)






# ============================================================
# ⚙️ Leistungsanalyse – Critical Power, W′ & FTP
# ============================================================

from calculations.critical_power import calc_critical_power, corrected_ftp

# --- Eingabedaten aus Formular / Session ---
p1min  = float(inputs.get("p1min", 0))
p3min  = float(inputs.get("p3min", 0))
p5min  = float(inputs.get("p5min", 0))
p12min = float(inputs.get("p12min", 0))
vlamax = float(inputs.get("vlamax", 0))
weight = float(inputs.get("weight", 70))

# ============================================================
# 🔹 1. Berechnung von CP und W′ (nur 1–12 min Tests)
# ============================================================
cp, w_prime = calc_critical_power(
    p1min=p1min,
    p3min=p3min,
    p5min=p5min,
    p12min=p12min
)

# ============================================================
# 🔹 2. Berechnung der FTP (metabolisch modelliert)
# ============================================================
ftp = corrected_ftp(cp, vlamax)

# ============================================================
# 🔹 3. Ergebnisse speichern
# ============================================================
r["cp"] = cp
r["w_prime"] = w_prime
r["ftp"] = ftp

# ============================================================
# 🔹 4. Anzeige der Ergebnisse
# ============================================================
st.subheader("⚙️ Leistungskennzahlen")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Critical Power (CP)", f"{r['cp']:.0f} W", help="Aerobe Dauerleistungsgrenze (MLSS-Niveau)")
    st.metric("W′", f"{r['w_prime']:.0f} J", help="Anaerober Energievorrat oberhalb der CP")

with c2:
    st.metric("Functional Threshold Power (FTP)", f"{r['ftp']:.0f} W", help="60-Minuten-Leistung für Trainingszonen und TrainingPeaks")
    st.metric("FTP (W/kg)", f"{r['ftp']/weight:.2f}", help="Relativer Schwellenwert (Leistung pro kg Körpergewicht)")

with c3:
    st.metric("VLamax", f"{vlamax:.3f} mmol/l/s", help="Maximale Laktatbildungsrate – beeinflusst FTP und Trainingsschwelle")
    st.metric("FTP / CP Verhältnis", f"{(r['ftp']/r['cp']*100):.1f} %", help="Verhältnis zeigt aerobe Stabilität (niedriger bei Sprintern)")









    st.subheader("📊 Ergebnisse")
    df = pd.DataFrame({
        "Parameter": [
            "Datum", "Name", "Geburtsdatum", "Gewicht", "Körperfett", "CP", "W′", "FTP", "FTP W/kg", "VO₂max rel. (ml/min/kg)", "VO₂max (l/min)",
            "VLaMax", "FatMax (W)", "FatMax (%CP)",
            "Athletentyp"
        ],
        "Wert": [
            str(date.today()), athlete_name_val, str(r["birth_date"]), weight, bodyfat, round(r['cp']), round(r['w_prime']), round(r['ftp_corr']), f"{r['ftp_corr']/r['weight']:.2f}", round(r['vo2_rel'],1), round(r['vo2_abs'],2),
            round(r['vlamax'],3), f"{round(r['fatmax_w'],1)}", f"{round((r['fatmax_w']/r['cp'])*100,1)} %",
            r['athlete_type']
        ]
    })
    st.markdown(tabulate(df, headers='keys', tablefmt='github', showindex=False))

#   st.subheader("🏁 Trainingszonen)")
#   st.dataframe(r['zones_df'], use_container_width=True)
#   st.markdown(r['zones_df'].to_markdown(index=False))

    # ---------- NEUER ZONEN-ABSCHNITT ----------
    st.subheader("🏁 Trainingszonen")

    # Berechnung (aus neuer zones.py)
    # zones = calc_zones(r['cp'], hfmax=None, fatmax_w=r['fatmax_w'], vlamax=r['vlamax'])
    zones = calc_zones(r["cp"], None, r["fatmax_w"], r["vlamax"])

    # Anzeige
    st.dataframe(zones, use_container_width=True)
    # st.markdown(zones.to_markdown(index=False))



st.markdown("""
## 🧭 Ergebnisse & Trainingszonen – Erklärung

---

### **Körperfett (%)**
Gibt an, wie viel Prozent des Körpergewichts aus Fett besteht.  
Ein niedriger Wert verbessert die Leistungsökonomie (W/kg),  
zu niedrige Werte können jedoch Regeneration und Hormonhaushalt beeinträchtigen.  
Für Ausdauerathlet:innen gelten **8–14 % (Männer)** und **15–22 % (Frauen)** als optimal.

---

### **Critical Power (CP)**
Die **Critical Power** ist die höchste Leistung, die über längere Zeit (20–60 min)  
ohne fortschreitende Ermüdung gehalten werden kann.  
Sie beschreibt die **aerobe Dauerleistungsgrenze** (≈ anaerobe Schwelle, MLSS).  
Je höher die CP, desto besser die Ausdauerleistung.

---

### **W′ (W-Prime)**
W′ repräsentiert den **anaeroben Energievorrat** oberhalb der CP.  
Ein hoher Wert zeigt eine gute Fähigkeit für Sprints und Attacken,  
ein niedriger Wert steht für hohe aerobe Effizienz und Ökonomie.

---

### **FTP (Functional Threshold Power)**
Praxiswert für die Schwellenleistung, meist ≈ 95 % der 20-min-Leistung.  
Sie zeigt, wie lange eine hohe Dauerleistung aufrechterhalten werden kann  
und dient als Grundlage zur Trainingszoneneinteilung.

---

### **FTP (W/kg)**
Die relative Schwellenleistung (FTP ÷ Körpergewicht)  
ist der wichtigste Vergleichswert zwischen Athlet:innen.  
- Freizeit: **2.0–3.0 W/kg**  
- Ambitioniert: **3.0–4.0 W/kg**  
- Elite: **> 5.0 W/kg**

---

### **VO₂max (relativ, ml/min/kg)**
Misst die aerobe Kapazität – wie viel Sauerstoff pro Minute und kg Körpergewicht  
verwertet werden kann.  
- Untrainiert: 35–45  
- Trainiert: 50–60  
- Elite: > 70 ml/min/kg

---

### **VO₂max (absolut, l/min)**
Zeigt die gesamte Sauerstoffaufnahme unabhängig vom Körpergewicht.  
Je höher, desto besser Herz-Kreislauf-Leistung und O₂-Transportkapazität.

---

### **VLamax (mmol/l/s)**
Die **maximale Laktatbildungsrate** beschreibt die anaerobe Stoffwechselaktivität.  
- **Niedrig (0.2–0.4):** effizient, ausdauerorientiert  
- **Hoch (0.6–1.0):** sprintstark, aber geringere Ausdauer  
Ein optimales Verhältnis aus **VO₂max und VLamax** bestimmt die Leistungsfähigkeit.

---

### **FatMax (Watt)**
Leistung, bei der die **Fettverbrennung maximal** ist – meist **60–70 % der CP**.  
Training in diesem Bereich verbessert die aerobe Effizienz und Fettstoffwechselkapazität.

---

### **FatMax (% CP)**
Zeigt, wie nah FatMax an der Schwelle liegt.  
Ein hoher Prozentsatz bedeutet, dass auch bei höherer Intensität  
noch effizient Fett genutzt werden kann – Zeichen einer starken aeroben Anpassung.

---

### **Athletentyp**
Bestimmt aus VO₂max, VLamax und CP:
- **Dieseltyp / Ausdauertyp:** hohe CP, niedrige VLamax → sehr effizient  
- **Allrounder:** ausgeglichenes Profil  
- **Sprinter / Explosivtyp:** hohe VLamax, niedrige CP → explosiv, weniger ökonomisch

---

## 🏁 Trainingszonen

**Z1 – Regeneration**  
Sehr lockere Belastung zur aktiven Erholung, fördert Durchblutung und Regeneration.  
Perfekt nach intensiven Trainingstagen oder Rennen.

**Z2 – Ausdauer (Fettstoffwechsel)**  
Klassisches Grundlagentraining (GA1).  
Maximale Fettverbrennung, Verbesserung der aeroben Kapazität und Mitochondriendichte.  
Lange, konstante Einheiten (1.5 – 4 h).

**Z3 – Tempo**  
Übergangsbereich (GA2).  
Leicht erhöhte Herzfrequenz, Kombination aus Fett- und Kohlenhydratstoffwechsel.  
Ideal zur Verbesserung der Ermüdungsresistenz und Toleranz anhaltender Belastung.

**Z4 – Schwelle**  
Bereich um CP / FTP / MLSS.  
Hohe, aber noch kontrollierte Intensität.  
Verbessert Laktattoleranz, Dauerleistungsfähigkeit und aerobe Effizienz.

**Z5 – VO₂max**  
Sehr intensive Intervalle nahe der maximalen Sauerstoffaufnahme.  
Trainiert Herz-Kreislauf-System und maximale Sauerstoffverwertung.  
Kurze Belastungen (2–6 min), lange Pausen.

---

## 🔢 RPE-Skala (0 – 10)

| RPE | Empfinden | Beschreibung |
|:----|:-----------|:--------------|
| 0 | Ruhe | keine Belastung |
| 1–2 | sehr leicht | Einrollen, Erholung |
| 3–4 | leicht – mäßig | GA1, Gespräche möglich |
| 5 | mittel | GA2, gleichmäßige Atmung |
| 6 | etwas hart | Übergang zu Schwelle |
| 7 | hart | FTP-Intervalle, 10–20 min |
| 8 | sehr hart | VO₂max-Intervalle |
| 9 | maximal | kurze Spitzenbelastung |
| 10 | absolut maximal | Sprint / Endbelastung |

---
""", unsafe_allow_html=True)






st.subheader("🎯 Dashboard Visuals")

# Nur anzeigen, wenn Analyseergebnisse vorhanden sind
if "results" not in st.session_state or not st.session_state["results"]:
    st.info("🔍 Noch keine Analyse durchgeführt. Bitte zuerst Daten eingeben und auf 'Analyse starten 🚀' klicken.")
else:
    r = st.session_state["results"]  # Ergebnisse laden

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**VLamax**")
        fig, ax = plt.subplots(figsize=(4,2))
        ax.barh([0], [r['vlamax']], height=0.4)
        ax.set_xlim(0,1)
        ax.set_yticks([])
        ax.set_xlabel("mmol/l/s")
        ax.text(min(max(r['vlamax'],0),1), 0, f"{r['vlamax']:.2f}", va="center", ha="center")
        st.pyplot(fig)

    with c2:
        st.markdown("**VO₂max (ml/min/kg)**")
        fig, ax = plt.subplots(figsize=(4, 2))

        lo, hi = 45, 85
        val = max(lo, min(hi, r['vo2_rel']))

        # Farbverlauf
        color_zones = [
            (lo, 55, "#b3d9ff"),
            (55, 65, "#80ffaa"),
            (65, 75, "#ffff80"),
            (75, 85, "#ff9966"),
        ]
        for start, end, color in color_zones:
            ax.axvspan(start, end, color=color, alpha=0.6)

        ax.barh([0], [val - lo], left=lo, height=0.35, color="#007a00")
        ax.set_xlim(lo, hi)
        ax.set_yticks([])
        ax.set_xlabel("ml/min/kg")
        ax.text(val, 0, f"{r['vo2_rel']:.1f}", va="center", ha="center", fontsize=10, fontweight="bold")
        st.pyplot(fig)





import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.markdown("**Fett- & Kohlenhydratverbrennung (kcal/h & g/h)**")
fig, ax1 = plt.subplots(figsize=(8, 5))

# ---------------------------
# Grundparameter
# ---------------------------
# --- Check if results exist ---
if "results" in st.session_state and st.session_state["results"] is not None:
    r = st.session_state["results"]

    # deine bisherigen Berechnungen und Grafiken:
    cp      = float(r.get("cp", 280))
    fatmax  = float(r.get("fatmax_w", 0.65 * cp))
    vlamax  = float(r.get("vlamax", 0.5))
    ...
else:
    st.info("Bitte zuerst eine Analyse durchführen, um die Ergebnisse anzuzeigen.")



cp = float(r.get("cp", 280))
fatmax = float(r.get("fatmax_w", 0.65 * cp))
vlamax = float(r.get("vlamax", 0.5))
ga1_lo = float(r.get("ga1_min", 0.55 * cp))
ga1_hi = float(r.get("ga1_max", 0.75 * cp))

# Leistungsskala
x = np.linspace(50, cp * 1.2, 400)  # W

# ---------------------------
# Modellierte Substratverteilung
# ---------------------------

# Fettverbrennung: Peak bei FatMax, danach starker Abfall (abhängig von VLamax)
steepness = np.clip(2.0 + (vlamax - 0.4) * 3.0, 1.8, 4.0)
width_factor = np.clip(0.1 + (0.5 - vlamax) * 0.03, 0.06, 0.12)

left_width = width_factor * 1.6
right_width = width_factor * 0.7

y_fat_rel = np.where(
    x < fatmax,
    np.exp(-((fatmax - x) / (left_width * cp)) ** steepness),
    np.exp(-((x - fatmax) / (right_width * cp)) ** (steepness * 1.2))
)
y_fat_rel = y_fat_rel / np.nanmax(y_fat_rel)  # 0–1 normiert

# Gesamtenergieumsatz: ca. 3.6 kcal pro Watt pro Stunde
total_kcal = x * 3.6

# Fett- und KH-Anteile in kcal/h
fat_kcal = total_kcal * y_fat_rel
carb_kcal = total_kcal - fat_kcal

# ---------------------------
# Kurven zeichnen (linke Achse = kcal/h)
# ---------------------------
ax1.plot(x, fat_kcal, color="#006600", linewidth=2.5, label="Fett (kcal/h)")
ax1.plot(x, carb_kcal, color="#cc3300", linewidth=2.5, label="Kohlenhydrate (kcal/h)")
ax1.fill_between(x, 0, fat_kcal, color="#00cc66", alpha=0.1)
ax1.fill_between(x, 0, carb_kcal, color="#ff9966", alpha=0.1)

# FatMax-Zone
ax1.axvspan(ga1_lo, ga1_hi, color="#b3ffb3", alpha=0.4, label="FatMax-Zone")
ax1.axvline(fatmax, color="#004d00", linestyle="--", linewidth=1.3)
ax1.text(fatmax, np.max(fat_kcal)*1.02, f"FatMax = {fatmax:.0f} W",
            ha="center", fontsize=9, color="#004d00")

# ---------------------------
# Rechte Achse: g/h
# ---------------------------
ax2 = ax1.twinx()
ax2.set_ylabel("g/h")

# Umrechnungsfaktoren:
# 1 g Fett ≈ 9.4 kcal, 1 g KH ≈ 4.2 kcal
fat_gph = fat_kcal / 9.4
carb_gph = carb_kcal / 4.2

ax2.plot(x, fat_gph, color="#006600", alpha=0.0)  # unsichtbar, Achsenskalierung übernehmen
ax2.plot(x, carb_gph, color="#cc3300", alpha=0.0)

# Max. Carb-Intake-Bereich (90–120 g/h)
ax2.axhspan(90, 120, color="#ffcc99", alpha=0.4, label="Max. KH-Aufnahme")

# ---------------------------
# Layout
# ---------------------------
ax1.set_xlim(50, cp * 1.2)
ax1.set_ylim(0, np.max(total_kcal) * 1.1)
ax1.set_xlabel("Leistung (Watt)")
ax1.set_ylabel("Energieumsatz (kcal/h)")
ax1.set_title("Fat & carbohydrate combustion")
ax1.grid(alpha=0.3)
ax1.legend(loc="upper left", fontsize=8)
ax2.legend(loc="upper right", fontsize=8)

st.pyplot(fig)






import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.markdown("**FatMax & Zonen (W)**")
fig, ax = plt.subplots(figsize=(8, 4))

# --- Werte aus Analyse ---
cp = float(r.get("cp", 300))
fatmax = float(r.get("fatmax_w", 0.65 * cp))
vlamax = float(r.get("vlamax", 0.5))
ga1_lo = float(r.get("ga1_min", 0.55 * cp))
ga1_hi = float(r.get("ga1_max", 0.75 * cp))
ga2_lo, ga2_hi = ga1_hi, 0.9 * cp

# --- Leistungsskala ---
x = np.linspace(0.01, cp * 1.1, 400)

# --- VLamax-Einfluss auf Kurvenform ---
steepness = 2.0 + (vlamax - 0.4) * 3.0     # 1.8–4.0
steepness = np.clip(steepness, 1.8, 4.0)
width_factor = 0.10 + (0.5 - vlamax) * 0.03  # 0.06–0.12
width_factor = np.clip(width_factor, 0.06, 0.12)

# --- Asymmetrische Fettstoffwechsel-Kurve ---
left_width = width_factor * 1.6     # sanfter Anstieg
right_width = width_factor * 0.7    # steiler Abfall
y_fat = np.where(
    x < fatmax,
    np.exp(-((fatmax - x) / (left_width * cp)) ** steepness),
    np.exp(-((x - fatmax) / (right_width * cp)) ** (steepness * 1.2))
)
y_fat = (y_fat / np.nanmax(y_fat)) * 100  # normiert auf 0–100 %

# --- Kohlenhydratstoffwechsel (rote Gegenkurve) ---
y_carb = 100 - y_fat

# --- Crossover-Punkt berechnen ---
cross_idx = np.argmin(np.abs(y_fat - y_carb))
cross_x, cross_y = x[cross_idx], y_fat[cross_idx]

# --- Hintergrundzonen ---
ax.axvspan(ga1_lo, ga1_hi, color="#b3ffb3", alpha=0.35, label="GA1 (Fettstoffwechsel)")
ax.axvspan(ga2_lo, ga2_hi, color="#ffff99", alpha=0.35, label="GA2 (Übergang)")

# --- Kurven zeichnen ---
ax.plot(x, y_fat, color="#007a00", linewidth=2.5, label="Fettstoffwechsel")
ax.plot(x, y_carb, color="#cc0000", linewidth=2.0, linestyle="--", label="Kohlenhydratstoffwechsel")

# --- FatMax-Linie ---
ax.axvline(fatmax, color="#004d00", linestyle="--", linewidth=1.3)
ax.text(fatmax, 104, f"FatMax = {fatmax:.0f} W", ha="center", fontsize=9, color="#004d00")

# --- Crossover-Punkt ---
ax.scatter(cross_x, cross_y, color="black", s=30, zorder=5)
ax.text(cross_x, cross_y + 6, f"Crossover ≈ {cross_x:.0f} W", ha="center", fontsize=8, color="black")

# --- Achsen & Layout ---
ax.set_xlim(0, cp * 1.1)
ax.set_ylim(0, 110)
ax.set_xlabel("Leistung (W)")
ax.set_ylabel("Substratanteil (% vom Maximum)")
ax.set_title("Substratverwendung in Abhängigkeit der Leistung")
ax.grid(alpha=0.3)
ax.legend(loc="upper right", fontsize=8)

st.pyplot(fig)









# --- Fat & carbohydrate combustion (optimized physiological version) ---
st.markdown("**Fat & carbohydrate combustion**")
fig, ax1 = plt.subplots(figsize=(8, 5))

# ---------------------------
# Basisparameter
# ---------------------------
cp      = float(r.get("cp", 280))
fatmax  = float(r.get("fatmax_w", 0.65 * cp))
vlamax  = float(r.get("vlamax", 0.5))
ga1_lo  = float(r.get("ga1_min", 0.55 * cp))
ga1_hi  = float(r.get("ga1_max", 0.75 * cp))

x = np.linspace(40, 1.5 * cp, 600)  # Leistung (Watt)

# ---------------------------
# 1️⃣ Gesamtenergie (kcal/h)
# ---------------------------
total_kcal = x * 3.6

# ---------------------------
# 2️⃣ Fettkurve: früher Anstieg, flacher Verlauf, schneller Abfall nach FatMax
# ---------------------------
# Linker Anstieg: weiche Sättigung (langsames Plateau)
# Rechter Abfall: exponentiell (schnell abnehmend nach FatMax)
a = 4.0   # bestimmt Anstiegsgeschwindigkeit
b = np.clip(12 * vlamax, 6, 18)  # steiler Abfall bei hoher VLamax
fat_share = (1 - np.exp(-x / (0.3 * cp))) * np.exp(-((x - fatmax) / (0.25 * cp))**2)
fat_share[x > cp] = 0
fat_share /= np.nanmax(fat_share)
fat_kcal = total_kcal * fat_share * 0.8  # Peak ca. 80 % der Gesamtenergie

# ---------------------------
# 3️⃣ KH-Kurve: exponentiell steigend, vor allem ab FatMax / CP
# ---------------------------
x_norm = x / cp
carb_kcal = total_kcal * (0.15 + 0.85 * (1 - np.exp(-4.5 * (x_norm - 0.3))))
carb_kcal = np.clip(carb_kcal, 0, None)

# ---------------------------
# 4️⃣ Plot (kcal/h, linke Achse)
# ---------------------------
ax1.plot(x, fat_kcal,  color="#007a00", linewidth=2.5, label="fat (kcal/h)")
ax1.plot(x, carb_kcal, color="#cc3300", linewidth=2.5, label="carbohydrate (kcal/h)")
ax1.fill_between(x, 0, fat_kcal,  color="#00cc66", alpha=0.15)
ax1.fill_between(x, 0, carb_kcal, color="#ff9966", alpha=0.10)

# FatMax-Zone
ax1.axvspan(ga1_lo, ga1_hi, color="#b3ffb3", alpha=0.35, label="FatMax zone")
ax1.axvline(fatmax, color="#004d00", linestyle="--", linewidth=1.2)
ax1.text(fatmax, np.interp(fatmax, x, fat_kcal)*1.05, f"FatMax = {fatmax:.0f} W",
         ha="center", fontsize=9, color="#004d00")

# ---------------------------
# 5️⃣ Rechte Achse (g/h)
# ---------------------------
ax2 = ax1.twinx()
ax2.set_ylabel("g/h")
fat_gph  = fat_kcal  / 9.4
carb_gph = carb_kcal / 4.2
yl0, yl1 = ax1.get_ylim()
ax2.set_ylim(yl0/4.2, yl1/4.2)
ax2.axhspan(90, 120, color="#ffcc99", alpha=0.35, label="max. carb. intake")

# ---------------------------
# Layout
# ---------------------------
ax1.set_xlim(x.min(), x.max())
ax1.set_xlabel("Leistung (Watt)")
ax1.set_ylabel("Energieumsatz (kcal/h)")
ax1.set_title("Fat & carbohydrate combustion")
ax1.grid(alpha=0.3)
ax1.legend(loc="upper left", fontsize=8)
ax2.legend(loc="upper right", fontsize=8)

st.pyplot(fig)

















st.subheader("📈 Critical Power Kurve")

pts = r["pts"]  # reale Datenpunkte
if pts:
    t_pts = np.array([t for t, _ in pts], dtype=float)
    p_pts = np.array([p for _, p in pts], dtype=float)

    fig, ax = plt.subplots(figsize=(7, 4))

        # Modellierte Kurve (1/t-Beziehung)
    t_curve = np.linspace(10, 1200, 300)
    p_curve = r["cp"] + (r["w_prime"] / t_curve)

        # --- Farbige Hintergrundzonen (auf Basis der CP-Zonen) ---
    cp = r["cp"]
    z_colors = [
        (0, 0.55 * cp, "#b3d9ff", "Z1"),       # blau, locker
        (0.55 * cp, 0.75 * cp, "#c2f0c2", "Z2"), # grün, Fettstoffwechsel
        (0.75 * cp, 0.90 * cp, "#ffffb3", "Z3"), # gelb, Übergang
        (0.90 * cp, 1.05 * cp, "#ffd699", "Z4"), # orange, Schwelle
        (1.05 * cp, 1.25 * cp, "#ff9999", "Z5"), # rot, VO2max
    ]
    for (low, high, color, label) in z_colors:
        ax.axhspan(low, high, color=color, alpha=0.3, label=label)

        # Reale Messpunkte
    ax.scatter(t_pts, p_pts, color="blue", label="Testdaten", zorder=4, s=40)

        # Modellierte Kurve
    ax.plot(t_curve, p_curve, color="red", linewidth=2.2, label="CP-Modell", zorder=3)

        # CP-Linie
    ax.axhline(cp, color="gray", linestyle="--", linewidth=1)
    ax.text(t_curve[-1], cp + 5, f"CP = {cp:.0f} W", va="bottom", ha="right", fontsize=9, color="gray")

        # Achsen + Layout
        # Achse logarithmisch, aber lesbare Sekundenwerte anzeigen
    ax.set_xscale("log")
    ax.set_xlabel("Dauer (s)")

        # Definierte Tick-Positionen (typische Testzeiten)
    xticks = [20, 60, 180, 300, 600, 900, 1200]
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(int(x)) for x in xticks])
    ax.set_ylabel("Leistung (W)")
    ax.set_title("Critical Power Modell mit Zonen")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

        # Legende schöner (nur einmal pro Zone)
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc="upper right", fontsize=8)

    st.pyplot(fig)

else:
    st.info("Keine ausreichenden Testpunkte für CP-Kurve vorhanden.")






    # ----- Export -----
    st.subheader("📄 Export")
    if st.button("PDF exportieren"):
        try:
            pdf_bytes = create_analysis_pdf_bytes(
                athlete_name_val, r['vo2_rel'], r['vlamax'], r['cp'], r['w_prime'], r['fatmax_w'],
                (r['ga1_min'], r['ga1_max']), (r['ga1_max'], 0.90*r['cp']), pts=r['pts']
            )
            st.success("PDF erstellt.")
            st.download_button(
                "📄 PDF herunterladen",
                data=pdf_bytes,
                file_name=f"{athlete_name_val or 'analyse'}_{date.today().isoformat()}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF-Erstellung fehlgeschlagen: {e}")


