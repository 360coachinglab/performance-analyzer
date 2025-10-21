
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from io import BytesIO

import matplotlib
matplotlib.use("Agg")  # headless backend for servers/Streamlit Cloud
import matplotlib.pyplot as plt

def _fig_to_png_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

def _plot_vlamax_gauge(vlamax):
    fig, ax = plt.subplots(figsize=(4, 1.2))
    ax.barh([0], [max(0, min(1, vlamax))], height=0.4)
    ax.set_xlim(0, 1); ax.set_yticks([]); ax.set_xlabel("VLamax (mmol/l/s)")
    ax.text(max(0, min(1, vlamax)), 0, f"{vlamax:.2f}", va="center", ha="center")
    fig.tight_layout()
    return _fig_to_png_bytes(fig)

def _plot_vo2_gauge(vo2_rel, lo=40, hi=80):
    fig, ax = plt.subplots(figsize=(4, 1.2))
    val = max(lo, min(hi, vo2_rel))
    ax.barh([0], [val-lo], height=0.4)
    ax.set_xlim(0, hi-lo); ax.set_yticks([]); ax.set_xlabel(f"VO₂max (ml/min/kg) [{lo}–{hi}]")
    ax.text(val-lo, 0, f"{vo2_rel:.1f}", va="center", ha="center")
    fig.tight_layout()
    return _fig_to_png_bytes(fig)

def _plot_fatmax_in_zones(fatmax_w, cp, ga1_range, ga2_range):
    ga1_lo, ga1_hi = ga1_range
    ga2_lo, ga2_hi = ga2_range
    fig, ax = plt.subplots(figsize=(6, 1.2))
    ax.hlines(0, ga1_lo, ga1_hi, linewidth=10)
    ax.hlines(0, ga2_lo, ga2_hi, linewidth=10)
    ax.plot([fatmax_w], [0], marker="o")
    ax.set_xlim(0, cp*1.1); ax.set_yticks([]); ax.set_xlabel("Watt")
    fig.tight_layout()
    return _fig_to_png_bytes(fig)

def _plot_cp_curve(cp, w_prime, pts):
    import numpy as np
    fig, ax = plt.subplots(figsize=(6, 3))
    t_curve = np.linspace(15, 1200, 200)
    p_curve = cp + (w_prime / t_curve)
    ax.plot(t_curve, p_curve, label="CP-Modell")
    if pts:
        t_pts = [t for t,_ in pts]; p_pts = [p for _,p in pts]
        ax.scatter(t_pts, p_pts, label="Messpunkte")
    ax.set_xscale("log")
    ax.set_xlabel("Dauer (s) (log)"); ax.set_ylabel("Leistung (W)")
    ax.legend()
    fig.tight_layout()
    return _fig_to_png_bytes(fig)

def _render_pdf(c, athlete_name, vo2_rel, vlamax, cp, w_prime, fatmax_w, ga1_range, ga2_range, pts):
    width, height = A4
    margin = 2*cm
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Performance Analyse")
    y -= 0.8*cm
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.grey)
    c.drawString(margin, y, "Neutrales PDF – automatisch generiert")
    c.setFillColor(colors.black)
    y -= 1.2*cm

    from datetime import date
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, f"Athlet: {athlete_name or '-'}")
    c.drawRightString(width - margin, y, f"Datum: {date.today().isoformat()}")
    y -= 0.8*cm

    lines = [
        ("VO₂max rel.", f"{vo2_rel:.1f} ml/min/kg", "Aerobe Kapazität."),
        ("VLamax", f"{vlamax:.3f} mmol/l/s", "Glykolytisches Potenzial."),
        ("Critical Power (CP)", f"{cp:.0f} W", "Dauerleistungsgrenze."),
        ("W′", f"{w_prime:.0f} J", "Anaerobe Kapazität oberhalb CP."),
        ("FatMax", f"{fatmax_w:.0f} W", "Leistung mit max. Fettstoffwechsel."),
    ]
    c.setFont("Helvetica-Bold", 11); c.drawString(margin, y, "Kennzahlen – Überblick"); y -= 0.5*cm
    c.setFont("Helvetica", 10)
    for title, val, desc in lines:
        c.drawString(margin, y, f"{title}: {val}"); y -= 0.42*cm
        c.setFillColor(colors.grey); c.drawString(margin+1.2*cm, y, desc); c.setFillColor(colors.black)
        y -= 0.48*cm
    y -= 0.3*cm
    c.setStrokeColor(colors.lightgrey); c.line(margin, y, width-margin, y); c.setStrokeColor(colors.black)
    y -= 0.6*cm

    # --- charts (in-memory images) ---
    v_img = ImageReader(BytesIO(_plot_vlamax_gauge(vlamax)))
    vo2_img = ImageReader(BytesIO(_plot_vo2_gauge(vo2_rel)))
    fatmax_img = ImageReader(BytesIO(_plot_fatmax_in_zones(fatmax_w, cp, ga1_range, ga2_range)))
    cpcurve_img = ImageReader(BytesIO(_plot_cp_curve(cp, w_prime, pts or [])))

    img_h = 3.5*cm; img_w = 8.0*cm
    c.drawImage(v_img, margin, y-img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
    c.drawImage(vo2_img, margin+img_w+0.6*cm, y-img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
    y -= img_h + 0.8*cm

    img_h2 = 3.0*cm; img_w2 = width - 2*margin
    c.drawImage(fatmax_img, margin, y-img_h2, width=img_w2, height=img_h2, preserveAspectRatio=True, mask='auto')
    y -= img_h2 + 0.8*cm

    img_h3 = 6.0*cm; img_w3 = width - 2*margin
    c.drawImage(cpcurve_img, margin, y-img_h3, width=img_w3, height=img_h3, preserveAspectRatio=True, mask='auto')
    y -= img_h3 + 0.6*cm

    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, 1.5*cm, "©")
    c.save()

def create_analysis_pdf(output_path, athlete_name, vo2_rel, vlamax, cp, w_prime, fatmax_w, ga1_range, ga2_range, pts=None):
    c = canvas.Canvas(str(output_path), pagesize=A4)
    _render_pdf(c, athlete_name, vo2_rel, vlamax, cp, w_prime, fatmax_w, ga1_range, ga2_range, pts or [])

def create_analysis_pdf_bytes(athlete_name, vo2_rel, vlamax, cp, w_prime, fatmax_w, ga1_range, ga2_range, pts=None):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    _render_pdf(c, athlete_name, vo2_rel, vlamax, cp, w_prime, fatmax_w, ga1_range, ga2_range, pts or [])
    pdf = buf.getvalue()
    buf.close()
    return pdf
