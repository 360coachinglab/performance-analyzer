def calc_vlamax(ffm, avg20, peak20, sprint_dur_s, gender):
    """Empirisches VLamax-Modell (LOOCV-optimiert) aus Sprintdaten:
    VLamax = -0.33217 + 0.05238 * (Avg20/FFM) + 0.01295 * Sprintdauer
    """
    ffm = max(ffm, 1e-6)
    avg_ffm = avg20 / ffm
    vl = -0.33217177131625886 + 0.05237854 * avg_ffm + 0.01295129 * float(sprint_dur_s)
    if gender == "Frau":
        vl -= 0.01
    return max(0.20, min(0.90, vl))
