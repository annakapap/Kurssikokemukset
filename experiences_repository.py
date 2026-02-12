from db import get_db


def list_experiences(search_query: str):
    db = get_db()

    if search_query:
        return db.execute(
            """
            SELECT e.id, e.user_id, e.course_name, e.content,
                   e.created_at, e.updated_at, u.username
            FROM experiences e
            JOIN users u ON u.id = e.user_id
            WHERE e.course_name LIKE ? OR e.content LIKE ?
            ORDER BY e.created_at DESC
            """,
            (f"%{search_query}%", f"%{search_query}%"),
        ).fetchall()

    return db.execute(
        """
        SELECT e.id, e.user_id, e.course_name, e.content,
               e.created_at, e.updated_at, u.username
        FROM experiences e
        JOIN users u ON u.id = e.user_id
        ORDER BY e.created_at DESC
        """
    ).fetchall()
def get_experience_by_id(experience_id: int):
    db = get_db()
    return db.execute(
        """
        SELECT id, user_id, course_name, content,
               created_at, updated_at
        FROM experiences
        WHERE id = ?
        """,
        (experience_id,),
    ).fetchone()
def create_experience(user_id: int, course_name: str, content: str):
    db = get_db()
    db.execute(
        "INSERT INTO experiences (user_id, course_name, content) VALUES (?, ?, ?)",
        (user_id, course_name, content),
    )
    db.commit()


def update_experience(experience_id: int, course_name: str, content: str):
    db = get_db()
    db.execute(
        """
        UPDATE experiences
        SET course_name = ?, content = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (course_name, content, experience_id),
    )
    db.commit()


def delete_experience(experience_id: int):
    db = get_db()
    db.execute("DELETE FROM experiences WHERE id = ?", (experience_id,))
    db.commit()
