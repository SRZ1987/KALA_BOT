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
)
from dbase.sos_db import delete_sos_report, get_sos_reports
from dbase.users_db import all_users
from keyboards.admin_kb import (
    admin_back_kb,
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


def _format_sellers():
    sellers = get_sellers()

    if not sellers:
        return "Продавцов пока нет."

    lines = ["Продавцы:"]

    for seller_id, data in sellers.items():
        lines.append(
            f"ID: <code>{seller_id}</code> | добавлен: "
            f"{_format_date(data.get('added_at'))}"
        )

    return "\n".join(lines)


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
                    f"ID: <code>{report.get('user_id')}</code>",
                    f"Телефон: {escape(str(report.get('phone', '')))}",
                    f"Дата: {_format_date(report.get('created_at'))}",
                    "",
                    escape(report.get("problem", "")),
                ]
            )
        )

    return "\n\n".join(lines)


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


@router.callback_query(F.data == "admin_sellers_list")
async def admin_sellers_list(callback: CallbackQuery):
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
        banned_id = ban_user(_parse_user_id(message.text))
    except ValueError:
        await message.answer("Нужен числовой user id.")
        return

    await state.clear()
    await message.answer(
        f"Пользователь <code>{banned_id}</code> забанен.",
        reply_markup=admin_menu_kb()
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
