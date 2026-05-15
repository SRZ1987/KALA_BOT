from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from keyboards.connection_kb import connection_kb

router = Router()


@router.callback_query(F.data== "connection")
async def show_forecast(callback: CallbackQuery):

    await callback.message.edit_text(
        "Здесь всё, что касается связи.",
        reply_markup=connection_kb()
    )
    await callback.answer()