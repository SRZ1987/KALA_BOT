



def weather_penalty(weather_ids):

    # приоритет плохой погоды
    # чем меньше число — тем хуже

    severity = {
        "storm": 1,
        "heavy_rain": 2,
        "rain": 3,
        "snow": 4,
        "fog": 5,
        "clear": 6,
        "clouds": 7,
    }

    current = severity["clouds"]

    for wid in weather_ids:

        if 200 <= wid < 300:
            current = min(current, severity["storm"])

        elif wid in [502, 503, 504, 522]:
            current = min(current, severity["heavy_rain"])

        elif 500 <= wid < 600:
            current = min(current, severity["rain"])

        elif 600 <= wid < 700:
            current = min(current, severity["snow"])

        elif 700 <= wid < 800:
            current = min(current, severity["fog"])

        elif wid == 800:
            current = min(current, severity["clear"])

    if current == severity["storm"]:
        return -35, "⛈ Гроза"

    if current == severity["heavy_rain"]:
        return -25, "🌧 Ливень"

    if current == severity["rain"]:
        return -12, "🌦 Дождь"

    if current == severity["snow"]:
        return -15, "❄️ Снег"

    if current == severity["fog"]:
        return -5, "🌫 Туман"

    if current == severity["clear"]:
        return -8, "☀️ Ясно"

    return 5, "☁️ Облачно"

