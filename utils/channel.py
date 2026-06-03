from config import CONTENT_CHANNEL_ID


def get_content_channel_id():
    if not CONTENT_CHANNEL_ID:
        return None

    value = CONTENT_CHANNEL_ID.strip()

    if value.lstrip("-").isdigit():
        return int(value)

    return value


async def safe_delete_channel_message(bot, message_id):
    channel_id = get_content_channel_id()

    if not channel_id or not message_id:
        return False

    try:
        await bot.delete_message(channel_id, int(message_id))
    except Exception:
        return False

    return True


async def safe_unpin_channel_message(bot, message_id):
    channel_id = get_content_channel_id()

    if not channel_id or not message_id:
        return False

    try:
        await bot.unpin_chat_message(channel_id, int(message_id))
    except Exception:
        return False

    return True
