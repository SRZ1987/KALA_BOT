

# =========================================================
# 🎣 FISHING FORECAST TELEGRAM BOT
# =========================================================
#
# Полностью переработанная версия бота.
#
# Что улучшено:
#
# ✅ async HTTP через aiohttp
# ✅ HTTPS запросы
# ✅ подробное логирование
# ✅ защита от падений
# ✅ антиспам
# ✅ защита edit_text
# ✅ улучшенный алгоритм клёва
# ✅ более точная обработка погоды
# ✅ обработка ошибок Telegram
# ✅ безопасные проверки данных
# ✅ кэширование погоды
# ✅ улучшенная логика давления
# ✅ улучшенная логика осадков
# ✅ улучшенная логика луны
# ✅ комментарии почти к каждой части
#
# Пока всё в одном файле как ты просил.
#
# =========================================================

import asyncio
import logging
import aiohttp
import os
import time

from datetime import datetime
from collections import defaultdict

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.exceptions import TelegramBadRequest


# =========================================================
# ⚙️ НАСТРОЙКИ
# =========================================================

# ❗ Лучше хранить в ENV
# Но пока можно оставить так

API_TOKEN = "8702789808:AAGb2qrVxVn9-s2sno5LRDn5KmIUGVBAEHw"
OWM_API_KEY = "331d8e86ef9631ddc0f0218237f50258"

ADMIN_ID = 588858971

# =========================================================
# 🌍 ГОРОДА ЭСТОНИИ
# =========================================================

CITIES = {
    "Таллинн": "Tallinn",
    "Тарту": "Tartu",
    "Нарва": "Narva",
    "Пярну": "Parnu",
    "Кохтла-Ярве": "Kohtla-Jarve",
    "Вильянди": "Viljandi",
    "Раквере": "Rakvere",
    "Хаапсалу": "Haapsalu",
    "Маарду": "Maardu",
    "Кейла": "Keila",
}

# =========================================================
# 🧠 ХРАНЕНИЕ ДАННЫХ
# =========================================================

# выбранный город пользователя
user_city = {}

# список пользователей
all_users = set()

# антиспам
user_last_request = {}

# кэш погоды
weather_cache = {}

# =========================================================
# 📝 ЛОГИРОВАНИЕ
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =========================================================
# 🤖 ИНИЦИАЛИЗАЦИЯ БОТА
# =========================================================

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# =========================================================
# 📌 FSM СОСТОЯНИЯ
# =========================================================

class FeedbackState(StatesGroup):
    waiting_feedback = State()


# =========================================================
# 🕓 РУССКИЕ ДНИ НЕДЕЛИ
# =========================================================

RU_DAYS = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье",
}

# =========================================================
# 🧊 АНТИСПАМ
# =========================================================

def check_spam(user_id: int, cooldown: int = 2) -> bool:
    """
    Проверка антиспама.

    Пользователь не сможет спамить кнопками.
    """

    now = time.time()

    if user_id in user_last_request:
        if now - user_last_request[user_id] < cooldown:
            return False

    user_last_request[user_id] = now
    return True


# =========================================================
# 🌙 ФАЗА ЛУНЫ
# =========================================================

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


# =========================================================
# 🌡 АНАЛИЗ ДАВЛЕНИЯ
# =========================================================

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


# =========================================================
# 🌦 АНАЛИЗ ТИПА ПОГОДЫ
# =========================================================

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


# =========================================================
# 🎣 ГЛАВНЫЙ АЛГОРИТМ КЛЁВА
# =========================================================

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


# =========================================================
# 🌤 ИКОНКИ ПОГОДЫ
# =========================================================

def weather_icon(weather_id):

    if 200 <= weather_id < 300:
        return "⛈"

    if 300 <= weather_id < 400:
        return "🌦"

    if 500 <= weather_id < 600:
        return "🌧"

    if 600 <= weather_id < 700:
        return "❄️"

    if 700 <= weather_id < 800:
        return "🌫"

    if weather_id == 800:
        return "☀️"

    if weather_id == 801:
        return "🌤"

    if weather_id == 802:
        return "⛅"

    return "☁️"


# =========================================================
# 🌍 ЗАГРУЗКА ПОГОДЫ
# =========================================================

async def fetch_forecast(city: str):

    # =====================================================
    # КЭШ
    # =====================================================

    if city in weather_cache:

        cached_time, cached_data = weather_cache[city]

        # кэш 10 минут
        if time.time() - cached_time < 600:
            return cached_data

    # =====================================================
    # API URL
    # =====================================================

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}"
        f"&appid={OWM_API_KEY}"
        f"&units=metric"
        f"&lang=ru"
    )

    try:

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.get(url) as response:

                if response.status != 200:

                    logger.error(
                        f"OWM ERROR {response.status}"
                    )

                    return None

                data = await response.json()

                if "list" not in data:
                    return None

                weather_cache[city] = (
                    time.time(),
                    data
                )

                return data

    except Exception as e:

        logger.exception(
            f"Ошибка загрузки погоды: {e}"
        )

        return None


# =========================================================
# 🎣 ПРОГНОЗ НА ДЕНЬ
# =========================================================

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

    if score >= 80:
        verdict = "🔥 ЖОР! Отличный клёв"

    elif score >= 65:
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


# =========================================================
# ⌨️ КЛАВИАТУРА ГОРОДОВ
# =========================================================

# =========================================================
# ⌨️ КЛАВИАТУРА ВЫБОРА ГОРОДА
# =========================================================

def get_city_keyboard():

    builder = InlineKeyboardBuilder()

    # -----------------------------------------------------
    # Добавляем все города
    # -----------------------------------------------------

    for city in CITIES.keys():

        builder.button(
            text=city,
            callback_data=f"city_{city}"
        )

    # -----------------------------------------------------
    # По 2 кнопки в ряд
    # -----------------------------------------------------

    builder.adjust(2)

    return builder.as_markup()

# =========================================================
# ⌨️ ГЛАВНАЯ КЛАВИАТУРА
# =========================================================

# =========================================================
# ⌨️ ГЛАВНАЯ КЛАВИАТУРА
# =========================================================

def get_main_keyboard(is_admin=False):

    builder = InlineKeyboardBuilder()

    # -----------------------------------------------------
    # Основные кнопки
    # -----------------------------------------------------

    builder.button(
        text="🌤 Сегодня",
        callback_data="today"
    )

    builder.button(
        text="📅 Неделя",
        callback_data="week"
    )

    builder.button(
        text="💬 Отзыв",
        callback_data="feedback"
    )

    # -----------------------------------------------------
    # Админ кнопка
    # -----------------------------------------------------

    if is_admin:

        builder.button(
            text="📊 Статистика",
            callback_data="stats"
        )

    # -----------------------------------------------------
    # Расположение кнопок
    # -----------------------------------------------------

    if is_admin:

        # 1 кнопка в ряд
        builder.adjust(1, 1, 1, 1)

    else:

        builder.adjust(1, 1, 1)

    return builder.as_markup()

# =========================================================
# 🚀 /start
# =========================================================

@dp.message(Command("start"))
async def cmd_start(message: Message):

    all_users.add(message.from_user.id)

    await message.answer(
        "🎣 Привет!\n\n"
        "Выбери город Эстонии:",
        reply_markup=get_city_keyboard()
    )


# =========================================================
# 🌍 ВЫБОР ГОРОДА
# =========================================================

@dp.callback_query(F.data.startswith("city_"))
async def select_city(callback: CallbackQuery):

    if not check_spam(callback.from_user.id):
        await callback.answer(
            "Не так быстро 😅",
            show_alert=True
        )
        return

    city_ru = callback.data[5:]
    city_eng = CITIES[city_ru]

    user_city[callback.from_user.id] = city_eng

    all_users.add(callback.from_user.id)

    try:

        await callback.message.edit_text(
            f"✅ Выбран город: <b>{city_ru}</b>\n\n"
            f"Что показать?",
            reply_markup=get_main_keyboard(
                callback.from_user.id == ADMIN_ID
            )
        )

    except TelegramBadRequest:
        pass

    await callback.answer()


# =========================================================
# 💬 ОТЗЫВ
# =========================================================

@dp.callback_query(F.data == "feedback")
async def feedback_start(
        callback: CallbackQuery,
        state: FSMContext
):

    await state.set_state(
        FeedbackState.waiting_feedback
    )

    try:

        await callback.message.edit_text(
            "💬 Напиши отзыв.\n"
            "Можно текст, фото или голосовое."
        )

    except TelegramBadRequest:
        pass

    await callback.answer()


# =========================================================
# 💬 ПОЛУЧЕНИЕ ОТЗЫВА
# =========================================================

@dp.message(FeedbackState.waiting_feedback)
async def feedback_receive(
        message: Message,
        state: FSMContext
):

    user = message.from_user

    info = (
        f"📩 Новый отзыв\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 <code>{user.id}</code>\n"
    )

    if user.username:
        info += f"📎 @{user.username}\n"

    try:

        await bot.forward_message(
            ADMIN_ID,
            message.chat.id,
            message.message_id
        )

        await bot.send_message(
            ADMIN_ID,
            info
        )

        await message.answer(
            "✅ Спасибо за отзыв!"
        )

    except Exception as e:

        logger.exception(e)

        await message.answer(
            "❌ Ошибка отправки."
        )

    await state.clear()


# =========================================================
# 📊 СТАТИСТИКА
# =========================================================

@dp.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа",
            show_alert=True
        )

        return

    try:

        await callback.message.edit_text(
            f"📊 <b>Статистика</b>\n\n"
            f"👥 Пользователей: "
            f"<b>{len(all_users)}</b>",
            reply_markup=get_main_keyboard(True)
        )

    except TelegramBadRequest:
        pass

    await callback.answer()


# =========================================================
# 🎣 ПРОГНОЗ
# =========================================================

@dp.callback_query(F.data.in_(["today", "week"]))
async def show_forecast(callback: CallbackQuery):

    user_id = callback.from_user.id

    if not check_spam(user_id):

        await callback.answer(
            "Слишком часто 😅",
            show_alert=True
        )

        return

    if user_id not in user_city:

        await callback.answer(
            "Сначала выбери город",
            show_alert=True
        )

        return

    city = user_city[user_id]

    data = await fetch_forecast(city)

    if not data:

        await callback.answer(
            "Ошибка погоды",
            show_alert=True
        )

        return

    # =====================================================
    # ГРУППИРОВКА ПО ДНЯМ
    # =====================================================

    days = defaultdict(list)

    for item in data["list"]:

        date = item["dt_txt"].split(" ")[0]

        days[date].append(item)

    sorted_days = sorted(days.keys())

    # =====================================================
    # ПРОГНОЗ НА СЕГОДНЯ
    # =====================================================

    if callback.data == "today":

        today = sorted_days[0]

        items = days[today]

        text = (
            f"🎣 <b>Сегодня — {city.upper()}</b>\n\n"
        )

        for item in items[:8]:

            dt = datetime.strptime(
                item["dt_txt"],
                "%Y-%m-%d %H:%M:%S"
            )

            time_text = dt.strftime("%H:%M")

            temp = item["main"]["temp"]

            desc = item["weather"][0][
                "description"
            ].capitalize()

            icon = weather_icon(
                item["weather"][0]["id"]
            )

            wind = item["wind"]["speed"]

            humidity = item["main"]["humidity"]

            pressure = item["main"]["pressure"]

            text += (
                f"{time_text} {icon} "
                f"<b>{temp:.1f}°C</b>\n"
                f"{desc}\n"
                f"💨 {wind:.1f} м/с | "
                f"💧 {humidity}% | "
                f"🌡 {pressure} hPa\n\n"
            )

        score, verdict = get_fishing_forecast(
            items,
            today
        )

        text += (
            f"🎣 <b>Прогноз клёва</b>\n\n"
            f"{score}\n\n"
            f"{verdict}"
        )

    # =====================================================
    # ПРОГНОЗ НА НЕДЕЛЮ
    # =====================================================

    else:

        text = (
            f"🎣 <b>Клёв на неделю — "
            f"{city.upper()}</b>\n\n"
        )

        prev_pressures = None

        for day in sorted_days[:7]:

            items = days[day]

            dt = datetime.strptime(
                day,
                "%Y-%m-%d"
            )

            ru_day = RU_DAYS[
                dt.strftime("%A")
            ]

            score, verdict = get_fishing_forecast(
                items,
                day,
                prev_pressures
            )

            prev_pressures = [
                i["main"]["pressure"]
                for i in items
            ]

            text += (
                f"📅 <b>{dt.strftime('%d.%m')} "
                f"({ru_day})</b>\n\n"
                f"{score}\n"
                f"{verdict}\n\n"
            )

    try:

        await callback.message.edit_text(
            text,
            reply_markup=get_main_keyboard(
                user_id == ADMIN_ID
            )
        )

    except TelegramBadRequest:
        pass

    await callback.answer()


# =========================================================
# 🚀 ЗАПУСК
# =========================================================

async def main():

    logger.info("Бот запущен")

    await dp.start_polling(bot)


# =========================================================
# 🚀 ENTRY POINT
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        logger.warning("Бот остановлен")

    except Exception as e:

        logger.exception(
            f"Критическая ошибка: {e}"
        )