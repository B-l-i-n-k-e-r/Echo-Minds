import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_NAME = "echominds.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alias TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT UNIQUE NOT NULL,
                owner_user_id INTEGER NOT NULL,
                password_hash BLOB NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(owner_user_id) REFERENCES users(user_id)
            )
        """)
        conn.commit()

def add_user(alias, password_hash):
    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (alias, password_hash, created_at) VALUES (?, ?, ?)",
            (alias, password_hash, datetime.now())
        )
        conn.commit()

def get_user_by_alias(alias):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE alias = ?", (alias,))
        return c.fetchone()