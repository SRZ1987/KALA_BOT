from aiogram.utils.keyboard import InlineKeyboardBuilder


def seller_ads_menu_kb(is_seller=False):
    kb = InlineKeyboardBuilder()

    kb.button(text="Смотреть объявления", callback_data="seller_ads_view")

    if is_seller:
        kb.button(text="Добавить объявление", callback_data="seller_ads_add")
        kb.button(text="Мои объявления", callback_data="seller_ads_my")

    kb.button(text="Назад", callback_data="connection")
    kb.adjust(1)

    return kb.as_markup()


def seller_ads_back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к продавцам", callback_data="seller_ads")
    kb.adjust(1)

    return kb.as_markup()


def seller_ads_my_kb(ads):
    kb = InlineKeyboardBuilder()

    for ad in ads:
        kb.button(
            text=f"Удалить #{ad['id']}",
            callback_data=f"seller_ads_delete:{ad['id']}"
        )

    kb.button(text="Назад", callback_data="seller_ads")
    kb.adjust(1)

    return kb.as_markup()


def seller_ads_admin_kb(ads):
    kb = InlineKeyboardBuilder()

    for ad in ads:
        kb.button(
            text=f"Удалить #{ad['id']}",
            callback_data=f"admin_seller_ad_delete:{ad['id']}"
        )

    kb.button(text="Назад к продавцам", callback_data="seller_ads")
    kb.adjust(1)

    return kb.as_markup()
