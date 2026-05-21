import json
import os
import uuid
from datetime import datetime, timedelta, timezone


DB_FILE = "data/photo_posts.json"
POST_LOG_FILE = "data/photo_post_log.json"
POST_INTERVAL_HOURS = 24


def _now():
    return datetime.now(timezone.utc)


def _ensure_data_dir():
    os.makedirs("data", exist_ok=True)


def _load(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return default

    if isinstance(default, list) and isinstance(data, list):
        return data

    if isinstance(default, dict) and isinstance(data, dict):
        return data

    return default


def _save(path, data):
    _ensure_data_dir()

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def _parse_time(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return _now()


def get_photo_posts():
    return _load(DB_FILE, [])


def get_seconds_until_next_photo(user_id):
    post_log = _load(POST_LOG_FILE, {})
    last_post = post_log.get(str(user_id))

    if not last_post:
        return 0

    next_post_at = _parse_time(last_post) + timedelta(
        hours=POST_INTERVAL_HOURS
    )
    seconds_left = int((next_post_at - _now()).total_seconds())

    return max(0, seconds_left)


def add_photo_post(user, post_type, file_id=None, text=None):
    now = _now()
    post = {
        "id": uuid.uuid4().hex[:10],
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "post_type": post_type,
        "file_id": file_id,
        "text": text,
        "created_at": now.isoformat()
    }

    posts = get_photo_posts()
    posts.append(post)
    _save(DB_FILE, posts)

    if post_type == "photo":
        post_log = _load(POST_LOG_FILE, {})
        post_log[str(user.id)] = now.isoformat()
        _save(POST_LOG_FILE, post_log)

    return post
