import json


def save_user(user_id, data):

    with open(
            "database/users.json",
            "r",
            encoding="utf-8"
    ) as f:

        users = json.load(f)

    # Если это новый пользователь — добавляем поле requests_left
    if "requests_left" not in data:
        data["requests_left"] = 20
        
    users[str(user_id)] = data

    with open(
            "database/users.json",
            "w",
            encoding="utf-8"
    ) as f:

        json.dump(
            users,
            f,
            ensure_ascii=False,
            indent=4
        )


def get_user(user_id):

    with open(
            "database/users.json",
            "r",
            encoding="utf-8"
    ) as f:

        users = json.load(f)

    return users.get(str(user_id))