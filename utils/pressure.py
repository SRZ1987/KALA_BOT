



def pressure_trend(today_pressures, yesterday_pressures):

    if not yesterday_pressures:
        return 0, "→ стабильно"

    avg_today = sum(today_pressures) / len(today_pressures)
    avg_yesterday = sum(yesterday_pressures) / len(yesterday_pressures)

    delta = avg_today - avg_yesterday

    # рыба плохо любит резкое падение давления

    if delta <= -6:
        return -25, f"↘ резкое падение ({delta:+.1f} hPa)"

    if delta <= -3:
        return -15, f"↘ падает ({delta:+.1f} hPa)"

    if delta < 0:
        return -5, f"↘ слегка падает ({delta:+.1f} hPa)"

    if delta >= 5:
        return 8, f"↗ растёт ({delta:+.1f} hPa)"

    return 10, f"→ стабильно ({delta:+.1f} hPa)"
