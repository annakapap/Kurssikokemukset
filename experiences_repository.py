"""Database operations related to experiences."""
from db import get_db

def list_experiences(search_query: str, limit: int, offset: int):
    """Return a paginated list of experiences with optional filtering."""
    db = get_db()

    search_query = (search_query or "").strip()

    if search_query:
        like = f"%{search_query}%"
        return db.execute(
            """
            SELECT
                e.id, e.user_id, e.course_name, e.content,
                e.created_at, e.updated_at, u.username
            FROM experiences e
            JOIN users u ON u.id = e.user_id
            WHERE e.course_name LIKE ? OR e.content LIKE ? OR u.username LIKE ?
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (like, like, like, limit, offset),
        ).fetchall()

    return db.execute(
        """
        SELECT
            e.id, e.user_id, e.course_name, e.content,
            e.created_at, e.updated_at, u.username
        FROM experiences e
        JOIN users u ON u.id = e.user_id
        ORDER BY e.created_at DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()

def count_experiences(search_query: str) -> int:
    """Return the total number of experiences matching the optional search query."""
    db = get_db()

    search_query = (search_query or "").strip()

    if search_query:
        like = f"%{search_query}%"
        row = db.execute(
            """
            SELECT COUNT(*) AS n
            FROM experiences e
            JOIN users u ON u.id = e.user_id
            WHERE e.course_name LIKE ? OR e.content LIKE ? OR u.username LIKE ?
            """,
            (like, like, like),
        ).fetchone()
        return int(row["n"])

    row = db.execute(
        """
        SELECT COUNT(*) AS n
        FROM experiences
        """,
    ).fetchone()
    return int(row["n"])

def get_experience_by_id(experience_id: int):
    """Return a single experience by its ID."""
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
    """Insert a new experience into the database."""
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO experiences (user_id, course_name, content)
        VALUES (?, ?, ?)
        """,
        (user_id, course_name, content),
    )
    db.commit()
    return cur.lastrowid



def update_experience(experience_id: int, course_name: str, content: str):
    """Update an existing experience."""
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
    """Delete an experience by ID."""
    db = get_db()
    db.execute("DELETE FROM experiences WHERE id = ?", (experience_id,))
    db.commit()

def get_experience_detail(experience_id: int):
    """Return detailed information about a specific experience."""
    db = get_db()
    return db.execute(
        """
        SELECT e.id, e.user_id, e.course_name, e.content, e.created_at, e.updated_at,
               u.username
        FROM experiences e
        JOIN users u ON u.id = e.user_id
        WHERE e.id = ?
        """,
        (experience_id,),
    ).fetchone()

def get_experience_owner(experience_id: int):
    """Return the ID and owner of a specific experience."""
    db = get_db()
    return db.execute(
        "SELECT id, user_id FROM experiences WHERE id = ?",
        (experience_id,),
    ).fetchone()

def list_experiences_by_user(user_id: int):
    """Return all experiences created by a specific user."""
    db = get_db()
    return db.execute(
        """
        SELECT id, course_name, created_at
        FROM experiences
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,),
    ).fetchall()


def count_experiences_by_user(user_id: int) -> int:
    """Return the number of experiences created by a specific user."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) AS n FROM experiences WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return int(row["n"])
