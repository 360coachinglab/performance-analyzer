import streamlit as st

st.set_page_config(page_title="360 Coaching Lab – Performance Analyzer", page_icon="🚴", layout="wide")

st.sidebar.markdown("### 🧬 360 Coaching Lab")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="🚴 Performance Analyzer")
st.sidebar.page_link("pages/Dashboards.py", label="📊 Dashboards")
st.sidebar.page_link("pages/Analyse_Overview.py", label="📈 Analyse-Übersicht")
st.sidebar.markdown("---")
st.sidebar.markdown("**Version:** 1.9.1**")

st.title("🚴 360 Coaching Lab – Performance Analyzer")
st.markdown("#### Leistungsdiagnostik & physiologische Analyse")

athlete_name = st.text_input("Athletenname", placeholder="Name eingeben")

st.write("👉 Das Feld ist nun neutral. Kein 'Lars Blum' mehr als Beispiel.")