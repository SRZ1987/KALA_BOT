import time

import aiohttp

from config import OWM_API_KEY
from dbase.data_dase import weather_cache
from utils.logger import logger


async def fetch_forecast(city: str):

    # =====================================================
    # КЭШ
    # =====================================================

    if city in weather_cache:

        cached_time, cached_data = weather_cache[city]

        # кэш 10 минут
        if time.time() - cached_time < 600:
            return cached_data

    # =====================================================
    # API URL
    # =====================================================

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}"
        f"&appid={OWM_API_KEY}"
        f"&units=metric"
        f"&lang=ru"
    )

    try:

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.get(url) as response:

                if response.status != 200:

                    logger.error(
                        f"OWM ERROR {response.status}"
                    )

                    return None

                data = await response.json()

                if "list" not in data:
                    return None

                weather_cache[city] = (
                    time.time(),
                    data
                )

                return data

    except Exception as e:

        logger.exception(
            f"Ошибка загрузки погоды: {e}"
        )

        return None

