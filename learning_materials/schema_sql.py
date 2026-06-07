"""Load and execute MySQL schema statements."""

from __future__ import annotations

from pathlib import Path

import pymysql

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "database" / "schema.sql"

DROP_STATEMENTS = [
    "SET FOREIGN_KEY_CHECKS = 0",
    "DROP TABLE IF EXISTS requests",
    "DROP TABLE IF EXISTS materials",
    "DROP TABLE IF EXISTS users",
    "DROP TABLE IF EXISTS providers",
    "DROP TABLE IF EXISTS authors",
    "DROP TABLE IF EXISTS material_types",
    "DROP TABLE IF EXISTS subjects",
    "DROP TABLE IF EXISTS roles",
    "SET FOREIGN_KEY_CHECKS = 1",
]


def parse_schema_sql(path: Path = SCHEMA_PATH) -> list[str]:
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        lines.append(line)
    body = "\n".join(lines)
    return [part.strip() for part in body.split(";") if part.strip()]


def run_schema(conn: pymysql.Connection, *, recreate: bool = False) -> None:
    with conn.cursor() as cur:
        if recreate:
            for stmt in DROP_STATEMENTS:
                cur.execute(stmt)
        for stmt in parse_schema_sql():
            cur.execute(stmt)
    conn.commit()
