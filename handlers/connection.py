from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.connection_kb import connection_kb


router = Router()


@router.callback_query(F.data == "connection")
async def show_connection(callback: CallbackQuery):
    await callback.message.edit_text(
        "Здесь всё, что касается связи.",
        reply_markup=connection_kb()
    )
    await callback.answer()
