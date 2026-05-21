from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants.est_cit import CITIES


def get_city_keyboard():
    builder = InlineKeyboardBuilder()

    for city in CITIES.keys():
        builder.button(
            text=city,
            callback_data=f"city_{city}"
        )

    builder.button(
        text="Назад в меню",
        callback_data="back_to_main_menu"
    )

    builder.adjust(2)

    return builder.as_markup()
