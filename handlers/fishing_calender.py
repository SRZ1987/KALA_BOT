from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.city_keyboard import get_city_keyboard


router = Router()


@router.callback_query(F.data == "fishing_calender_main_menu")
async def show_forecast(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери город для прогноза:",
        reply_markup=get_city_keyboard()
    )
    await callback.answer()
