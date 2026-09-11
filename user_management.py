import json
import os
from werkzeug.security import generate_password_hash, check_password_hash


USERS_FILE = "users.json"


def load_users():

    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except:
        return {}


def save_users(users):

    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


def register_user(username, email, password):

    users = load_users()

    if username in users:
        return False, "Username already exists"

    users[username] = {
        "email": email,
        "password": generate_password_hash(password),
        "skills": []
    }

    save_users(users)

    return True, "Registration successful"


def authenticate_user(username, password):

    users = load_users()

    if username not in users:
        return False

    if check_password_hash(
        users[username]["password"],
        password
    ):
        return True

    return False