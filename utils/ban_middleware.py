from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from dbase.admin_db import is_banned


class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")

        if not user:
            return await handler(event, data)

        if user.id == ADMIN_ID:
            return await handler(event, data)

        if not is_banned(user.id):
            return await handler(event, data)

        if isinstance(event, CallbackQuery):
            await event.answer(
                "Вы забанены!",
                show_alert=True
            )
            return None

        if isinstance(event, Message):
            await event.answer("Вы забанены!")
            return None

        return None
