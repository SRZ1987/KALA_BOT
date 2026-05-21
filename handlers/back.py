from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from config import ADMIN_ID
from keyboards.main_menu_kb import main_menu_kb


router = Router()


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Вы в главном меню",
        reply_markup=main_menu_kb(
            callback.from_user.id == ADMIN_ID
        )
    )
    await callback.answer()


@router.message(F.text == "Назад")
async def back_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы в главном меню",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "Главное меню",
        reply_markup=main_menu_kb(
            message.from_user.id == ADMIN_ID
        )
    )
