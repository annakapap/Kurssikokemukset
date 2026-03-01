"""Application module."""

from db import get_db
from sqlite3 import IntegrityError

def create_user(username: str, password_hash: str) -> None:
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
    except IntegrityError as exc:
        raise exc


def get_user_by_username(username: str):
    db = get_db()
    return db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
