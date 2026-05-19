from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants.est_cit import CITIES


CITY_ITEMS = list(CITIES.items())


def rides_menu_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Смотреть объявления", callback_data="rides_view")
    kb.button(text="Добавить объявление", callback_data="rides_add")
    kb.button(text="Мои объявления", callback_data="rides_my")
    kb.button(text="Назад", callback_data="connection")

    kb.adjust(1)
    return kb.as_markup()


def rides_city_kb(prefix):
    kb = InlineKeyboardBuilder()

    for index, (city_name, city_key) in enumerate(CITY_ITEMS):
        kb.button(
            text=city_name,
            callback_data=f"{prefix}:{index}"
        )

    kb.button(text="Назад", callback_data="rides")
    kb.adjust(2)

    return kb.as_markup()


def rides_type_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Ищу попутчика", callback_data="rides_type:need")
    kb.button(text="Есть место в машине", callback_data="rides_type:offer")
    kb.button(text="Назад", callback_data="rides_add")

    kb.adjust(1)
    return kb.as_markup()


def rides_back_kb():
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
