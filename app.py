# app.py — 360 Coaching Lab • Performance Analyzer (v1.9.9 clean)
# CP nur aus 1/3/5/12 min • FTP stark VLamax-abhängig • Zonen/Grafiken/PDF

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from tabulate import tabulate

# -----------------------------
# Page / Session
# -----------------------------
st.set_page_config(page_title="Performance Analyzer", page_icon="🚴", layout="wide")
st.sidebar.markdown("**Version:** 1.9.9 (CP: 1/3/5/12 • FTP ~ VLamax)")

if "results" not in st.session_state:
    st.session_state["results"] = None

# -----------------------------
# Imports (robust)
# -----------------------------
try:
    from calculations.critical_power import calc_critical_power, corrected_ftp
except Exception:
    st.error("❌ Importfehler: calculations/critical_power.py nicht gefunden/fehlerhaft.")
    st.stop()

try:
    from calculations.vo2max import calc_vo2max
    from calculations.vlamax_exact import calc_vlamax_exact_with_ffm
    from calculations.vlamax import calc_vlamax as calc_vlamax_classic
    from calculations.fatmax import calc_fatmax
    from calculations.zones import calc_zones, calc_ga1_zone
    from utils.athlete_type import determine_athlete_type
    from pdf_export import create_analysis_pdf_bytes
except Exception as e:
    st.error(f"❌ Importfehler in Kalkulations-Modulen: {e}")
    st.stop()

# -----------------------------
# Compute
# -----------------------------
def compute_analysis(inputs: dict) -> dict:
    gender     = inputs["gender"]
    weight     = float(inputs["weight"])
    bodyfat    = float(inputs["bodyfat"])
    birth_date = inputs["birth_date"]
    hfmax      = inputs["hfmax"]

    # Leistungsdaten
    p1min  = float(inputs.get("p1min")  or 0.0)
    p3min  = float(inputs.get("p3min")  or 0.0)
    p5min  = float(inputs.get("p5min")  or 0.0)
    p12min = float(inputs.get("p12min") or 0.0)

    # Sprintdaten NUR für VLamax (nicht für CP!)
    sprint_dur = float(inputs["sprint_dur"])
    avg20      = float(inputs["avg20"])
    peak20     = float(inputs["peak20"])

    # Körperzusammensetzung
    ffm = weight * (1 - bodyfat / 100.0)

    # --- VLamax zuerst (wichtig, da FTP davon abhängt)
    try:
        vlamax = calc_vlamax_exact_with_ffm(ffm, avg20, peak20, sprint_dur, gender)
        model_used = "Exact-App"
    except Exception:
        vlamax = calc_vlamax_classic(ffm, avg20, peak20, sprint_dur, gender)
        model_used = "Classic-Fallback"

    # --- VO2max (Formel B: 7 + 10.8 * (P5/kg))
    vo2_abs, vo2_rel = calc_vo2max(p5min, weight, gender, method="B")

    # --- CP/W′ NUR aus 1/3/5/12-min Tests
    # (keine 20 s oder andere Sprints!)
    cp, w_prime = calc_critical_power(
        p1min=p1min if p1min > 0 else None,
        p3min=p3min if p3min > 0 else None,
        p5min=p5min if p5min > 0 else None,
        p12min=p12min if p12min > 0 else None,
    )

    # --- FTP stark VLamax-abhängig
    ftp = corrected_ftp(cp, vlamax)
    ftp_wkg = ftp / weight if weight > 0 else 0.0

    # --- FatMax & Zonen
    fatmax_w, fatmax_pct_ftp, zone_label = calc_fatmax(vo2_rel, vlamax, cp)
    zones_df = calc_zones(cp, hfmax, fatmax_w, vlamax)
    ga1_min, ga1_max, ga1_pct_min, ga1_pct_max = calc_ga1_zone(fatmax_w, cp, vlamax)

    # --- Athletentyp
    athlete_type = determine_athlete_type(vo2_rel, vlamax, cp, weight)

    # --- Punkte für CP-Modell-Plot
    pts = []
    if p1min  > 0: pts.append((60,  p1min))
    if p3min  > 0: pts.append((180, p3min))
    if p5min  > 0: pts.append((300, p5min))
    if p12min > 0: pts.append((720, p12min))

    return {
        "gender": gender, "weight": weight, "bodyfat": bodyfat, "birth_date": birth_date,
        "hfmax": hfmax, "p1min": p1min, "p3min": p3min, "p5min": p5min, "p12min": p12min,
        "vlamax": vlamax, "model_used": model_used,
        "vo2_abs": vo2_abs, "vo2_rel": vo2_rel,
        "cp": cp, "w_prime": w_prime, "ftp": ftp, "ftp_wkg": ftp_wkg,
        "fatmax_w": fatmax_w, "fatmax_pct_ftp": fatmax_pct_ftp,
        "ga1_min": ga1_min, "ga1_max": ga1_max, "ga1_pct_min": ga1_pct_min, "ga1_pct_max": ga1_pct_max,
        "zones_df": zones_df, "athlete_type": athlete_type, "pts": pts
    }

# -----------------------------
# Sidebar – Eingaben
# -----------------------------
st.sidebar.header("Eingaben")

athlete_name = st.sidebar.text_input("Name (optional)", value="")
weight   = st.sidebar.number_input("Körpergewicht (kg)", 40.0, 150.0, 70.0, step=0.1)
bodyfat  = st.sidebar.number_input("Körperfett (%)", 3.0, 40.0, 15.0, step=0.1)
birth_dt = st.sidebar.date_input("Geburtsdatum", value=date(1995, 1, 1))
hfmax    = st.sidebar.number_input("HFmax", 100, 220, 190)

st.sidebar.markdown("---")
st.sidebar.subheader("Leistungstests (All-Out)")
c1, c2 = st.sidebar.columns(2)
with c1:
    p1min  = st.number_input("1-min Power (W)",  0.0, 2000.0, 0.0, step=5.0)
    p5min  = st.number_input("5-min Power (W)",  0.0, 2000.0, 350.0, step=5.0)
with c2:
    p3min  = st.number_input("3-min Power (W)",  0.0, 2000.0, 0.0, step=5.0)
    p12min = st.number_input("12-min Power (W)", 0.0, 2000.0, 300.0, step=5.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Sprintdaten für VLamax")
sprint_dur = st.sidebar.number_input("Sprintdauer (s)", 10, 30, 20)
avg20      = st.sidebar.number_input("20s Ø-Leistung (W)", 200, 2500, 650)
peak20     = st.sidebar.number_input("20s Peak-Leistung (W)", 300, 3000, 900)

st.sidebar.markdown("---")
start = st.sidebar.button("Analyse starten 🚀", use_container_width=True)

# -----------------------------
# Header
# -----------------------------
st.title("🚴 Performance Analyzer")
st.caption("CP aus 1–12 min • FTP stark VLamax-abhängig • Zonen/Grafiken/PDF")

# -----------------------------
# Analyse-Trigger
# -----------------------------
if start:
    # minimaler Check: mind. 2 Zeitpunkte
    n_pts = sum([x > 0 for x in [p1min, p3min, p5min, p12min]])
    if n_pts < 2:
        st.warning("Bitte mindestens **zwei** Testwerte (z. B. 3 & 12 min) eingeben.")
    else:
        inputs = dict(
            gender="Mann",  # optional: ggf. Auswahl nach oben verlegen
            weight=weight, bodyfat=bodyfat, birth_date=birth_dt, hfmax=hfmax,
            p1min=p1min, p3min=p3min, p5min=p5min, p12min=p12min,
            sprint_dur=sprint_dur, avg20=avg20, peak20=peak20
        )
        r = compute_analysis(inputs)
        r["athlete_name"] = athlete_name.strip()
        st.session_state["results"] = r
        st.success("Analyse abgeschlossen. Ergebnisse unten.")

# -----------------------------
# Start-Hinweis
# -----------------------------
if st.session_state["results"] is None:
    st.info("Bitte gib links deine Daten ein und klicke auf **„Analyse starten 🚀“**, um Ergebnisse anzuzeigen.")
    st.stop()

# -----------------------------
# Ergebnisse & Dashboard
# -----------------------------
r = st.session_state["results"]

st.subheader("⚙️ Leistungskennzahlen")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Critical Power (CP)", f"{r['cp']:.0f} W", help="Aerobe Dauerleistungsgrenze (≈ MLSS).")
    st.metric("W′", f"{r['w_prime']:.0f} J", help="Anaerober Energievorrat oberhalb CP.")
with m2:
    st.metric("FTP (60-min)", f"{r['ftp']:.0f} W", help="Für TrainingPeaks als Schwelle eintragen.")
    st.metric("FTP (W/kg)", f"{r['ftp_wkg']:.2f}")
with m3:
    st.metric(f"VLamax ({'Exact' if r['model_used']=='Exact-App' else 'Fallback'})", f"{r['vlamax']:.3f} mmol/l/s")
    st.metric("Körperfett", f"{bodyfat:.1f} %")

st.info(f"💡 **TrainingPeaks:** Trage **FTP = {r['ftp']:.0f} W** als Schwelle ein. (CP ist höher/ähnlich, aber FTP ist die 60-min-Praxisleistung.)")

# -----------------------------
# Ergebnistabelle (kompakt)
# -----------------------------
df_sum = pd.DataFrame({
    "Parameter": [
        "Datum","Athlet","Geburtsdatum","Gewicht","Körperfett",
        "CP","W′","FTP","FTP W/kg","VO₂max rel.","VO₂max abs.",
        "VLamax","FatMax (W)","FatMax (%CP)","Athletentyp"
    ],
    "Wert": [
        date.today().isoformat(),
        r.get("athlete_name",""),
        str(r.get("birth_date","")),
        f"{r['weight']:.1f} kg",
        f"{bodyfat:.1f} %",
        f"{r['cp']:.0f} W",
        f"{r['w_prime']:.0f} J",
        f"{r['ftp']:.0f} W",
        f"{r['ftp_wkg']:.2f}",
        f"{r['vo2_rel']:.1f} ml/kg/min",
        f"{r['vo2_abs']:.2f} l/min",
        f"{r['vlamax']:.3f} mmol/l/s",
        f"{r['fatmax_w']:.0f} W",
        f"{(r['fatmax_w']/r['cp']*100):.1f} %",
        r['athlete_type']
    ]
})
st.markdown(tabulate(df_sum, headers='keys', tablefmt='github', showindex=False))

# -----------------------------
# Trainingszonen (CP-basiert)
# -----------------------------
st.subheader("🏁 Trainingszonen (CP-basiert, VLamax/FatMax berücksichtigt)")
try:
    zones_df = r["zones_df"]
    # zusätzlich Prozentspalten relativ zu CP
    z = zones_df.copy()
    if "von (W)" in z.columns and "bis (W)" in z.columns:
        z["von (%CP)"] = (z["von (W)"] / r["cp"] * 100).round(1)
        z["bis (%CP)"] = (z["bis (W)"] / r["cp"] * 100).round(1)
        cols = ["Zone","von (W)","bis (W)","von (%CP)","bis (%CP)","Beschreibung"]
        z = z[[c for c in cols if c in z.columns]]
    st.dataframe(z, use_container_width=True)
except Exception as e:
    st.warning(f"Zonen konnten nicht angezeigt werden: {e}")






### ✅ **Codeblock: ausführliche Erklärung als Expander**
# -----------------------------
# Ergebnisse & Trainingszonen – Erklärung
# -----------------------------
with st.expander("🧭 Ergebnisse & Trainingszonen – Erklärung (ausklappen)", expanded=False):
    st.markdown("""
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







# -----------------------------
# Dashboard Visuals (VLamax + VO2max Gauges)
# -----------------------------
st.subheader("🎯 Dashboard Visuals")

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
    # farbige Bänder
    for start, end, color in [(lo,55,"#b3d9ff"),(55,65,"#80ffaa"),(65,75,"#ffff80"),(75,85,"#ff9966")]:
        ax.axvspan(start, end, color=color, alpha=0.6)
    ax.barh([0], [val - lo], left=lo, height=0.35, color="#007a00")
    ax.set_xlim(lo, hi); ax.set_yticks([]); ax.set_xlabel("ml/min/kg")
    ax.text(val, 0, f"{r['vo2_rel']:.1f}", va="center", ha="center", fontsize=10, fontweight="bold")
    st.pyplot(fig)

# -----------------------------
# Fat & Carbohydrate combustion (physiologisch)
# -----------------------------
st.markdown("**Fett- & Kohlenhydratverbrennung (kcal/h & g/h)**")
fig, ax1 = plt.subplots(figsize=(8, 5))

cp     = float(r["cp"])
fatmax = float(r["fatmax_w"])
vlamax = float(r["vlamax"])
ga1_lo = float(r["ga1_min"]); ga1_hi = float(r["ga1_max"])

x = np.linspace(40, 1.5*cp, 600)           # Watt
total_kcal = x * 3.6

# Fett: früher Anstieg, dann Plateau, nach FatMax rascher Abfall → 0 bei CP
left_sat   = 1 - np.exp(-x/(0.35*cp))
right_drop = np.exp(-((x - fatmax)/(0.22*cp))**2.2)
fat_share  = left_sat * right_drop
fat_share[x > cp] = 0
fat_share /= np.nanmax(fat_share) + 1e-9
fat_kcal = total_kcal * fat_share * 0.8

# KH: exponentiell steigend (vor allem ab CP)
x_norm = x / cp
carb_kcal = total_kcal * (0.12 + 0.88*(1 - np.exp(-4.8*(x_norm - 0.35))))
carb_kcal = np.clip(carb_kcal, 0, None)

ax1.plot(x, fat_kcal,  color="#007a00", linewidth=2.2, label="Fett (kcal/h)")
ax1.plot(x, carb_kcal, color="#cc3300", linewidth=2.2, label="Kohlenhydrate (kcal/h)")
ax1.fill_between(x, 0, fat_kcal,  color="#00cc66", alpha=0.12)
ax1.fill_between(x, 0, carb_kcal, color="#ff9966", alpha=0.10)

ax1.axvspan(ga1_lo, ga1_hi, color="#b3ffb3", alpha=0.35, label="FatMax-Zone")
ax1.axvline(fatmax, color="#004d00", linestyle="--", linewidth=1.2)
ax1.text(fatmax, np.interp(fatmax, x, fat_kcal)*1.05, f"FatMax = {fatmax:.0f} W",
         ha="center", fontsize=9, color="#004d00")

ax2 = ax1.twinx()
ax2.set_ylabel("g/h")
fat_gph  = fat_kcal  / 9.4
carb_gph = carb_kcal / 4.2
yl0, yl1 = ax1.get_ylim()
ax2.set_ylim(yl0/4.2, yl1/4.2)
ax2.axhspan(90, 120, color="#ffcc99", alpha=0.30, label="Max. KH-Aufnahme")

ax1.set_xlim(x.min(), x.max())
ax1.set_xlabel("Leistung (W)")
ax1.set_ylabel("kcal/h")
ax1.set_title("Fat & carbohydrate combustion")
ax1.grid(alpha=0.3)
ax1.legend(loc="upper left", fontsize=8)
ax2.legend(loc="upper right", fontsize=8)
st.pyplot(fig)

# -----------------------------
# Substratverwendung als Prozent + Zonen-Hintergrund
# -----------------------------
st.markdown("**FatMax & Zonen (W)**")
fig, ax = plt.subplots(figsize=(8, 4))

x = np.linspace(0.01, 1.1*cp, 400)
# asymmetrische Fettkurve (0..100%)
left_width = 0.10 * 1.6
right_width = 0.10 * 0.7
y_fat = np.where(
    x < fatmax,
    np.exp(-((fatmax - x) / (left_width * cp)) ** 2.2),
    np.exp(-((x - fatmax) / (right_width * cp)) ** (2.2 * 1.2))
)
y_fat = (y_fat / (np.nanmax(y_fat) + 1e-9)) * 100
y_carb = 100 - y_fat

# Crossover
cross_idx = np.argmin(np.abs(y_fat - y_carb))
cross_x, cross_y = x[cross_idx], y_fat[cross_idx]

ga2_lo, ga2_hi = ga1_hi, 0.90*cp
ax.axvspan(ga1_lo, ga1_hi, color="#b3ffb3", alpha=0.35, label="GA1 (Fett)")
ax.axvspan(ga2_lo, ga2_hi, color="#ffff99", alpha=0.35, label="GA2 (Übergang)")

ax.plot(x, y_fat,  color="#007a00", linewidth=2.2, label="Fett (%)")
ax.plot(x, y_carb, color="#cc0000", linewidth=2.0, linestyle="--", label="KH (%)")

ax.axvline(fatmax, color="#004d00", linestyle="--", linewidth=1.2)
ax.text(fatmax, 104, f"FatMax = {fatmax:.0f} W", ha="center", fontsize=9, color="#004d00")

ax.scatter(cross_x, cross_y, color="black", s=28, zorder=5)
ax.text(cross_x, cross_y + 6, f"Crossover ≈ {cross_x:.0f} W", ha="center", fontsize=8, color="black")

ax.set_xlim(0, 1.1*cp); ax.set_ylim(0, 110)
ax.set_xlabel("Watt"); ax.set_ylabel("Substratanteil (% vom Maximum)")
ax.set_title("Substratverwendung vs. Leistung")
ax.grid(alpha=0.3); ax.legend(loc="upper right", fontsize=8)
st.pyplot(fig)

# -----------------------------
# CP-Kurve (Modell + Punkte)
# -----------------------------
st.subheader("📈 Critical Power Kurve")
pts = r["pts"]
if pts:
    t_pts = np.array([t for t, _ in pts], dtype=float)
    p_pts = np.array([p for _, p in pts], dtype=float)

    fig, ax = plt.subplots(figsize=(7, 4))
    # Modell: P = CP + W′/t
    t_curve = np.linspace(10, 1200, 300)
    p_curve = r["cp"] + (r["w_prime"] / t_curve)

    # Zonen in Farbe (horizontal – nach Leistung)
    cpv = r["cp"]
    for (low, high, color, label) in [
        (0, 0.55*cpv, "#b3d9ff", "Z1"),
        (0.55*cpv, 0.75*cpv, "#c2f0c2", "Z2"),
        (0.75*cpv, 0.90*cpv, "#ffffb3", "Z3"),
        (0.90*cpv, 1.05*cpv, "#ffd699", "Z4"),
        (1.05*cpv, 1.25*cpv, "#ff9999", "Z5"),
    ]:
        ax.axhspan(low, high, color=color, alpha=0.3, label=label)

    ax.scatter(t_pts, p_pts, color="blue", label="Testdaten", zorder=4, s=40)
    ax.plot(t_curve, p_curve, color="red", linewidth=2.2, label="CP-Modell", zorder=3)

    ax.axhline(cpv, color="gray", linestyle="--", linewidth=1)
    ax.text(t_curve[-1], cpv + 5, f"CP = {cpv:.0f} W", va="bottom", ha="right", fontsize=9, color="gray")

    # X-Achse logarithmisch, aber mit „normalen“ Ticks
    ax.set_xscale("log")
    ax.set_xlabel("Dauer (s)")
    xticks = [60, 180, 300, 600, 720, 900, 1200]
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(int(x)) for x in xticks])
    ax.set_ylabel("Leistung (W)")
    ax.set_title("Critical Power Modell (1/3/5/12)")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

    # Legend dedup
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc="upper right", fontsize=8)

    st.pyplot(fig)
else:
    st.info("Zu wenige Testpunkte für die CP-Kurve.")

# -----------------------------
# Erklärungen (Markdown)
# -----------------------------
with st.expander("ℹ️ Ergebnisse & Trainingszonen – Erklärung"):
    st.markdown("""
**CP (Critical Power)** = aerobe Dauerleistungsgrenze (≈ MLSS), berechnet aus 1–12-min Tests.  
**W′** = anaerober Energievorrat oberhalb CP.  
**FTP** = aus CP **& VLamax** modellierte 60-min-Praxisleistung → **in TrainingPeaks als Schwelle eintragen**.

**Zonen:** intern CP-basiert (mit VLamax/FatMax-Anpassung). In TrainingPeaks nutzt du die FTP-basierten Zonen.
""")

# -----------------------------
# Export (PDF)
# -----------------------------
st.subheader("📄 Export")
if st.button("PDF exportieren"):
    try:
        pdf_bytes = create_analysis_pdf_bytes(
            r.get("athlete_name",""), r['vo2_rel'], r['vlamax'], r['cp'], r['w_prime'], r['fatmax_w'],
            (r['ga1_min'], r['ga1_max']), (r['ga1_max'], 0.90*r['cp']), pts=r['pts']
        )
        st.success("PDF erstellt.")
        st.download_button(
            "📄 PDF herunterladen",
            data=pdf_bytes,
            file_name=f"{(r.get('athlete_name') or 'analyse')}_{date.today().isoformat()}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF-Erstellung fehlgeschlagen: {e}")
