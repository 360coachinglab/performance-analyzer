import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="📊 Dashboards – 360 Coaching Lab", page_icon="📊", layout="wide")

# Sidebar navigation
st.sidebar.markdown("### 🧬 360 Coaching Lab")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="🚴 Performance Analyzer")
st.sidebar.page_link("pages/Dashboards.py", label="📊 Dashboards")
st.sidebar.markdown("---")
st.sidebar.markdown("**Version:** 1.8.1**")

st.title("📊 Dashboards")

csv_path = Path("data/athleten_daten.csv")
if not csv_path.exists():
    st.info("Noch keine Daten vorhanden. Führe zuerst eine Analyse im Haupt-Tool aus, damit Ergebnisse gespeichert werden.")
    st.stop()

df = pd.read_csv(csv_path)
if "Datum" in df.columns:
    try:
        df["Datum"] = pd.to_datetime(df["Datum"])
    except Exception:
        pass

st.subheader("VO₂max vs. VLamax")
left, right = st.columns([3,2])
with left:
    fig, ax = plt.subplots()
    ax.scatter(df["VO2max rel (ml/min/kg)"], df["VLamax (mmol/l/s)"], c="#3CB371")
    ax.set_xlabel("VO₂max rel (ml/min/kg)")
    ax.set_ylabel("VLamax (mmol/l/s)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
with right:
    st.dataframe(df[["Name","Datum","VO2max rel (ml/min/kg)","VLamax (mmol/l/s)","FTP (W)","FatMax (W)"]].sort_values(by="Datum", ascending=False).reset_index(drop=True))

st.subheader("Vergleich pro Athlet (Balken)")
names = sorted(df["Name"].unique().tolist())
sel = st.multiselect("Athleten auswählen", names, default=names[: min(5, len(names))])
filt = df[df["Name"].isin(sel)]
if len(filt) == 0:
    st.info("Bitte mindestens einen Athleten auswählen.")
else:
    last = filt.sort_values("Datum").groupby("Name").tail(1)
    fig2, ax2 = plt.subplots()
    ax2.bar(last["Name"], last["VO2max rel (ml/min/kg)"], color="#3CB371")
    ax2.set_ylabel("VO₂max rel (ml/min/kg)")
    ax2.set_xticklabels(last["Name"], rotation=20, ha="right")
    st.pyplot(fig2)

    fig3, ax3 = plt.subplots()
    ax3.bar(last["Name"], last["VLamax (mmol/l/s)"], color="#3CB371")
    ax3.set_ylabel("VLamax (mmol/l/s)")
    ax3.set_xticklabels(last["Name"], rotation=20, ha="right")
    st.pyplot(fig3)
