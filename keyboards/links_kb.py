




from aiogram.utils.keyboard import InlineKeyboardBuilder

LINKS_MENU_buttons= {
    "Разрешение на  рыбалку": "https://kalaluba.ee/hobbyFishingPermit",
    "Запреты на ловлю": "https://kalastusinfo.ee/ru/p%D1%8B%D0%B1%D0%BE%D0%BB%D0%BE%D0%B2%D1%81%D1%82%D0%B2%D0%B0/%D0%B7%D0%B0%D0%BF%D1%80%D0%B5%D1%82%D0%B0-%D0%BD%D0%B0-%D0%BB%D0%BE%D0%B2%D0%BB%D1%8E-%D1%80%D1%8B%D0%B1%D1%8B/",
    "Минимальные размеры рыбы":"https://kalastusinfo.ee/ru/p%d1%8b%d0%b1%d0%be%d0%bb%d0%be%d0%b2%d1%81%d1%82%d0%b2%d0%b0/%d0%bc%d0%b8%d0%bd%d0%b8%d0%bc%d0%b0%d0%bb%d1%8c%d0%bd%d1%8b%d0%b5-%d1%80%d0%b0%d0%b7%d0%bc%d0%b5%d1%80%d1%8b/",

}

def links_menu_kb():
    kb= InlineKeyboardBuilder()
    for name, index in LINKS_MENU_buttons.items():
        kb.button(text=name, url=index)
    kb.button(
        text="Назад в меню",
        callback_data="back_to_main_menu",

    )
    kb.adjust(1)
    return kb.as_markup()

