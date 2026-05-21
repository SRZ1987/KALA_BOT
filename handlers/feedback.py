from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from keyboards.back_kb import back_kb
from utils.fsm import FeedbackState
from utils.logger import logger


router = Router()


@router.callback_query(F.data == "feedback")
async def feedback_start(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(
        FeedbackState.waiting_feedback
    )

    try:
        await callback.message.edit_text(
            "Напиши сообщение администратору.\n"
            "Можно отправить текст, фото или голосовое.",
            reply_markup=back_kb()
        )

    except TelegramBadRequest:
        pass

    await callback.answer()


@router.message(FeedbackState.waiting_feedback)
async def feedback_receive(
        message: Message,
        state: FSMContext,
        bot: Bot
):
    user = message.from_user

    info = (
        "Новое сообщение администратору\n\n"
        f"Имя: {user.full_name}\n"
        f"User ID / Telegram ID: <code>{user.id}</code>\n"
    )

    if user.username:
        info += f"Username: @{user.username}\n"

    try:
        await bot.send_message(
            ADMIN_ID,
            info
        )

        await bot.forward_message(
            ADMIN_ID,
            message.chat.id,
            message.message_id
        )

        await message.answer(
            "Спасибо, сообщение отправлено администратору.",
            reply_markup=back_kb()
        )

    except Exception as e:
        logger.exception(e)

        await message.answer(
            "Ошибка отправки сообщения.",
            reply_markup=back_kb()
        )

    await state.clear()
