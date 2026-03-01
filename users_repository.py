"""Database operations related to users."""

from sqlite3 import IntegrityError
from db import get_db

def create_user(username: str, password_hash: str) -> None:
    """Insert a new user into the database."""
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
    """Return a user row by username."""
    db = get_db()
    return db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
