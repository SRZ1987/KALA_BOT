from collections import defaultdict

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from constants.ru_days import RU_DAYS
from keyboards.main_keyboard import get_main_keyboard
from main import weather_icon
from utils import check_spam
from dbase.data_dase import user_city
from utils import fetch_forecast,get_fishing_forecast
from config import ADMIN_ID
from datetime import datetime


router = Router()



@router.callback_query(F.data.in_(["today", "week"]))
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
