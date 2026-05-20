from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import ADMIN_ID
from keyboards.main_menu_kb import main_menu_kb


router = Router()


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Вы в главном меню",
        reply_markup=main_menu_kb(
            callback.from_user.id == ADMIN_ID
        )
    )
    await callback.answer()
