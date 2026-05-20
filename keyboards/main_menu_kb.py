from aiogram.utils.keyboard import InlineKeyboardBuilder


MAIN_MENU_BUTTONS = {
    "Календарь клёва": "fishing_calender_main_menu",
    "Полезные ссылки": "useful_links",
    "Связь и остальное": "connection",
}


def main_menu_kb(is_admin=False):
    kb = InlineKeyboardBuilder()

    for name, index in MAIN_MENU_BUTTONS.items():
        kb.button(text=name, callback_data=index)

    if is_admin:
        kb.button(text="Админка", callback_data="admin_panel")

    kb.adjust(1)
    return kb.as_markup()
