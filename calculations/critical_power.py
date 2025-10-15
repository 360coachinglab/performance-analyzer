def calc_critical_power(p5min, p12min, p20s):
    ftp = round(p5min * 0.9, 1)
    w_prime = round((p20s - ftp) * 15, 1)
    return ftp, w_prime
