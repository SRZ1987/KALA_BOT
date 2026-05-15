from aiogram.utils.keyboard import InlineKeyboardBuilder
from constants.est_cit import CITIES





def get_city_keyboard():

    builder = InlineKeyboardBuilder()

    # -----------------------------------------------------
    # Добавляем все города
    # -----------------------------------------------------

    for city in CITIES.keys():

        builder.button(
            text=city,
            callback_data=f"city_{city}"
        )


    # -----------------------------------------------------
    # По 2 кнопки в ряд
    # -----------------------------------------------------

    builder.adjust(2)

    return builder.as_markup()
