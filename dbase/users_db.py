import json
import os

DB_FILE = "data/users.json"


def load_users():

    if not os.path.exists(DB_FILE):

        return {}

    with open(DB_FILE, "r", encoding="utf-8") as file:

        return json.load(file)


def save_users():

    with open(DB_FILE, "w", encoding="utf-8") as file:

        json.dump(
            all_users,
            file,
            ensure_ascii=False,
            indent=4
        )


all_users = load_users()


def add_user(user_id, username):

    user_id = str(user_id)

    if user_id not in all_users:

        all_users[user_id] = {
            "username": username,
            "points": 0
        }

        save_users()