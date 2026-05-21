from aiogram.utils.keyboard import InlineKeyboardBuilder


def photo_posts_menu_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Смотреть ленту", callback_data="photo_posts_view")
    kb.button(text="Добавить фото", callback_data="photo_posts_add")
    kb.button(text="Назад", callback_data="connection")

    kb.adjust(1)
    return kb.as_markup()


def photo_posts_back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к фото дня", callback_data="photo_posts")
    kb.adjust(1)

    return kb.as_markup()
