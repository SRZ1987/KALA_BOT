from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from utils.anti_spam import check_spam
from constants.est_cit import CITIES
from dbase.data_dase import user_city
from dbase.users_db import  all_users
from aiogram import Router, F
from keyboards.main_keyboard import get_main_keyboard
from config import ADMIN_ID

router = Router()

@router.callback_query(F.data.startswith("city_"))
async def select_city(callback: CallbackQuery):

    if not check_spam(callback.from_user.id):
        await callback.answer(
            "Не так быстро 😅",
            show_alert=True
        )
        return

    city_ru = callback.data[5:]
    city_eng = CITIES[city_ru]

    user_city[callback.from_user.id] = city_eng

    all_users.add(callback.from_user.id)

    try:

        await callback.message.edit_text(
            f"✅ Выбран город: <b>{city_ru}</b>\n\n"
            f"Что показать?",
            reply_markup=get_main_keyboard(
                callback.from_user.id == ADMIN_ID
            )
        )

    except TelegramBadRequest:
        pass

    await callback.answer()

