#!/usr/bin/env python3
"""Create MySQL database and tables for the educational materials app."""

from __future__ import annotations

import pymysql

from learning_materials.db_config import mysql_connect_kwargs, mysql_settings
from learning_materials.schema_sql import run_schema


def main() -> None:
    settings = mysql_settings()
    db_name = settings["database"]

    print(f"Подключение к MySQL {settings['host']}:{settings['port']}...")
    with pymysql.connect(**mysql_connect_kwargs(with_database=False)) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    print(f"База данных «{db_name}» готова.")

    with pymysql.connect(**mysql_connect_kwargs()) as conn:
        print("Пересоздание таблиц...")
        run_schema(conn, recreate=True)
    print("Таблицы созданы. Запустите приложение — загрузятся тестовые данные.")


if __name__ == "__main__":
    main()
