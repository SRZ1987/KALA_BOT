import json
import os
import uuid
from datetime import datetime, timedelta, timezone


ADS_FILE = "data/seller_ads.json"
POST_LOG_FILE = "data/seller_post_log.json"
AD_LIFETIME_DAYS = 7
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


def cleanup_expired_seller_ads():
    ads = _load(ADS_FILE, [])
    now = _now()

    active_ads = [
        ad for ad in ads
        if _parse_time(ad.get("expires_at")) > now
    ]

    if len(active_ads) != len(ads):
        _save(ADS_FILE, active_ads)

    return active_ads


def get_all_seller_ads():
    return cleanup_expired_seller_ads()


def get_user_seller_ads(user_id):
    user_id = int(user_id)

    return [
        ad for ad in cleanup_expired_seller_ads()
        if ad.get("user_id") == user_id
    ]


def get_seconds_until_next_post(user_id):
    post_log = _load(POST_LOG_FILE, {})
    last_post = post_log.get(str(user_id))

    if not last_post:
        return 0

    next_post_at = _parse_time(last_post) + timedelta(
        hours=POST_INTERVAL_HOURS
    )
    seconds_left = int((next_post_at - _now()).total_seconds())

    return max(0, seconds_left)


def add_seller_ad(user, text):
    now = _now()
    ad = {
        "id": uuid.uuid4().hex[:10],
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "text": text,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=AD_LIFETIME_DAYS)).isoformat()
    }

    ads = cleanup_expired_seller_ads()
    ads.append(ad)
    _save(ADS_FILE, ads)

    post_log = _load(POST_LOG_FILE, {})
    post_log[str(user.id)] = now.isoformat()
    _save(POST_LOG_FILE, post_log)

    return ad


def delete_seller_ad(ad_id, user_id=None):
    ads = cleanup_expired_seller_ads()
    new_ads = []
    deleted = False

    for ad in ads:
        is_target = ad.get("id") == ad_id
        is_owner = user_id is None or ad.get("user_id") == int(user_id)

        if is_target and is_owner:
            deleted = True
            continue

        new_ads.append(ad)

    if deleted:
        _save(ADS_FILE, new_ads)

    return deleted
