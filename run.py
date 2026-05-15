import asyncio
import logging
import aiohttp
import os
import time

from datetime import datetime
from collections import defaultdict

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.exceptions import TelegramBadRequest
from handlers import routers
from config import API_TOKEN
from utils.logger import logger





bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_routers(*routers)

async def main():

    logger.info("Бот запущен")


    await dp.start_polling(bot)


# =========================================================
# 🚀 ENTRY POINT
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        logger.warning("Бот остановлен")

    except Exception as e:

        logger.exception(
            f"Критическая ошибка: {e}"
        )