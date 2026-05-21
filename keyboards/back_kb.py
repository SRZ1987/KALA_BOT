from aiogram.utils.keyboard import InlineKeyboardBuilder


def back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад в меню", callback_data="back_to_main_menu")
    kb.adjust(1)
    return kb.as_markup()


def connection_back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="connection")
    kb.adjust(1)
    return kb.as_markup()


def rides_back_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к попутчикам", callback_data="rides")
    kb.adjust(1)
    return kb.as_markup()
