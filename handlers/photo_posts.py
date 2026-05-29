import asyncio
from datetime import datetime
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from dbase.photo_posts_db import (
    add_photo_post,
    get_photo_posts,
    get_seconds_until_next_photo,
)
from dbase.users_db import all_users
from keyboards.photo_posts_kb import (
    photo_posts_back_kb,
    photo_posts_menu_kb,
)
from utils.fsm import PhotoPostState


router = Router()


def _is_admin(user_id):
    return user_id == ADMIN_ID


def _format_date(value):
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y %H:%M")
    except (TypeError, ValueError):
        return "неизвестно"


def _format_author(post):
    username = post.get("username")

    if username:
        return f"@{escape(username)}"

    return escape(post.get("full_name") or "без username")


def _format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours:
        return f"{hours} ч. {minutes} мин."

    return f"{minutes} мин."


def _caption(post):
    header = (
        f"Автор: {_format_author(post)}\n"
        f"Дата: {_format_date(post.get('created_at'))}"
    )
    text = post.get("text")

    if text:
        return f"{header}\n\n{escape(text)}"

    return header


async def _broadcast_post(bot, post):
    post_type = post.get("post_type")
    file_id = post.get("file_id")
    caption = _caption(post)

    for user_id in list(all_users):
        try:
            if post_type == "photo" and file_id:
                await bot.send_photo(user_id, file_id, caption=caption)
            elif post_type == "voice" and file_id:
                await bot.send_voice(user_id, file_id, caption=caption)
            elif post_type == "text":
                await bot.send_message(user_id, caption)

            await asyncio.sleep(0.05)
        except Exception:
            continue


@router.callback_query(F.data == "photo_posts")
async def photo_posts_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Фото дня\n\n"
        "Каждый пользователь может добавить одно фото в сутки. "
        "Админ может добавлять сообщения, фото и голосовые без ограничений.",
        reply_markup=photo_posts_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "photo_posts_view")
async def photo_posts_view(callback: CallbackQuery):
    posts = get_photo_posts()

    if not posts:
        await callback.message.edit_text(
            "В ленте пока ничего нет.",
            reply_markup=photo_posts_back_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "Лента фото дня:",
        reply_markup=photo_posts_back_kb()
    )

    for post in posts[-20:]:
        post_type = post.get("post_type")
        file_id = post.get("file_id")

        if post_type == "photo" and file_id:
            await callback.message.answer_photo(
                file_id,
                caption=_caption(post)
            )
        elif post_type == "voice" and file_id:
            await callback.message.answer_voice(
                file_id,
                caption=_caption(post)
            )
        elif post_type == "text":
            await callback.message.answer(
                _caption(post)
            )

    await callback.message.answer(
        "Конец ленты.",
        reply_markup=photo_posts_back_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "photo_posts_add")
async def photo_posts_add(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        seconds_left = get_seconds_until_next_photo(callback.from_user.id)

        if seconds_left:
            await callback.answer(
                f"Новое фото можно добавить через {_format_seconds(seconds_left)}.",
                show_alert=True
            )
            return

    await state.set_state(PhotoPostState.content)
    await callback.message.edit_text(
        "Отправь фото с описанием в подписи.\n\n"
        "Админ также может отправить текст или голосовое.",
        reply_markup=photo_posts_back_kb()
    )
    await callback.answer()


@router.message(PhotoPostState.content)
async def photo_posts_save(message: Message, state: FSMContext):
    is_admin = _is_admin(message.from_user.id)

    if message.photo:
        if not is_admin:
            seconds_left = get_seconds_until_next_photo(message.from_user.id)

            if seconds_left:
                await state.clear()
                await message.answer(
                    f"Новое фото можно добавить через {_format_seconds(seconds_left)}.",
                    reply_markup=photo_posts_back_kb()
                )
                return

        post = add_photo_post(
            message.from_user,
            "photo",
            file_id=message.photo[-1].file_id,
            text=message.caption
        )
        await _broadcast_post(message.bot, post)
        await state.clear()
        await message.answer(
            "Фото опубликовано и отправлено в общую ленту.",
            reply_markup=photo_posts_back_kb()
        )
        return

    if is_admin and message.voice:
        post = add_photo_post(
            message.from_user,
            "voice",
            file_id=message.voice.file_id,
            text=message.caption
        )
        await _broadcast_post(message.bot, post)
        await state.clear()
        await message.answer(
            "Голосовое опубликовано и отправлено в общую ленту.",
            reply_markup=photo_posts_back_kb()
        )
        return

    if is_admin and message.text:
        post = add_photo_post(
            message.from_user,
            "text",
            text=message.text
        )
        await _broadcast_post(message.bot, post)
        await state.clear()
        await message.answer(
            "Сообщение опубликовано и отправлено в общую ленту.",
            reply_markup=photo_posts_back_kb()
        )
        return

    await message.answer(
        "Отправь фото. Описание можно добавить в подписи к фото."
    )


@router.message(F.photo)
async def photo_posts_direct_photo(message: Message):
    is_admin = _is_admin(message.from_user.id)

    if not is_admin:
        seconds_left = get_seconds_until_next_photo(message.from_user.id)

        if seconds_left:
            await message.answer(
                f"Новое фото можно добавить через {_format_seconds(seconds_left)}.",
                reply_markup=photo_posts_back_kb()
            )
            return

    post = add_photo_post(
        message.from_user,
        "photo",
        file_id=message.photo[-1].file_id,
        text=message.caption
    )
    await _broadcast_post(message.bot, post)
    await message.answer(
        "Фото опубликовано в общей ленте.",
        reply_markup=photo_posts_back_kb()
    )
