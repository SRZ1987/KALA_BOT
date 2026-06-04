from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from config import ADMIN_ID
from dbase.admin_db import is_seller
from keyboards.main_menu_kb import main_menu_kb
from utils.menu_text import main_menu_text


router = Router()


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin = callback.from_user.id == ADMIN_ID
    seller = is_seller(callback.from_user.id)

    await callback.message.edit_text(
        main_menu_text(
            is_admin=is_admin,
            is_seller=seller
        ),
        reply_markup=main_menu_kb(
            is_admin=is_admin,
            is_seller=seller
        )
    )
    await callback.answer()


@router.message(F.text == "Назад")
async def back_message(message: Message, state: FSMContext):
    await state.clear()
    is_admin = message.from_user.id == ADMIN_ID
    seller = is_seller(message.from_user.id)

    await message.answer(
        "Вы в главном меню",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        main_menu_text(
            is_admin=is_admin,
            is_seller=seller
        ),
        reply_markup=main_menu_kb(
            is_admin=is_admin,
            is_seller=seller
        )
    )
