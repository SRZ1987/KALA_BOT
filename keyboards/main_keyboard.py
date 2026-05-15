from aiogram.utils.keyboard import InlineKeyboardBuilder



def get_main_keyboard(is_admin=False):

    builder = InlineKeyboardBuilder()

    # -----------------------------------------------------
    # Основные кнопки
    # -----------------------------------------------------

    builder.button(
        text="🌤 Сегодня",
        callback_data="today"
    )

    builder.button(
        text="📅 Неделя",
        callback_data="week"
    )

    # builder.button(
    #     text="💬 Отзыв",
    #     callback_data="feedback"
    # )

    builder.button(
        text="Назад в меню",
        callback_data="back_to_main_menu"
    )

    # -----------------------------------------------------
    # Админ кнопка
    # -----------------------------------------------------

    if is_admin:

        builder.button(
            text="📊 Статистика",
            callback_data="stats"
        )

    # -----------------------------------------------------
    # Расположение кнопок
    # -----------------------------------------------------

    if is_admin:

        # 1 кнопка в ряд
        builder.adjust(1)

    else:

        builder.adjust(1)

    return builder.as_markup()
