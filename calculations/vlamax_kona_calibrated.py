
def calc_vlamax_kona_calibrated(ffm_kg, avg20_w, peak20_w, sprint_dur_s, vo2_rel_mlkg, p5min_w, p12min_w, gender):
    ffm_kg = max(float(ffm_kg), 1e-6)
    w_per_ffm = float(avg20_w) / ffm_kg
    vo2_term = float(vo2_rel_mlkg) / 70.0
    ratio_term = (float(p12min_w) / max(1.0, float(p5min_w))) - 0.85
    female = 1 if str(gender).strip().lower() == "frau" else 0
    vl = (
        -0.394416084
        + 0.039491880 * w_per_ffm
        + 0.000036755 * float(peak20_w)
        + 0.008563458 * float(sprint_dur_s)
        - 0.218798931 * vo2_term
        - 0.100301249 * ratio_term
        - 0.014584308 * female
    )
    return max(0.20, min(0.90, round(vl, 3)))
