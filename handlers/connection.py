from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.connection_kb import connection_kb


router = Router()


@router.callback_query(F.data == "connection")
async def show_connection(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Связь и остальное</b>\n\n"
        "🆘 <b>NB! SOS</b> — срочно сообщить о проблеме, чтобы помощь увидели подписчики и канал.\n"
        "🚗 <b>Попутчики</b> — оставить или посмотреть объявления о поездках.\n"
        "📷 <b>Фото дня</b> — посмотреть фото/видео, которые пользователи отправили в канал.\n"
        "💬 <b>Отзыв администратору</b> — написать сообщение админу.",
        reply_markup=connection_kb()
    )
    await callback.answer()
