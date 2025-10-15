def determine_athlete_type(vo2_rel, vlamax, ftp, weight):
    if vo2_rel > 70 and vlamax < 0.4:
        return 'Climber / Ausdauer-Athlet'
    elif vlamax > 0.7:
        return 'Sprinter / Explosivtyp'
    elif ftp / max(weight,1e-9) > 5.0:
        return 'Allrounder / XCO-Athlet'
    else:
        return 'Ausgeglichen'
