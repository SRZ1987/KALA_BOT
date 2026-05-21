from datetime import datetime
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from dbase.admin_db import is_seller
from dbase.seller_ads_db import (
    add_seller_ad,
    delete_seller_ad,
    get_all_seller_ads,
    get_seconds_until_next_post,
    get_user_seller_ads,
)
from keyboards.seller_ads_kb import (
    seller_ads_admin_kb,
    seller_ads_back_kb,
    seller_ads_menu_kb,
    seller_ads_my_kb,
)
from utils.fsm import SellerAdState


router = Router()


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
        lines.append(
            "\n".join(
                [
                    f"<b>{number}. Объявление продавца #{ad['id']}</b>",
                    f"Автор: {_format_contact(ad)}",
                    f"ID: <code>{ad.get('user_id')}</code>",
                    f"До: {_format_date(ad.get('expires_at'))}",
                    "",
                    escape(ad.get("text", "")),
                ]
            )
        )

    return "\n\n".join(lines)


def _format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours:
        return f"{hours} ч. {minutes} мин."

    return f"{minutes} мин."


@router.callback_query(F.data == "seller_ads")
async def seller_ads_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        "Объявления продавцов",
        reply_markup=seller_ads_menu_kb(
            is_seller(callback.from_user.id)
        )
    )
    await callback.answer()


@router.callback_query(F.data == "seller_ads_view")
async def seller_ads_view(callback: CallbackQuery):
    ads = get_all_seller_ads()

    await callback.message.edit_text(
        _format_ads(ads, "Активных объявлений продавцов пока нет."),
        reply_markup=(
            seller_ads_admin_kb(ads)
            if _is_admin(callback.from_user.id)
            else seller_ads_back_kb()
        )
    )
    await callback.answer()


@router.callback_query(F.data == "seller_ads_add")
async def seller_ads_add(callback: CallbackQuery, state: FSMContext):
    if not is_seller(callback.from_user.id):
        await callback.answer(
            "Только продавец может добавить объявление.",
            show_alert=True
        )
        return

    seconds_left = get_seconds_until_next_post(callback.from_user.id)

    if seconds_left:
        await callback.answer(
            f"Новое объявление можно добавить через {_format_seconds(seconds_left)}.",
            show_alert=True
        )
        return

    await state.set_state(SellerAdState.text)
    await callback.message.edit_text(
        "Напиши объявление продавца одним сообщением.",
        reply_markup=seller_ads_back_kb()
    )
    await callback.answer()


@router.message(SellerAdState.text)
async def seller_ads_save(message: Message, state: FSMContext):
    if not is_seller(message.from_user.id):
        await state.clear()
        await message.answer(
            "Только продавец может добавить объявление."
        )
        return

    seconds_left = get_seconds_until_next_post(message.from_user.id)

    if seconds_left:
        await state.clear()
        await message.answer(
            f"Новое объявление можно добавить через {_format_seconds(seconds_left)}.",
            reply_markup=seller_ads_back_kb()
        )
        return

    text = (message.text or "").strip()

    if len(text) < 10:
        await message.answer("Слишком короткое объявление.")
        return

    if len(text) > 900:
        await message.answer("Умести объявление в 900 символов.")
        return

    ad = add_seller_ad(message.from_user, text)
    await state.clear()
    await message.answer(
        f"Объявление #{ad['id']} опубликовано на 7 дней.",
        reply_markup=seller_ads_back_kb()
    )


@router.callback_query(F.data == "seller_ads_my")
async def seller_ads_my(callback: CallbackQuery):
    if not is_seller(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    ads = get_user_seller_ads(callback.from_user.id)

    await callback.message.edit_text(
        _format_ads(ads, "У тебя пока нет активных объявлений продавца."),
        reply_markup=seller_ads_my_kb(ads)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("seller_ads_delete:"))
async def seller_ads_delete(callback: CallbackQuery):
    ad_id = callback.data.split(":")[1]
    deleted = delete_seller_ad(ad_id, callback.from_user.id)

    if not deleted:
        await callback.answer("Объявление не найдено.", show_alert=True)
        return

    ads = get_user_seller_ads(callback.from_user.id)

    await callback.message.edit_text(
        _format_ads(ads, "Объявление удалено. Активных объявлений больше нет."),
        reply_markup=seller_ads_my_kb(ads)
    )
    await callback.answer("Удалено")


@router.callback_query(F.data.startswith("admin_seller_ad_delete:"))
async def admin_seller_ad_delete(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    ad_id = callback.data.split(":")[1]
    delete_seller_ad(ad_id)
    ads = get_all_seller_ads()

    await callback.message.edit_text(
        _format_ads(ads, "Активных объявлений продавцов пока нет."),
        reply_markup=seller_ads_admin_kb(ads)
    )
    await callback.answer("Удалено")
