from datetime import datetime


def moon_phase(date: datetime):

    known_new_moon = datetime(2000, 1, 6)

    synodic_month = 29.53058867

    days = (date - known_new_moon).total_seconds() / 86400

    phase = (days % synodic_month) / synodic_month

    if phase < 0.03 or phase > 0.97:
        label = "🌑 Новолуние"

    elif phase < 0.22:
        label = "🌒 Растущий серп"

    elif phase < 0.28:
        label = "🌓 Первая четверть"

    elif phase < 0.47:
        label = "🌔 Прибывающая луна"

    elif phase < 0.53:
        label = "🌕 Полнолуние"

    elif phase < 0.72:
        label = "🌖 Убывающая луна"

    elif phase < 0.78:
        label = "🌗 Последняя четверть"

    else:
        label = "🌘 Убывающий серп"

    return phase, label


# =========================================================
# 🎣 БОНУС ЛУНЫ ДЛЯ КЛЁВА
# =========================================================

def moon_fishing_bonus(phase: float):

    # новолуние
    if phase < 0.05 or phase > 0.95:
        return 15

    # полнолуние
    if 0.45 < phase < 0.55:
        return 8

    # четверти
    if 0.20 < phase < 0.30 or 0.70 < phase < 0.80:
        return 5

    return 0
