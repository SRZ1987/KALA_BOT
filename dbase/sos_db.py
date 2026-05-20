import json
import os
import uuid
from datetime import datetime, timezone


DB_FILE = "data/sos_reports.json"


def _now():
    return datetime.now(timezone.utc)


def _ensure_data_dir():
    os.makedirs("data", exist_ok=True)


def _load_reports():
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


def _save_reports(reports):
    _ensure_data_dir()

    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(
            reports,
            file,
            ensure_ascii=False,
            indent=4
        )


def add_sos_report(user, problem, phone, lat=None, lon=None):
    report = {
        "id": uuid.uuid4().hex[:10],
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "problem": problem,
        "phone": phone,
        "lat": lat,
        "lon": lon,
        "created_at": _now().isoformat()
    }

    reports = _load_reports()
    reports.append(report)
    _save_reports(reports)

    return report


def get_sos_reports():
    return _load_reports()


def delete_sos_report(report_id):
    reports = _load_reports()
    new_reports = [
        report for report in reports
        if report.get("id") != report_id
    ]

    deleted = len(new_reports) != len(reports)

    if deleted:
        _save_reports(new_reports)

    return deleted
