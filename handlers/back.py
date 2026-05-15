from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from keyboards.main_menu_kb import main_menu_kb

router = Router()

@router.callback_query(F.data== "back_to_main_menu")
async def show_forecast(callback: CallbackQuery):

    await callback.message.edit_text(
        "Вы в главном меню",
        reply_markup=main_menu_kb()
    )
    await callback.answer()




