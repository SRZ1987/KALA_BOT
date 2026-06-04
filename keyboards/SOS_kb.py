from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def geo_kb():
    kb = ReplyKeyboardBuilder()

    kb.row(KeyboardButton(text="Геолокация", request_location=True))
    kb.row(KeyboardButton(text="Пропустить геолокацию"))
    kb.row(KeyboardButton(text="Назад"))

    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def contact_kb():
    kb = ReplyKeyboardBuilder()

    kb.row(KeyboardButton(text="Телефон", request_contact=True))
    kb.row(KeyboardButton(text="Назад"))

    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
