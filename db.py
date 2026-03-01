"""Application module."""

import sqlite3
from flask import g

DATABASE = "instance/app.sqlite3"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    @app.cli.command("init-db")
    def init_db_command():
        db = sqlite3.connect(DATABASE)
        with open("schema.sql", "r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.close()
        print("Initialized the database.")
