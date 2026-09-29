"""Everything related to SQLite: creating the table, saving and reading checks."""

import sqlite3
from contextlib import closing
from pathlib import Path

# The database file is created in the project's main folder.
DB_PATH = Path(__file__).resolve().parent.parent / "uptime.db"


def get_connection():
    """Open a connection to the database. Rows can be read by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the checks table (and an index) if they don't exist yet."""
    with closing(get_connection()) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS checks (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    url              TEXT    NOT NULL,
                    is_up            INTEGER NOT NULL,
                    status_code      INTEGER,
                    response_time_ms INTEGER,
                    error            TEXT,
                    checked_at       TEXT    NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_checks_url ON checks (url)"
            )


def save_checks(results):
    """Save a list of result dictionaries (from checker.py) in one go."""
    with closing(get_connection()) as conn:
        with conn:
            conn.executemany(
                """
                INSERT INTO checks
                    (url, is_up, status_code, response_time_ms, error, checked_at)
                VALUES
                    (:url, :is_up, :status_code, :response_time_ms, :error, :checked_at)
                """,
                results,
            )


def get_history(url, limit=10):
    """Return the most recent checks for a website (newest first)."""
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM checks WHERE url = ? ORDER BY id DESC LIMIT ?",
            (url, limit),
        ).fetchall() 