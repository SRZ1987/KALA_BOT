import json
import os
from datetime import datetime, timezone


SELLERS_FILE = "data/sellers.json"
BANNED_USERS_FILE = "data/banned_users.json"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _ensure_data_dir():
    os.makedirs("data", exist_ok=True)


def _load_dict(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return {}

    if isinstance(data, dict):
        return data

    return {}


def _save_dict(path, data):
    _ensure_data_dir()

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def _normalize_user_id(user_id):
    return str(int(str(user_id).strip()))


def get_sellers():
    return _load_dict(SELLERS_FILE)


def is_seller(user_id):
    return _normalize_user_id(user_id) in get_sellers()


def add_seller(user_id):
    seller_id = _normalize_user_id(user_id)
    sellers = get_sellers()
    sellers[seller_id] = {
        "user_id": int(seller_id),
        "added_at": _now()
    }
    _save_dict(SELLERS_FILE, sellers)

    return seller_id


def delete_seller(user_id):
    seller_id = _normalize_user_id(user_id)
    sellers = get_sellers()
    deleted = seller_id in sellers

    if deleted:
        del sellers[seller_id]
        _save_dict(SELLERS_FILE, sellers)

    return deleted


def get_banned_users():
    return _load_dict(BANNED_USERS_FILE)


def is_banned(user_id):
    return _normalize_user_id(user_id) in get_banned_users()


def ban_user(user_id, username=None):
    banned_id = _normalize_user_id(user_id)
    banned_users = get_banned_users()
    banned_users[banned_id] = {
        "user_id": int(banned_id),
        "username": username,
        "banned_at": _now()
    }
    _save_dict(BANNED_USERS_FILE, banned_users)

    return banned_id


def unban_user(user_id):
    banned_id = _normalize_user_id(user_id)
    banned_users = get_banned_users()
    deleted = banned_id in banned_users

    if deleted:
        del banned_users[banned_id]
        _save_dict(BANNED_USERS_FILE, banned_users)

    return deleted
