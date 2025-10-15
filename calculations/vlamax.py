def calc_vlamax(ffm, avg20, peak20, sprint_dur_s, gender):
    ffm = max(ffm, 1e-6)
    peak_ffm = peak20 / ffm
    avg_ffm = avg20 / ffm
    dur_corr = 1.0 + 0.015 * (20 - sprint_dur_s)
    vl = (-0.054) + 0.0061 * peak_ffm + 0.0147 * avg_ffm
    vl *= dur_corr
    if gender == "Frau":
        vl -= 0.01
    return max(0.20, min(0.90, vl))
