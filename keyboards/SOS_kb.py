from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

def contact_geo_kb():
    kb = ReplyKeyboardBuilder()

    kb.row(
        KeyboardButton(text="📍 Геолокация", request_location=True),
        KeyboardButton(text="📱 Телефон", request_contact=True),
    )

    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)