def calc_vlamax(ffm, p20s, ftp, gender):
    base = 0.4 if gender == 'Mann' else 0.35
    return base + (p20s / ffm / 100) - (ftp / 1000)
