from db import get_db


def get_user_by_username(username: str):
    db = get_db()
    return db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
