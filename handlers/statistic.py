import asyncio
from datetime import datetime
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from dbase.admin_db import (
    add_seller,
    ban_user,
    delete_seller,
    get_banned_users,
    get_sellers,
    unban_user,
)
from dbase.sos_db import delete_sos_report, get_sos_reports
from dbase.users_db import all_users
from keyboards.admin_kb import (
    admin_back_kb,
    admin_bans_kb,
    admin_menu_kb,
    admin_sellers_kb,
    admin_sos_kb,
)
from utils.fsm import AdminState


router = Router()


def is_admin(user_id):
    return user_id == ADMIN_ID


def _parse_user_id(text):
    return int((text or "").strip())


def _format_date(value):
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y %H:%M")
    except (TypeError, ValueError):
        return "неизвестно"


def _get_known_username(user_id):
    user = all_users.get(str(user_id), {})

    return user.get("username")


def _format_sellers():
    sellers = get_sellers()

    if not sellers:
        return "Продавцов пока нет."

    lines = ["Продавцы:"]

    for seller_id, data in sellers.items():
        username = _get_known_username(seller_id) or data.get("username") or "имя неизвестно"
        lines.append(
            f"User ID / Telegram ID: <code>{seller_id}</code>\n"
            f"Имя: {escape(str(username))}\n"
            f"Добавлен: {_format_date(data.get('added_at'))}"
        )

    return "\n\n".join(lines)


def _format_banned_users():
    banned_users = get_banned_users()

    if not banned_users:
        return "Бан-лист пуст."

    lines = ["Бан-лист:"]

    for banned_id, data in banned_users.items():
        username = (
            _get_known_username(banned_id)
            or data.get("username")
            or "имя неизвестно"
        )
        lines.append(
            f"User ID / Telegram ID: <code>{banned_id}</code>\n"
            f"Имя: {escape(str(username))}\n"
            f"Забанен: {_format_date(data.get('banned_at'))}"
        )

    return "\n\n".join(lines)


def _format_sos_reports(reports):
    if not reports:
        return "SOS сообщений пока нет."

    lines = ["SOS сообщения:"]

    for number, report in enumerate(reports, start=1):
        username = report.get("username")
        contact = f"@{escape(username)}" if username else escape(
            report.get("full_name") or "без username"
        )
        lines.append(
            "\n".join(
                [
                    f"<b>{number}. SOS #{report['id']}</b>",
                    f"Автор: {contact}",
                    f"User ID / Telegram ID: <code>{report.get('user_id')}</code>",
                    f"Телефон: {escape(str(report.get('phone', '')))}",
                    f"Дата: {_format_date(report.get('created_at'))}",
                    "",
                    escape(report.get("problem", "")),
                ]
            )
        )

    return "\n\n".join(lines)


def _parse_poll(text):
    lines = [
        line.strip()
        for line in (text or "").splitlines()
        if line.strip()
    ]

    if len(lines) < 3:
        raise ValueError("poll_lines")

    question = lines[0]
    options = lines[1:]

    if len(question) > 300:
        raise ValueError("question_long")

    if len(options) > 10:
        raise ValueError("too_many_options")

    if any(len(option) > 100 for option in options):
        raise ValueError("option_long")

    return question, options


async def _broadcast_poll(bot, question, options):
    sent = 0
    failed = 0

    for user_id in list(all_users):
        try:
            await bot.send_poll(
                user_id,
                question=question,
                options=options,
                is_anonymous=False
            )
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    return sent, failed


async def _broadcast_native_poll(message):
    sent = 0
    failed = 0

    for user_id in list(all_users):
        try:
            await message.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    return sent, failed


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        "Админка",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        "Статистика\n\n"
        f"Общее количество подписчиков: <b>{len(all_users)}</b>\n"
        f"Продавцов: <b>{len(get_sellers())}</b>\n"
        f"Забанено: <b>{len(get_banned_users())}</b>",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_sellers")
async def admin_sellers(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        _format_sellers(),
        reply_markup=admin_sellers_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_seller_add")
async def admin_seller_add(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.set_state(AdminState.add_seller)
    await callback.message.edit_text(
        "Напиши user id продавца, которого нужно добавить.",
        reply_markup=admin_back_kb()
    )
    await callback.answer()


@router.message(AdminState.add_seller)
async def admin_seller_add_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        seller_id = add_seller(_parse_user_id(message.text))
    except ValueError:
        await message.answer("Нужен числовой user id.")
        return

    await state.clear()
    await message.answer(
        f"Продавец <code>{seller_id}</code> добавлен.",
        reply_markup=admin_sellers_kb()
    )


@router.callback_query(F.data == "admin_seller_delete")
async def admin_seller_delete(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.set_state(AdminState.delete_seller)
    await callback.message.edit_text(
        "Напиши user id продавца, которого нужно удалить.",
        reply_markup=admin_back_kb()
    )
    await callback.answer()


@router.message(AdminState.delete_seller)
async def admin_seller_delete_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = _parse_user_id(message.text)
    except ValueError:
        await message.answer("Нужен числовой user id.")
        return

    deleted = delete_seller(user_id)
    await state.clear()

    if deleted:
        await message.answer(
            f"Продавец <code>{user_id}</code> удален.",
            reply_markup=admin_sellers_kb()
        )
        return

    await message.answer(
        f"Продавец <code>{user_id}</code> не найден.",
        reply_markup=admin_sellers_kb()
    )


@router.callback_query(F.data == "admin_bans")
async def admin_bans(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        _format_banned_users(),
        reply_markup=admin_bans_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_ban_user")
async def admin_ban_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.set_state(AdminState.ban_user)
    await callback.message.edit_text(
        "Напиши user id пользователя, которого нужно забанить.",
        reply_markup=admin_back_kb()
    )
    await callback.answer()


@router.message(AdminState.ban_user)
async def admin_ban_user_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = _parse_user_id(message.text)
        banned_id = ban_user(
            user_id,
            username=_get_known_username(user_id)
        )
    except ValueError:
        await message.answer("Нужен числовой user id.")
        return

    await state.clear()
    await message.answer(
        f"Пользователь <code>{banned_id}</code> забанен.",
        reply_markup=admin_bans_kb()
    )


@router.callback_query(F.data == "admin_unban_user")
async def admin_unban_user(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.set_state(AdminState.unban_user)
    await callback.message.edit_text(
        "Напиши user id пользователя, которого нужно удалить из бана.",
        reply_markup=admin_back_kb()
    )
    await callback.answer()


@router.message(AdminState.unban_user)
async def admin_unban_user_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    try:
        user_id = _parse_user_id(message.text)
    except ValueError:
        await message.answer("Нужен числовой user id.")
        return

    deleted = unban_user(user_id)
    await state.clear()

    if deleted:
        await message.answer(
            f"Пользователь <code>{user_id}</code> удален из бана.",
            reply_markup=admin_bans_kb()
        )
        return

    await message.answer(
        f"Пользователь <code>{user_id}</code> не найден в бан-листе.",
        reply_markup=admin_bans_kb()
    )


@router.callback_query(F.data == "admin_sos")
async def admin_sos(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    reports = get_sos_reports()

    await callback.message.edit_text(
        _format_sos_reports(reports),
        reply_markup=admin_sos_kb(reports)
    )
    await callback.answer()


@router.callback_query(F.data == "admin_poll")
async def admin_poll(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.set_state(AdminState.poll)
    await callback.message.edit_text(
        "Напиши голосование одним сообщением:\n\n"
        "1 строка - вопрос\n"
        "2 строка - первый вариант\n"
        "3 строка - второй вариант\n\n"
        "Можно добавить до 10 вариантов.",
        reply_markup=admin_back_kb()
    )
    await callback.answer()


@router.message(AdminState.poll)
async def admin_poll_send(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    if message.poll:
        sent, failed = await _broadcast_native_poll(message)
        await state.clear()
        await message.answer(
            "Голосование отправлено.\n\n"
            f"Доставлено: <b>{sent}</b>\n"
            f"Не удалось отправить: <b>{failed}</b>",
            reply_markup=admin_menu_kb()
        )
        return

    try:
        question, options = _parse_poll(message.text)
    except ValueError as error:
        reason = str(error)

        if reason == "question_long":
            await message.answer("Вопрос слишком длинный. Максимум 300 символов.")
        elif reason == "too_many_options":
            await message.answer("Слишком много вариантов. Максимум 10.")
        elif reason == "option_long":
            await message.answer("Один из вариантов слишком длинный. Максимум 100 символов.")
        else:
            await message.answer(
                "Нужно минимум 3 строки: вопрос и хотя бы 2 варианта ответа."
            )
        return

    sent, failed = await _broadcast_poll(message.bot, question, options)
    await state.clear()
    await message.answer(
        "Голосование отправлено.\n\n"
        f"Доставлено: <b>{sent}</b>\n"
        f"Не удалось отправить: <b>{failed}</b>",
        reply_markup=admin_menu_kb()
    )


@router.message(F.poll)
async def admin_native_poll(message: Message):
    if not is_admin(message.from_user.id):
        return

    sent, failed = await _broadcast_native_poll(message)
    await message.answer(
        "Голосование отправлено.\n\n"
        f"Доставлено: <b>{sent}</b>\n"
        f"Не удалось отправить: <b>{failed}</b>",
        reply_markup=admin_menu_kb()
    )


@router.callback_query(F.data.startswith("admin_sos_delete:"))
async def admin_sos_delete(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    report_id = callback.data.split(":")[1]
    delete_sos_report(report_id)
    reports = get_sos_reports()

    await callback.message.edit_text(
        _format_sos_reports(reports),
        reply_markup=admin_sos_kb(reports)
    )
    await callback.answer("Удалено")
