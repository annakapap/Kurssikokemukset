from db import get_db


def create_user(username: str, password_hash: str) -> None:
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    db.commit()


def get_user_by_username(username: str):
    db = get_db()
    return db.execute(
        "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
        (username,),
    ).fetchone()
