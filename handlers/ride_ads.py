from datetime import datetime
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from dbase.rides_db import (
    add_ride_ad,
    delete_user_ad,
    get_all_ads,
    get_user_ads,
)
from keyboards.rides_kb import (
    rides_admin_ads_kb,
    rides_back_inline_kb,
    rides_back_kb,
    rides_menu_kb,
    rides_my_ads_kb,
)
from utils.channel import get_content_channel_id
from utils.fsm import RideAdState


router = Router()

AD_TYPES = {
    "need": "Ищу попутчика",
    "offer": "Ищу попутчика",
}


def _is_admin(user_id):
    return user_id == ADMIN_ID


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
                    f"<b>{number}. {escape(ad_type)} #{ad['id']}</b>",
                    f"Автор: {_format_contact(ad)}",
                    f"ID: <code>{ad.get('user_id')}</code>",
                    f"До: {_format_date(ad.get('expires_at'))}",
                    "",
                    escape(ad.get("text", "")),
                ]
            )
        )

    return "\n\n".join(lines)


def _format_public_ad(ad):
    return escape((ad.get("text") or "").strip())


async def _publish_ride_ad_to_channel(bot, ad):
    channel_id = get_content_channel_id()

    if not channel_id:
        return None

    try:
        return await bot.send_message(channel_id, _format_public_ad(ad))
    except Exception:
        return None


@router.callback_query(F.data == "rides")
async def rides_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        "Попутчики\n\n"
        "Здесь можно найти попутчика или оставить объявление. "
        "Объявления удаляются автоматически через 7 дней.",
        reply_markup=rides_menu_kb()
    )

    await callback.answer()


@router.callback_query(F.data == "rides_view")
async def rides_view(callback: CallbackQuery):
    ads = get_all_ads()
    text = _format_ads(
        ads,
        "Активных объявлений пока нет."
    )

    await callback.message.edit_text(
        text,
        reply_markup=(
            rides_admin_ads_kb(ads)
            if _is_admin(callback.from_user.id)
            else rides_back_kb()
        )
    )

    await callback.answer()


@router.callback_query(F.data == "rides_add")
async def rides_add(callback: CallbackQuery, state: FSMContext):
    await state.update_data(ad_type="need")
    await state.set_state(RideAdState.text)

    await callback.message.edit_text(
        "Напиши текст объявления одним сообщением.\n\n"
        "Например: ищу попутчика, еду завтра в 10:00 из Таллинна "
        "в Тарту, связь через Telegram.",
        reply_markup=rides_back_inline_kb()
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
        ad_type=data["ad_type"],
        text=text
    )

    await state.clear()
    channel_message = await _publish_ride_ad_to_channel(message.bot, ad)
    channel_text = (
        "Отправлено в канал."
        if channel_message
        else "Канал не настроен, в канал не отправлено."
    )

    await message.answer(
        f"Готово. Объявление #{ad['id']} опубликовано на 7 дней.\n\n"
        f"{channel_text}",
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


@router.callback_query(F.data.startswith("admin_ride_delete:"))
async def admin_ride_delete(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    ad_id = callback.data.split(":")[1]
    delete_user_ad(ad_id)
    ads = get_all_ads()
    text = _format_ads(
        ads,
        "Активных объявлений пока нет."
    )

    await callback.message.edit_text(
        text,
        reply_markup=rides_admin_ads_kb(ads)
    )
    await callback.answer("Удалено")
