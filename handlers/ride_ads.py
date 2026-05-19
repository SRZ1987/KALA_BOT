from datetime import datetime
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from dbase.rides_db import (
    add_ride_ad,
    delete_user_ad,
    get_ads_by_city,
    get_user_ads,
)
from keyboards.rides_kb import (
    CITY_ITEMS,
    rides_back_kb,
    rides_city_kb,
    rides_menu_kb,
    rides_my_ads_kb,
    rides_type_kb,
)
from utils.fsm import RideAdState


router = Router()

AD_TYPES = {
    "need": "Ищу попутчика",
    "offer": "Есть место в машине",
}


def _format_date(value):
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y")
    except (TypeError, ValueError):
        return "неизвестно"


def _format_contact(ad):
    username = ad.get("username")

    if username:
        return f"@{escape(username)}"

    return escape(ad.get("full_name") or "без username")


def _format_ads(ads, empty_text):
    if not ads:
        return empty_text

    lines = []

    for number, ad in enumerate(ads, start=1):
        ad_type = AD_TYPES.get(
            ad.get("ad_type"),
            "Объявление"
        )

        lines.append(
            "\n".join(
                [
                    f"<b>{number}. {escape(ad_type)}</b>",
                    f"Город: <b>{escape(ad.get('city_name', ''))}</b>",
                    f"Автор: {_format_contact(ad)}",
                    f"До: {_format_date(ad.get('expires_at'))}",
                    "",
                    escape(ad.get("text", "")),
                ]
            )
        )

    return "\n\n".join(lines)


@router.callback_query(F.data == "rides")
async def rides_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        "Попутчики\n\n"
        "Здесь можно найти место в машине или оставить объявление. "
        "Объявления удаляются автоматически через 7 дней.",
        reply_markup=rides_menu_kb()
    )

    await callback.answer()


@router.callback_query(F.data == "rides_view")
async def rides_view(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери город, по которому показать объявления:",
        reply_markup=rides_city_kb("rides_view_city")
    )

    await callback.answer()


@router.callback_query(F.data.startswith("rides_view_city:"))
async def rides_view_city(callback: CallbackQuery):
    city_index = int(callback.data.split(":")[1])
    city_name, city_key = CITY_ITEMS[city_index]
    ads = get_ads_by_city(city_key)

    text = _format_ads(
        ads,
        f"По городу <b>{escape(city_name)}</b> пока нет объявлений."
    )

    await callback.message.edit_text(
        text,
        reply_markup=rides_back_kb()
    )

    await callback.answer()


@router.callback_query(F.data == "rides_add")
async def rides_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RideAdState.city)

    await callback.message.edit_text(
        "Выбери город для объявления:",
        reply_markup=rides_city_kb("rides_add_city")
    )

    await callback.answer()


@router.callback_query(F.data.startswith("rides_add_city:"))
async def rides_add_city(callback: CallbackQuery, state: FSMContext):
    city_index = int(callback.data.split(":")[1])
    city_name, city_key = CITY_ITEMS[city_index]

    await state.update_data(
        city_name=city_name,
        city_key=city_key
    )
    await state.set_state(RideAdState.ad_type)

    await callback.message.edit_text(
        "Что добавить?",
        reply_markup=rides_type_kb()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("rides_type:"))
async def rides_type(callback: CallbackQuery, state: FSMContext):
    ad_type = callback.data.split(":")[1]

    if ad_type not in AD_TYPES:
        await callback.answer("Неизвестный тип объявления", show_alert=True)
        return

    await state.update_data(ad_type=ad_type)
    await state.set_state(RideAdState.text)

    await callback.message.edit_text(
        "Напиши текст объявления одним сообщением.\n\n"
        "Например: есть место в машине, еду завтра в 10:00 из Таллинна "
        "в Тарту, 2 места, связь через Telegram."
    )

    await callback.answer()


@router.message(RideAdState.text)
async def rides_save(message: Message, state: FSMContext):
    text = (message.text or "").strip()

    if len(text) < 10:
        await message.answer(
            "Слишком коротко. Напиши, куда и когда едешь, "
            "или кого ищешь."
        )
        return

    if len(text) > 900:
        await message.answer(
            "Слишком длинное объявление. Умести текст в 900 символов."
        )
        return

    data = await state.get_data()
    ad = add_ride_ad(
        user=message.from_user,
        city_key=data["city_key"],
        city_name=data["city_name"],
        ad_type=data["ad_type"],
        text=text
    )

    await state.clear()

    await message.answer(
        f"Готово. Объявление #{ad['id']} опубликовано на 7 дней.",
        reply_markup=rides_back_kb()
    )


@router.callback_query(F.data == "rides_my")
async def rides_my(callback: CallbackQuery):
    ads = get_user_ads(callback.from_user.id)
    text = _format_ads(
        ads,
        "У тебя пока нет активных объявлений."
    )

    await callback.message.edit_text(
        text,
        reply_markup=rides_my_ads_kb(ads)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("rides_delete:"))
async def rides_delete(callback: CallbackQuery):
    ad_id = callback.data.split(":")[1]
    deleted = delete_user_ad(ad_id, callback.from_user.id)

    if not deleted:
        await callback.answer(
            "Не нашел твое объявление или оно уже удалено.",
            show_alert=True
        )
        return

    ads = get_user_ads(callback.from_user.id)
    text = _format_ads(
        ads,
        "Объявление удалено. Активных объявлений больше нет."
    )

    await callback.message.edit_text(
        text,
        reply_markup=rides_my_ads_kb(ads)
    )

    await callback.answer("Удалено")
