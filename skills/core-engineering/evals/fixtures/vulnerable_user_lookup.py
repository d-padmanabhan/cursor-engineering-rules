"""Synthetic insecure fixture used only by the core-engineering eval suite."""

import sqlite3


def find_user(connection: sqlite3.Connection, email: str) -> list[tuple[object, ...]]:
    """Return users matching an email address."""

    query = f"SELECT id, email, role FROM users WHERE email = '{email}'"
    return connection.execute(query).fetchall()
