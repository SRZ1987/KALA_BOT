from aiogram.utils.keyboard import InlineKeyboardBuilder


CONNECTION_KB_BUTTONS = {
    "Отзыв администратору": "feedback",
    "NB! SOS": "sos_start",
    "Попутчики": "rides",
    "Фото дня": "photo_posts",
    "Объявления продавцов": "seller_ads",
}


def connection_kb():
    kb = InlineKeyboardBuilder()

    for name, index in CONNECTION_KB_BUTTONS.items():
        kb.button(text=name, callback_data=index)

    kb.button(
        text="Назад в меню",
        callback_data="back_to_main_menu",
    )

    kb.adjust(1)
    return kb.as_markup()
