import json
import os
import uuid
from datetime import datetime, timedelta, timezone


DB_FILE = "data/rides.json"
AD_LIFETIME_DAYS = 7


def _now():
    return datetime.now(timezone.utc)


def _ensure_data_dir():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)


def _load_ads():
    if not os.path.exists(DB_FILE):
        return []

    with open(DB_FILE, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return []

    if isinstance(data, list):
        return data

    return []


def _save_ads(ads):
    _ensure_data_dir()

    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(
            ads,
            file,
            ensure_ascii=False,
            indent=4
        )


def _parse_time(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return _now()


def cleanup_expired_ads():
    ads = _load_ads()
    now = _now()

    active_ads = [
        ad for ad in ads
        if _parse_time(ad.get("expires_at")) > now
    ]

    if len(active_ads) != len(ads):
        _save_ads(active_ads)

    return active_ads


def add_ride_ad(user, ad_type, text):
    now = _now()
    ad = {
        "id": uuid.uuid4().hex[:10],
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "ad_type": ad_type,
        "text": text,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=AD_LIFETIME_DAYS)).isoformat()
    }

    ads = cleanup_expired_ads()
    ads.append(ad)
    _save_ads(ads)

    return ad


def get_all_ads():
    return cleanup_expired_ads()


def get_user_ads(user_id):
    ads = cleanup_expired_ads()

    return [
        ad for ad in ads
        if ad.get("user_id") == user_id
    ]


def delete_user_ad(ad_id, user_id):
    ads = cleanup_expired_ads()
    new_ads = [
        ad for ad in ads
        if not (
            ad.get("id") == ad_id
            and ad.get("user_id") == user_id
        )
    ]

    deleted = len(new_ads) != len(ads)

    if deleted:
        _save_ads(new_ads)

    return deleted
