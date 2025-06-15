import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = 'rental_bot.db'


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                username TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS advertisements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                dates TEXT NOT NULL,
                price TEXT NOT NULL,
                hashtag TEXT NOT NULL,
                photo_file_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)


def add_user(user_id: int, username: str):
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )


def add_advertisement(user_id: int, title: str, description: str, dates: str, price: str, hashtag: str, photo_file_id: str):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO advertisements
            (user_id, title, description, dates, price, hashtag, photo_file_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, description, dates, price, hashtag, photo_file_id, datetime.now().isoformat())
        )


def get_user_ads(user_id: int):
    with get_db() as conn:
        ads = conn.execute(
            "SELECT * FROM advertisements WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        return ads


def get_ads_by_hashtag(hashtag: str):
    with get_db() as conn:
        ads = conn.execute(
            "SELECT * FROM advertisements WHERE hashtag = ? ORDER BY created_at DESC",
            (hashtag,)
        ).fetchall()
        return ads


def get_all_hashtags():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT hashtag FROM advertisements"
        ).fetchall()
        return [row['hashtag'] for row in rows]


def delete_ad_by_id(ad_id: int, user_id: int):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM advertisements WHERE id = ? AND user_id = ?",
            (ad_id, user_id)
        )


def get_ad_by_id(ad_id: int, user_id: int):
    with get_db() as conn:
        ad = conn.execute(
            "SELECT * FROM advertisements WHERE id = ? AND user_id = ?",
            (ad_id, user_id)
        ).fetchone()
        return ad


def get_username_by_user_id(user_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT username FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row["username"] if row else None
