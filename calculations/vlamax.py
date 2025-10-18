
def calc_vlamax(ffm, avg20, peak20, sprint_dur_s, gender):
    """Empirisches VLamax-Modell (Classic, v1.9.2)
    Formel:
        VLamax = -0.33217 + 0.05238 * (Avg20/FFM) + 0.01295 * Sprintdauer
    Frauenkorrektur: -0.01
    Wertebereich: [0.20, 0.90]
    """
    ffm = max(float(ffm), 1e-6)
    avg_ffm = float(avg20) / ffm
    vl = -0.33217177131625886 + 0.05237854 * avg_ffm + 0.01295129 * float(sprint_dur_s)
    if str(gender).strip().lower().startswith("f"):
        vl -= 0.01
    return max(0.20, min(0.90, round(vl, 3)))
