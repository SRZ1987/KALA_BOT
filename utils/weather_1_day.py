from datetime import datetime

from constants.weather_icons import calculate_fishing_score
from utils import moon_phase, pressure_trend


def get_fishing_forecast(
        items,
        day_str,
        previous_pressures=None
):

    if not items:
        return "Нет данных", "Прогноз недоступен"

    temps = [i["main"]["temp"] for i in items]
    winds = [i["wind"]["speed"] for i in items]
    pressures = [i["main"]["pressure"] for i in items]
    clouds = [i["clouds"]["all"] for i in items]
    humidity = [i["main"]["humidity"] for i in items]

    precipitation = sum(
        i.get("rain", {}).get("3h", 0)
        + i.get("snow", {}).get("3h", 0)
        for i in items
    )

    weather_ids = [
        i["weather"][0]["id"]
        for i in items
    ]

    avg_temp = sum(temps) / len(temps)
    avg_wind = sum(winds) / len(winds)
    avg_pressure = sum(pressures) / len(pressures)
    avg_clouds = sum(clouds) / len(clouds)
    avg_humidity = sum(humidity) / len(humidity)

    date_obj = datetime.strptime(day_str, "%Y-%m-%d")

    moon_value, moon_label = moon_phase(date_obj)

    pressure_bonus, pressure_text = pressure_trend(
        pressures,
        previous_pressures
    )

    score = calculate_fishing_score(
        avg_temp,
        avg_wind,
        avg_pressure,
        avg_clouds,
        avg_humidity,
        precipitation,
        weather_ids,
        moon_value,
        pressure_bonus,
    )

    # =====================================================
    # ШКАЛА
    # =====================================================

    bar = (
            "█" * (score // 5)
            + "░" * (20 - score // 5)
    )

    # =====================================================
    # ВЕРДИКТ
    # =====================================================

    if score >= 95:
        verdict = "🔥 ЖОР! Отличный клёв"

    elif score >= 80:
        verdict = "🎣 Хороший клёв"

    elif score >= 50:
        verdict = "🙂 Клёв средний"

    elif score >= 35:
        verdict = "😐 Слабый клёв"

    else:
        verdict = "🥶 Рыба почти не активна"

    return (
        f"{score}/100\n[{bar}]",
        (
            f"{verdict}\n"
            f"{pressure_text}\n"
            f"{moon_label}"
        )
    )

