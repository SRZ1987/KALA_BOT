import asyncio
from datetime import datetime
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from dbase.admin_db import is_seller, is_test_mode_enabled
from dbase.seller_ads_db import (
    add_seller_ad,
    delete_seller_ad,
    get_all_seller_ads,
    get_seconds_until_next_post,
    get_user_seller_ads,
    set_seller_ad_channel_message,
)
from dbase.users_db import all_users
from keyboards.seller_ads_kb import (
    seller_ads_admin_kb,
    seller_ads_back_kb,
    seller_ads_menu_kb,
    seller_ads_my_kb,
)
from utils.channel import (
    get_content_channel_id,
    safe_delete_channel_message,
    safe_unpin_channel_message,
)
from utils.fsm import SellerAdState


router = Router()


def _is_admin(user_id):
    return user_id == ADMIN_ID


def _can_open_seller_ads(user_id):
    return _is_admin(user_id) or is_seller(user_id)


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


def _format_single_ad(ad):
    return _format_ads([ad], "")


def _format_public_ad(ad):
    text = (ad.get("text") or "").strip()

    if text:
        return escape(text)

    return None


async def _send_seller_ad(message, ad):
    text = _format_public_ad(ad)

    if ad.get("post_type") == "photo" and ad.get("file_id"):
        await message.answer_photo(
            ad["file_id"],
            caption=text,
            reply_markup=seller_ads_back_kb()
        )
        return

    await message.answer(
        text,
        reply_markup=seller_ads_back_kb()
    )


async def _broadcast_seller_ad(bot, ad):
    if is_test_mode_enabled():
        return 0, 0

    text = _format_public_ad(ad)
    sent = 0
    failed = 0

    for user_id in list(all_users):
        try:
            if ad.get("post_type") == "photo" and ad.get("file_id"):
                await bot.send_photo(
                    user_id,
                    ad["file_id"],
                    caption=text
                )
            else:
                await bot.send_message(user_id, text)

            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    return sent, failed


async def _publish_seller_ad_to_channel(bot, ad):
    channel_id = get_content_channel_id()

    if not channel_id:
        return None

    text = _format_public_ad(ad)

    if ad.get("post_type") == "photo" and ad.get("file_id"):
        channel_message = await bot.send_photo(
            channel_id,
            ad["file_id"],
            caption=text
        )
    else:
        channel_message = await bot.send_message(channel_id, text)

    try:
        await bot.pin_chat_message(
            channel_id,
            channel_message.message_id,
            disable_notification=True
        )
    except Exception:
        pass

    set_seller_ad_channel_message(ad["id"], channel_message.message_id)

    return channel_message


def _format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours:
        return f"{hours} ч. {minutes} мин."

    return f"{minutes} мин."


@router.callback_query(F.data == "seller_ads")
async def seller_ads_menu(callback: CallbackQuery, state: FSMContext):
    if not _can_open_seller_ads(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()

    await callback.message.edit_text(
        "Объявления продавцов",
        reply_markup=seller_ads_menu_kb(
            _can_open_seller_ads(callback.from_user.id)
        )
    )
    await callback.answer()


@router.callback_query(F.data == "seller_ads_view")
async def seller_ads_view(callback: CallbackQuery):
    if not _can_open_seller_ads(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    ads = get_all_seller_ads()

    if any(ad.get("post_type") == "photo" and ad.get("file_id") for ad in ads):
        await callback.message.edit_text(
            "Объявления продавцов:",
            reply_markup=(
                seller_ads_admin_kb(ads)
                if _is_admin(callback.from_user.id)
                else seller_ads_back_kb()
            )
        )

        for ad in ads[-20:]:
            await _send_seller_ad(callback.message, ad)

        await callback.answer()
        return

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
    if not _can_open_seller_ads(callback.from_user.id):
        await callback.answer(
            "Только продавец может добавить объявление.",
            show_alert=True
        )
        return

    seconds_left = (
        0
        if _is_admin(callback.from_user.id)
        else get_seconds_until_next_post(callback.from_user.id)
    )

    if seconds_left:
        await callback.answer(
            f"Новое объявление можно добавить через {_format_seconds(seconds_left)}.",
            show_alert=True
        )
        return

    await state.set_state(SellerAdState.text)
    await callback.message.edit_text(
        "Напиши объявление продавца одним сообщением.\n\n"
        "Можно отправить текст или фото с подписью.",
        reply_markup=seller_ads_back_kb()
    )
    await callback.answer()


@router.message(SellerAdState.text)
async def seller_ads_save(message: Message, state: FSMContext):
    if not _can_open_seller_ads(message.from_user.id):
        await state.clear()
        await message.answer(
            "Только продавец может добавить объявление."
        )
        return

    seconds_left = (
        0
        if _is_admin(message.from_user.id)
        else get_seconds_until_next_post(message.from_user.id)
    )

    if seconds_left:
        await state.clear()
        await message.answer(
            f"Новое объявление можно добавить через {_format_seconds(seconds_left)}.",
            reply_markup=seller_ads_back_kb()
        )
        return

    is_photo = bool(message.photo)
    text = (message.caption if is_photo else message.text or "").strip()

    if not is_photo and len(text) < 10:
        await message.answer("Слишком короткое объявление.")
        return

    max_length = 650 if is_photo else 900

    if len(text) > max_length:
        await message.answer(f"Умести объявление в {max_length} символов.")
        return

    ad = add_seller_ad(
        message.from_user,
        text,
        post_type="photo" if is_photo else "text",
        file_id=message.photo[-1].file_id if is_photo else None
    )
    await state.clear()
    sent, failed = await _broadcast_seller_ad(message.bot, ad)
    channel_message = await _publish_seller_ad_to_channel(message.bot, ad)
    channel_text = (
        "В канал опубликовано и закреплено."
        if channel_message
        else "Канал не настроен, в канал не отправлено."
    )
    delivery_text = (
        "Тестовый режим включен, рассылка пользователям отключена."
        if is_test_mode_enabled()
        else "Отправлено в ленту."
    )
    await message.answer(
        f"Объявление #{ad['id']} опубликовано на 7 дней.\n\n"
        f"{delivery_text}\n"
        f"{channel_text}\n\n"
        f"Доставлено: <b>{sent}</b>\n"
        f"Не удалось отправить: <b>{failed}</b>",
        reply_markup=seller_ads_back_kb()
    )


@router.callback_query(F.data == "seller_ads_my")
async def seller_ads_my(callback: CallbackQuery):
    if not _can_open_seller_ads(callback.from_user.id):
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

    await safe_unpin_channel_message(
        callback.message.bot,
        deleted.get("channel_message_id")
    )
    await safe_delete_channel_message(
        callback.message.bot,
        deleted.get("channel_message_id")
    )

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
    deleted = delete_seller_ad(ad_id)
    if deleted:
        await safe_unpin_channel_message(
            callback.message.bot,
            deleted.get("channel_message_id")
        )
        await safe_delete_channel_message(
            callback.message.bot,
            deleted.get("channel_message_id")
        )
    ads = get_all_seller_ads()

    await callback.message.edit_text(
        _format_ads(ads, "Активных объявлений продавцов пока нет."),
        reply_markup=seller_ads_admin_kb(ads)
    )
    await callback.answer("Удалено")
