from main import weather_penalty
from utils import moon_fishing_bonus


def calculate_fishing_score(
        temp,
        wind,
        pressure,
        clouds,
        humidity,
        precipitation,
        weather_ids,
        moon_phase_value,
        pressure_bonus,
):

    score = 50

    # =====================================================
    # 🌡 ТЕМПЕРАТУРА
    # =====================================================

    if 10 <= temp <= 20:
        score += 22

    elif 5 <= temp < 10:
        score += 12

    elif 20 < temp <= 24:
        score += 8

    elif temp < 0:
        score -= 25

    elif temp > 28:
        score -= 20

    # =====================================================
    # 💨 ВЕТЕР
    # =====================================================

    if 2 <= wind <= 5:
        score += 20

    elif 5 < wind <= 8:
        score += 10

    elif wind < 1:
        score -= 15

    elif wind > 12:
        score -= 30

    elif wind > 8:
        score -= 15

    # =====================================================
    # ☁️ ОБЛАЧНОСТЬ
    # =====================================================

    if 40 <= clouds <= 80:
        score += 15

    elif clouds < 20:
        score -= 12

    elif clouds > 95:
        score -= 8

    # =====================================================
    # 🌡 ДАВЛЕНИЕ
    # =====================================================

    if 1005 <= pressure <= 1020:
        score += 12

    elif pressure < 995:
        score -= 18

    elif pressure > 1032:
        score -= 8

    score += pressure_bonus

    # =====================================================
    # 🌧 ОСАДКИ
    # =====================================================

    if precipitation > 15:
        score -= 25

    elif precipitation > 5:
        score -= 12

    elif precipitation > 0:
        score -= 3

    # =====================================================
    # 💧 ВЛАЖНОСТЬ
    # =====================================================

    if humidity > 92:
        score -= 5

    # =====================================================
    # 🌦 ПОГОДА
    # =====================================================

    weather_score, _ = weather_penalty(weather_ids)

    score += weather_score

    # =====================================================
    # 🌙 ЛУНА
    # =====================================================

    score += moon_fishing_bonus(moon_phase_value)

    # =====================================================
    # ОГРАНИЧЕНИЕ
    # =====================================================

    score = max(0, min(100, score))

    return score

