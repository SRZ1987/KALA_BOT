from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import ADMIN_ID
from dbase.users_db import all_users
from keyboards.admin_kb import admin_menu_kb


router = Router()


def is_admin(user_id):
    return user_id == ADMIN_ID


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Нет доступа",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "Админка",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(
            "Нет доступа",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "Статистика\n\n"
        f"Общее количество подписчиков: <b>{len(all_users)}</b>",
        reply_markup=admin_menu_kb()
    )
    await callback.answer()
