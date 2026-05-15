import time

from dbase.data_dase import user_last_request




def check_spam(user_id: int, cooldown: int = 2) -> bool:
    """
    Проверка антиспама.

    Пользователь не сможет спамить кнопками.
    """

    now = time.time()

    if user_id in user_last_request:
        if now - user_last_request[user_id] < cooldown:
            return False

    user_last_request[user_id] = now
    return True
