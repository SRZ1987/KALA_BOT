




from aiogram.utils.keyboard import InlineKeyboardBuilder

CONNECTION_KB_buttons= {
    "Отзыв администратору":"feedback",
    "NB! SOS":"sos_start",


}

def connection_kb():
    kb= InlineKeyboardBuilder()
    for name, index in CONNECTION_KB_buttons.items():
        kb.button(text=name, callback_data=index)
    kb.button(
        text="Назад в меню",
        callback_data="back_to_main_menu",

    )
    kb.adjust(1)
    return kb.as_markup()

