import json


def save_ctf_registration(user_id, data):

    with open(
        "database/ctf_users.json",
        "r",
        encoding="utf-8"
    ) as f:

        users = json.load(f)

    users[str(user_id)] = data

    with open(
        "database/ctf_users.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            users,
            f,
            ensure_ascii=False,
            indent=4
        )


def get_ctf_users():

    with open(
        "database/ctf_users.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

def is_ctf_registered(user_id):

    users = get_ctf_users()

    return str(user_id) in users

