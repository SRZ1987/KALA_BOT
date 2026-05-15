from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID
from dbase.data_dase import all_users
from keyboards.main_keyboard import get_main_keyboard
from aiogram import Router,F

router = Router()


@router.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:

        await callback.answer(
            "Нет доступа",
            show_alert=True
        )

        return

    try:

        await callback.message.edit_text(
            f"📊 <b>Статистика</b>\n\n"
            f"👥 Пользователей: "
            f"<b>{len(all_users)}</b>",
            reply_markup=get_main_keyboard(True)
        )

    except TelegramBadRequest:
        pass

    await callback.answer()

