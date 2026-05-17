import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
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