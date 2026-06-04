from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from keyboards.links_kb import links_menu_kb

router = Router()


@router.callback_query(F.data== "useful_links")
async def show_forecast(callback: CallbackQuery):

    await callback.message.edit_text(
        "<b>Полезные ссылки</b>\n\n"
        "Собрал быстрые ссылки, которые могут пригодиться перед рыбалкой, поездкой или проверкой условий.",
        reply_markup=links_menu_kb()
    )
    await callback.answer()
