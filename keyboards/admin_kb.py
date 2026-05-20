from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Статистика", callback_data="stats")
    kb.button(text="Назад в меню", callback_data="back_to_main_menu")

    kb.adjust(1)
    return kb.as_markup()
