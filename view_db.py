"""Print basic data from the MySQL database."""

from __future__ import annotations

import pymysql
from pymysql.cursors import DictCursor

from learning_materials.db_config import mysql_connect_kwargs


def main() -> None:
    try:
        with pymysql.connect(cursorclass=DictCursor, **mysql_connect_kwargs()) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                print("Tables:")
                for row in cursor.fetchall():
                    name = next(iter(row.values()))
                    print(f"- {name}")

                print("\nUsers:")
                cursor.execute(
                    """
                    SELECT users.id, users.full_name, users.login, users.password_plain, roles.name_ru
                    FROM users
                    JOIN roles ON roles.id = users.role_id
                    ORDER BY users.id
                    """
                )
                for row in cursor.fetchall():
                    print(
                        f"{row['id']}: {row['full_name']} | login={row['login']} | "
                        f"password={row['password_plain']} | role={row['name_ru']}"
                    )
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            f"Ошибка подключения к MySQL: {exc}\n"
            "Проверьте MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE."
        ) from exc


if __name__ == "__main__":
    main()
