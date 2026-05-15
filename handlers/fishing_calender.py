from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from keyboards.city_keyboard import get_city_keyboard

router = Router()


@router.callback_query(F.data== "fishing_calender_main_menu")
async def show_forecast(callback: CallbackQuery):

    await callback.message.edit_text(
        "Прогноз на рыбалку на 1 день иои несколько дней!",
        reply_markup=get_city_keyboard()
    )
    await callback.answer()