import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="📈 Analyse-Übersicht – 360 Coaching Lab", page_icon="📈", layout="wide")

# Sidebar navigation
st.sidebar.markdown("### 🧬 360 Coaching Lab")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="🚴 Performance Analyzer")
st.sidebar.page_link("pages/Dashboards.py", label="📊 Dashboards")
st.sidebar.page_link("pages/Analyse_Overview.py", label="📈 Analyse-Übersicht")
st.sidebar.markdown("---")
st.sidebar.markdown("**Version:** 1.9**")

st.title("📈 Analyse-Übersicht")
st.markdown("Vergleiche die wichtigsten Leistungsparameter deiner Athleten (jeweils letzter Test).")

csv_path = Path("data/athleten_daten.csv")
if not csv_path.exists():
    st.info("Noch keine Daten vorhanden. Führe zuerst eine Analyse im Haupt-Tool aus.")
    st.stop()

df = pd.read_csv(csv_path)
if "Datum" in df.columns:
    try:
        df["Datum"] = pd.to_datetime(df["Datum"])
    except Exception:
        pass

# Nur letzter Test pro Athlet
df_last = df.sort_values("Datum").groupby("Name").tail(1)

metrics = [
    ("VO2max rel (ml/min/kg)", "VO₂max rel (ml/min/kg)"),
    ("VLamax (mmol/l/s)", "VLamax (mmol/l/s)"),
    ("FTP (W)", "FTP (W)"),
    ("FatMax (W)", "FatMax (W)"),
]

for col, label in metrics:
    if col not in df_last.columns:
        continue
    st.subheader(label)
    fig, ax = plt.subplots()
    ax.bar(df_last["Name"], df_last[col], color="#3CB371")
    ax.set_ylabel(label)
    ax.set_xticklabels(df_last["Name"], rotation=20, ha="right")
    st.pyplot(fig)
