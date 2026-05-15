


from aiogram.utils.keyboard import InlineKeyboardBuilder

MAIN_MENU_buttons= {
    "Календарь клёва": "fishing_calender_main_menu",
    "Полезные ссылки": "useful_links",
    "Связь и остальное": "connection"

}

def main_menu_kb():
    kb= InlineKeyboardBuilder()
    for name, index in MAIN_MENU_buttons.items():
        kb.button(text=name, callback_data=index)
    kb.adjust(1)
    return kb.as_markup()

