"""Database connection and initialization helpers."""

import sqlite3
from flask import g

DATABASE = "instance/app.sqlite3"


def get_db():
    """Return a database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(_=None):
    """Close the database connection if it exists."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Register the init-db CLI command for database initialization."""
    @app.cli.command("init-db")

    def init_db_command():
        """Create database tables using the schema.sql file."""
        db = sqlite3.connect(DATABASE)
        with open("schema.sql", "r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.close()
        print("Initialized the database.")
