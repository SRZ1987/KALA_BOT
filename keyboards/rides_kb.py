from aiogram.utils.keyboard import InlineKeyboardBuilder


def rides_menu_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Смотреть объявления", callback_data="rides_view")
    kb.button(text="Добавить объявление", callback_data="rides_add")
    kb.button(text="Мои объявления", callback_data="rides_my")
    kb.button(text="Назад", callback_data="connection")

    kb.adjust(1)
    return kb.as_markup()


def rides_back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к попутчикам", callback_data="rides")
    kb.adjust(1)

    return kb.as_markup()


def rides_back_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к попутчикам", callback_data="rides")
    kb.adjust(1)

    return kb.as_markup()


def rides_my_ads_kb(ads):
    kb = InlineKeyboardBuilder()

    for ad in ads:
        kb.button(
            text=f"Удалить #{ad['id']}",
            callback_data=f"rides_delete:{ad['id']}"
        )

    kb.button(text="Назад", callback_data="rides")
    kb.adjust(1)

    return kb.as_markup()


def rides_admin_ads_kb(ads):
    kb = InlineKeyboardBuilder()

    for ad in ads:
        kb.button(
            text=f"Удалить #{ad['id']}",
            callback_data=f"admin_ride_delete:{ad['id']}"
        )

    kb.button(text="Назад к попутчикам", callback_data="rides")
    kb.adjust(1)

    return kb.as_markup()
