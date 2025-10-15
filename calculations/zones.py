import pandas as pd

def calc_zones(ftp, hfmax):
    data = [
        ('Z1 - Regeneration', 0.0, 0.55),
        ('Z2 - GA1', 0.56, 0.75),
        ('Z3 - GA2', 0.76, 0.9),
        ('Z4 - Schwelle', 0.91, 1.05),
        ('Z5 - VO₂max', 1.06, 1.20),
    ]
    df = pd.DataFrame(data, columns=['Zone', '%FTP von', '%FTP bis'])
    df['Leistung (W)'] = [f"{int(ftp*a)}–{int(ftp*b)}" for _, a, b in data]
    df['Herzfrequenz (HF)'] = [f"{int(hfmax*a)}–{int(hfmax*b)}" for _, a, b in data]
    return df
