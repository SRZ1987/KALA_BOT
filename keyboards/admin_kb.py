from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb():
    # Admin controls are grouped here so Railway gets a fresh deploy trigger.
    kb = InlineKeyboardBuilder()

    kb.button(text="Статистика", callback_data="stats")
    kb.button(text="Продавцы", callback_data="admin_sellers")
    kb.button(text="Бан-лист", callback_data="admin_bans")
    kb.button(text="SOS сообщения", callback_data="admin_sos")
    kb.button(text="Назад в меню", callback_data="back_to_main_menu")

    kb.adjust(1)
    return kb.as_markup()


def admin_sellers_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Добавить продавца", callback_data="admin_seller_add")
    kb.button(text="Удалить продавца", callback_data="admin_seller_delete")
    kb.button(text="Назад в админку", callback_data="admin_panel")

    kb.adjust(1)
    return kb.as_markup()


def admin_bans_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Добавить в бан", callback_data="admin_ban_user")
    kb.button(text="Удалить из бана", callback_data="admin_unban_user")
    kb.button(text="Назад в админку", callback_data="admin_panel")

    kb.adjust(1)
    return kb.as_markup()


def admin_back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад в админку", callback_data="admin_panel")
    kb.adjust(1)

    return kb.as_markup()


def admin_sos_kb(reports):
    kb = InlineKeyboardBuilder()

    for report in reports:
        kb.button(
            text=f"Удалить SOS #{report['id']}",
            callback_data=f"admin_sos_delete:{report['id']}"
        )

    kb.button(text="Назад в админку", callback_data="admin_panel")
    kb.adjust(1)

    return kb.as_markup()
