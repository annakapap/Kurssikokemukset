from db import get_db


def list_comments(experience_id: int):
    db = get_db()
    return db.execute(
        """
        SELECT c.id, c.content, c.created_at, u.username, c.user_id
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.experience_id = ?
        ORDER BY c.created_at ASC
        """,
        (experience_id,),
    ).fetchall()


def add_comment(experience_id: int, user_id: int, content: str):
    db = get_db()
    db.execute(
        "INSERT INTO comments (experience_id, user_id, content) VALUES (?, ?, ?)",
        (experience_id, user_id, content),
    )
    db.commit()

def count_comments_by_user(user_id: int) -> int:
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) AS n FROM comments WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return int(row["n"])
