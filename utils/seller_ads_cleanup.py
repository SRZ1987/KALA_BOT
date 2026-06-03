import asyncio

from dbase.seller_ads_db import pop_expired_seller_ads
from utils.channel import (
    safe_delete_channel_message,
    safe_unpin_channel_message,
)
from utils.logger import logger


async def cleanup_expired_seller_ads_loop(bot):
    while True:
        expired_ads = pop_expired_seller_ads()

        for ad in expired_ads:
            message_id = ad.get("channel_message_id")
            await safe_unpin_channel_message(bot, message_id)
            await safe_delete_channel_message(bot, message_id)

        if expired_ads:
            logger.info(
                f"Удалено просроченных объявлений продавцов: {len(expired_ads)}"
            )

        await asyncio.sleep(3600)
