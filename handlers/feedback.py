from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from utils.logger import logger

router = Router()

from utils.fsm import FeedbackState
from keyboards.back_kb import back_kb


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
            "💬 Напиши отзыв.\n"
            "Можно текст, фото или голосовое."
        )

    except TelegramBadRequest:
        pass

    await callback.answer()


# =========================================================
# 💬 ПОЛУЧЕНИЕ ОТЗЫВА
# =========================================================

@router.message(FeedbackState.waiting_feedback)
async def feedback_receive(
        message: Message,
        state: FSMContext,
        bot: Bot
):

    user = message.from_user

    info = (
        f"📩 Новый отзыв\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 <code>{user.id}</code>\n"
    )

    if user.username:
        info += f"📎 @{user.username}\n"

    try:

        await bot.forward_message(
            ADMIN_ID,
            message.chat.id,
            message.message_id
        )

        await bot.send_message(
            ADMIN_ID,
            info
        )

        await message.answer(
            "✅ Спасибо за отзыв!",
            reply_markup=back_kb()
        )

    except Exception as e:

        logger.exception(e)

        await message.answer(
            "❌ Ошибка отправки.",
            reply_markup=back_kb()
        )

    await state.clear()
