"""Print basic data from the local SQLite database."""

from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "data" / "learning_materials.sqlite3"


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"Database file not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        print("Tables:")
        for (table_name,) in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ):
            print(f"- {table_name}")

        print("\nUsers:")
        for row in cursor.execute(
            """
            SELECT users.id, users.full_name, users.login, users.password_plain, roles.name_ru
            FROM users
            JOIN roles ON roles.id = users.role_id
            ORDER BY users.id
            """
        ):
            user_id, full_name, login, password, role = row
            print(f"{user_id}: {full_name} | login={login} | password={password} | role={role}")


if __name__ == "__main__":
    main()
