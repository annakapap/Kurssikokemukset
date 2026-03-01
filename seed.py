import argparse
import os
import random
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "app.db")


def connect():
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema(conn):
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()


def seed(users: int, experiences: int, comments: int):
    conn = connect()
    ensure_schema(conn)
    cur = conn.cursor()

    categories = ["A", "B", "C", "D", "E"]
    for name in categories:
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()

    cat_rows = cur.execute("SELECT id FROM categories ORDER BY id").fetchall()
    cat_ids = [r["id"] for r in cat_rows]

    for i in range(users):
        username = f"user{i:05d}"
        pw_hash = generate_password_hash("password")
        cur.execute(
            "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
            (username, pw_hash),
        )
    conn.commit()

    user_rows = cur.execute("SELECT id FROM users ORDER BY id").fetchall()
    user_ids = [r["id"] for r in user_rows]

    now = datetime.utcnow()
    exp_ids = []

    base_tokens = ["12345", "qwerty", "abcdef", "00000", "zzzzz"]

    for i in range(experiences):
        uid = random.choice(user_ids)
        course_name = f"Course{random.randint(1, 500)}"

        token = random.choice(base_tokens)
        if random.random() < 0.3:
            content = token + "\n" + token
        else:
            content = token

        created_at = (now - timedelta(minutes=random.randint(0, 300000))).isoformat(timespec="seconds")

        cur.execute(
            """
            INSERT INTO experiences (user_id, course_name, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (uid, course_name, content, created_at),
        )
        exp_id = cur.lastrowid
        exp_ids.append(exp_id)

        chosen = random.sample(cat_ids, k=random.randint(1, min(3, len(cat_ids))))
        for cid in chosen:
            cur.execute(
                "INSERT OR IGNORE INTO experience_categories (experience_id, category_id) VALUES (?, ?)",
                (exp_id, cid),
            )

        if (i + 1) % 2000 == 0:
            conn.commit()

    conn.commit()

    for i in range(comments):
        uid = random.choice(user_ids)
        exp_id = random.choice(exp_ids)

        token = random.choice(["12345", "qwerty", "abcdef"])
        if random.random() < 0.2:
            content = token + "\n" + token
        else:
            content = token

        created_at = (now - timedelta(minutes=random.randint(0, 300000))).isoformat(timespec="seconds")

        cur.execute(
            """
            INSERT INTO comments (experience_id, user_id, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (exp_id, uid, content, created_at),
        )

        if (i + 1) % 5000 == 0:
            conn.commit()

    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=200)
    parser.add_argument("--experiences", type=int, default=20000)
    parser.add_argument("--comments", type=int, default=50000)
    args = parser.parse_args()

    seed(args.users, args.experiences, args.comments)
    print(
        f"Seeded DB at {DB_PATH} with users={args.users}, "
        f"experiences={args.experiences}, comments={args.comments}"
    )


if __name__ == "__main__":
    main()
