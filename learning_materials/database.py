"""SQLite storage for the educational materials catalog app."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class UserRecord:
    id: int
    role_code: str
    role_name: str
    full_name: str
    login: str
    password_plain: str


@dataclass
class MaterialRecord:
    id: int
    code: str
    title: str
    subject: str
    material_type: str
    author: str
    provider: str
    description: str
    format_name: str
    pages: int
    available_count: int
    price: float
    discount_percent: float

    @property
    def final_price(self) -> float:
        return round(self.price * (1 - self.discount_percent / 100), 2)


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def initialize(self) -> None:
        conn = self.connect()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name_ru TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL REFERENCES roles(id),
                full_name TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                password_plain TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS material_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                format_name TEXT NOT NULL,
                pages INTEGER NOT NULL CHECK (pages >= 0),
                available_count INTEGER NOT NULL CHECK (available_count >= 0),
                price REAL NOT NULL CHECK (price >= 0),
                discount_percent REAL NOT NULL DEFAULT 0 CHECK (
                    discount_percent >= 0 AND discount_percent <= 100
                ),
                subject_id INTEGER NOT NULL REFERENCES subjects(id),
                material_type_id INTEGER NOT NULL REFERENCES material_types(id),
                author_id INTEGER NOT NULL REFERENCES authors(id),
                provider_id INTEGER NOT NULL REFERENCES providers(id)
            );

            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_number INTEGER NOT NULL UNIQUE,
                user_id INTEGER NOT NULL REFERENCES users(id),
                material_id INTEGER NOT NULL REFERENCES materials(id),
                request_date TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                status TEXT NOT NULL
            );
            """
        )
        self._seed()
        conn.commit()

    def _seed(self) -> None:
        conn = self.connect()
        if conn.execute("SELECT COUNT(*) FROM roles").fetchone()[0] > 0:
            return

        conn.executemany(
            "INSERT INTO roles (code, name_ru) VALUES (?, ?)",
            [
                ("student", "Студент"),
                ("teacher", "Преподаватель"),
                ("admin", "Администратор"),
            ],
        )
        roles = {
            row["code"]: row["id"]
            for row in conn.execute("SELECT id, code FROM roles").fetchall()
        }
        conn.executemany(
            "INSERT INTO users (role_id, full_name, login, password_plain) VALUES (?, ?, ?, ?)",
            [
                (roles["admin"], "Администратор системы", "admin", "admin"),
                (roles["teacher"], "Иванова Мария Петровна", "teacher", "teacher"),
                (roles["student"], "Петров Алексей Сергеевич", "student", "student"),
            ],
        )

        materials = [
            ("MATH-001", "Сборник задач по алгебре", "Математика", "Практикум", "Николаев А. В.", "Учебный центр", "Задачи для подготовки к контрольным работам.", "PDF", 96, 18, 250.0, 10),
            ("INFO-014", "Основы Python", "Информатика", "Электронный курс", "Смирнова Е. К.", "Digital School", "Введение в программирование с примерами и упражнениями.", "HTML", 0, 42, 0.0, 0),
            ("PHYS-022", "Лабораторные работы по физике", "Физика", "Методичка", "Кузнецов Д. Р.", "Колледж-Пресс", "Пошаговые инструкции для лабораторных занятий.", "PDF", 64, 7, 180.0, 0),
            ("RUS-007", "Русский язык: орфография", "Русский язык", "Конспект", "Орлова Н. Н.", "Учебный центр", "Краткие правила, схемы и тренировочные упражнения.", "DOCX", 38, 0, 120.0, 20),
            ("HIST-105", "История России в таблицах", "История", "Справочник", "Васильев И. О.", "Академия знаний", "Даты, события и персоналии в удобных таблицах.", "PDF", 52, 15, 160.0, 5),
            ("ENG-031", "English Grammar Starter", "Английский язык", "Рабочая тетрадь", "Brown S.", "Language Lab", "Базовая грамматика с упражнениями и ключами.", "PDF", 80, 11, 210.0, 0),
        ]
        for item in materials:
            self.insert_material_by_names(*item)

        users = {
            row["login"]: row["id"]
            for row in conn.execute("SELECT id, login FROM users").fetchall()
        }
        material_ids = {
            row["code"]: row["id"]
            for row in conn.execute("SELECT id, code FROM materials").fetchall()
        }
        conn.executemany(
            """
            INSERT INTO requests (request_number, user_id, material_id, request_date, quantity, status)
            VALUES (?, ?, ?, date('now'), ?, ?)
            """,
            [
                (1001, users["student"], material_ids["MATH-001"], 1, "Новая"),
                (1002, users["teacher"], material_ids["PHYS-022"], 3, "В работе"),
            ],
        )

    def _get_or_create(self, table: str, name: str) -> int:
        name = name.strip()
        row = self.connect().execute(f"SELECT id FROM {table} WHERE name = ?", (name,)).fetchone()
        if row is not None:
            return int(row["id"])
        cur = self.connect().execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))
        return int(cur.lastrowid)

    def verify_credentials(self, login: str, password: str) -> Optional[UserRecord]:
        row = self.connect().execute(
            """
            SELECT u.id, r.code, r.name_ru, u.full_name, u.login, u.password_plain
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.login = ?
            """,
            (login,),
        ).fetchone()
        if row is None or row["password_plain"] != password:
            return None
        return UserRecord(
            int(row["id"]),
            str(row["code"]),
            str(row["name_ru"]),
            str(row["full_name"]),
            str(row["login"]),
            str(row["password_plain"]),
        )

    def list_materials(self) -> list[MaterialRecord]:
        rows = self.connect().execute(
            """
            SELECT m.id, m.code, m.title, m.description, m.format_name, m.pages,
                   m.available_count, m.price, m.discount_percent,
                   s.name AS subject, t.name AS material_type,
                   a.name AS author, p.name AS provider
            FROM materials m
            JOIN subjects s ON s.id = m.subject_id
            JOIN material_types t ON t.id = m.material_type_id
            JOIN authors a ON a.id = m.author_id
            JOIN providers p ON p.id = m.provider_id
            ORDER BY m.id
            """
        ).fetchall()
        return [self._material_from_row(row) for row in rows]

    def get_material(self, material_id: int) -> Optional[MaterialRecord]:
        for material in self.list_materials():
            if material.id == material_id:
                return material
        return None

    def _material_from_row(self, row: sqlite3.Row) -> MaterialRecord:
        return MaterialRecord(
            int(row["id"]),
            str(row["code"]),
            str(row["title"]),
            str(row["subject"]),
            str(row["material_type"]),
            str(row["author"]),
            str(row["provider"]),
            str(row["description"]),
            str(row["format_name"]),
            int(row["pages"]),
            int(row["available_count"]),
            float(row["price"]),
            float(row["discount_percent"]),
        )

    def list_reference(self, table: str) -> list[tuple[int, str]]:
        rows = self.connect().execute(f"SELECT id, name FROM {table} ORDER BY name").fetchall()
        return [(int(row["id"]), str(row["name"])) for row in rows]

    def next_material_code(self) -> str:
        row = self.connect().execute("SELECT COALESCE(MAX(id), 0) + 1 AS n FROM materials").fetchone()
        return f"MAT-{int(row['n']):03d}"

    def insert_material_by_names(
        self,
        code: str,
        title: str,
        subject: str,
        material_type: str,
        author: str,
        provider: str,
        description: str,
        format_name: str,
        pages: int,
        available_count: int,
        price: float,
        discount_percent: float,
    ) -> int:
        subject_id = self._get_or_create("subjects", subject)
        type_id = self._get_or_create("material_types", material_type)
        author_id = self._get_or_create("authors", author)
        provider_id = self._get_or_create("providers", provider)
        return self.insert_material(
            code,
            title,
            description,
            format_name,
            pages,
            available_count,
            price,
            discount_percent,
            subject_id,
            type_id,
            author_id,
            provider_id,
        )

    def insert_material(
        self,
        code: str,
        title: str,
        description: str,
        format_name: str,
        pages: int,
        available_count: int,
        price: float,
        discount_percent: float,
        subject_id: int,
        material_type_id: int,
        author_id: int,
        provider_id: int,
    ) -> int:
        cur = self.connect().execute(
            """
            INSERT INTO materials (
                code, title, description, format_name, pages, available_count,
                price, discount_percent, subject_id, material_type_id, author_id, provider_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                code,
                title,
                description,
                format_name,
                pages,
                available_count,
                price,
                discount_percent,
                subject_id,
                material_type_id,
                author_id,
                provider_id,
            ),
        )
        self.connect().commit()
        return int(cur.lastrowid)

    def update_material(
        self,
        material_id: int,
        code: str,
        title: str,
        description: str,
        format_name: str,
        pages: int,
        available_count: int,
        price: float,
        discount_percent: float,
        subject_id: int,
        material_type_id: int,
        author_id: int,
        provider_id: int,
    ) -> None:
        self.connect().execute(
            """
            UPDATE materials
            SET code = ?, title = ?, description = ?, format_name = ?, pages = ?,
                available_count = ?, price = ?, discount_percent = ?,
                subject_id = ?, material_type_id = ?, author_id = ?, provider_id = ?
            WHERE id = ?
            """,
            (
                code,
                title,
                description,
                format_name,
                pages,
                available_count,
                price,
                discount_percent,
                subject_id,
                material_type_id,
                author_id,
                provider_id,
                material_id,
            ),
        )
        self.connect().commit()

    def delete_material(self, material_id: int) -> tuple[bool, str]:
        row = self.connect().execute(
            "SELECT 1 FROM requests WHERE material_id = ? LIMIT 1", (material_id,)
        ).fetchone()
        if row is not None:
            return False, "Материал уже указан в заявках, поэтому удаление запрещено."
        self.connect().execute("DELETE FROM materials WHERE id = ?", (material_id,))
        self.connect().commit()
        return True, ""

    def list_requests(self, user: UserRecord) -> list[dict[str, Any]]:
        if user.role_code == "student":
            rows = self.connect().execute(
                """
                SELECT r.*, u.full_name, m.code, m.title
                FROM requests r
                JOIN users u ON u.id = r.user_id
                JOIN materials m ON m.id = r.material_id
                WHERE r.user_id = ?
                ORDER BY r.request_number DESC
                """,
                (user.id,),
            ).fetchall()
        else:
            rows = self.connect().execute(
                """
                SELECT r.*, u.full_name, m.code, m.title
                FROM requests r
                JOIN users u ON u.id = r.user_id
                JOIN materials m ON m.id = r.material_id
                ORDER BY r.request_number DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def update_request_status(self, request_id: int, status: str) -> None:
        self.connect().execute("UPDATE requests SET status = ? WHERE id = ?", (status, request_id))
        self.connect().commit()

    def create_request(self, user_id: int, material_id: int, quantity: int) -> None:
        row = self.connect().execute(
            "SELECT COALESCE(MAX(request_number), 1000) + 1 AS n FROM requests"
        ).fetchone()
        self.connect().execute(
            """
            INSERT INTO requests (request_number, user_id, material_id, request_date, quantity, status)
            VALUES (?, ?, ?, date('now'), ?, 'Новая')
            """,
            (int(row["n"]), user_id, material_id, quantity),
        )
        self.connect().commit()

    def get_role_id(self, code: str) -> int:
        row = self.connect().execute("SELECT id FROM roles WHERE code = ?", (code,)).fetchone()
        if row is None:
            raise KeyError(code)
        return int(row["id"])

    def list_users(self) -> list[dict[str, Any]]:
        rows = self.connect().execute(
            """
            SELECT u.id, u.full_name, u.login, r.code AS role_code, r.name_ru AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            ORDER BY u.id
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def insert_user(self, role_id: int, full_name: str, login: str, password_plain: str) -> None:
        self.connect().execute(
            "INSERT INTO users (role_id, full_name, login, password_plain) VALUES (?, ?, ?, ?)",
            (role_id, full_name, login, password_plain),
        )
        self.connect().commit()

    def delete_user(self, user_id: int) -> None:
        self.connect().execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.connect().commit()
