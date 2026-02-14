from db import get_db


def list_categories():
    db = get_db()
    return db.execute(
        "SELECT id, name FROM categories ORDER BY name"
    ).fetchall()


def set_experience_categories(experience_id: int, category_ids: list[int]):
    db = get_db()
    db.execute("DELETE FROM experience_categories WHERE experience_id = ?", (experience_id,))
    for cid in category_ids:
        db.execute(
            "INSERT INTO experience_categories (experience_id, category_id) VALUES (?, ?)",
            (experience_id, cid),
        )
    db.commit()


def get_experience_categories(experience_id: int):
    db = get_db()
    return db.execute(
        """
        SELECT c.id, c.name
        FROM categories c
        JOIN experience_categories ec ON ec.category_id = c.id
        WHERE ec.experience_id = ?
        ORDER BY c.name
        """,
        (experience_id,),
    ).fetchall()
