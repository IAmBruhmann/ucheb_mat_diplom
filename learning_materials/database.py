"""MySQL storage for the educational materials catalog app."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Optional

import pymysql
from pymysql.cursors import DictCursor

from learning_materials.db_config import mysql_connect_kwargs, mysql_settings
from learning_materials.schema_sql import run_schema

_REF_TABLES = frozenset({"subjects", "material_types", "authors", "providers"})


def _num(value: Any) -> float:
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


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
    def __init__(self, **connect_kwargs: Any) -> None:
        self._connect_kwargs = connect_kwargs
        self._conn: Optional[pymysql.Connection] = None

    @classmethod
    def from_env(cls) -> Database:
        return cls(**mysql_connect_kwargs())

    def connect(self) -> pymysql.Connection:
        if self._conn is None or not self._conn.open:
            self._conn = pymysql.connect(
                cursorclass=DictCursor,
                autocommit=False,
                **self._connect_kwargs,
            )
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _ensure_database(self) -> None:
        settings = mysql_settings()
        db_name = settings["database"]
        with pymysql.connect(**mysql_connect_kwargs(with_database=False)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conn.commit()

    def _run_schema(self) -> None:
        run_schema(self.connect(), recreate=False)

    def initialize(self) -> None:
        self._ensure_database()
        if self._conn is not None:
            self.close()
        self._run_schema()
        self._seed()

    def _seed(self) -> None:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM roles")
            if int(cur.fetchone()["c"]) > 0:
                return

            cur.executemany(
                "INSERT INTO roles (code, name_ru) VALUES (%s, %s)",
                [
                    ("student", "Студент"),
                    ("teacher", "Преподаватель"),
                    ("admin", "Администратор"),
                ],
            )
            cur.execute("SELECT id, code FROM roles")
            roles = {str(row["code"]): int(row["id"]) for row in cur.fetchall()}

            cur.executemany(
                "INSERT INTO users (role_id, full_name, login, password_plain) VALUES (%s, %s, %s, %s)",
                [
                    (roles["admin"], "Администратор системы", "admin", "admin"),
                    (roles["teacher"], "Иванова Мария Петровна", "teacher", "teacher"),
                    (roles["student"], "Петров Алексей Сергеевич", "student", "student"),
                ],
            )

        conn.commit()

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

        with conn.cursor() as cur:
            cur.execute("SELECT login, id FROM users")
            users = {str(row["login"]): int(row["id"]) for row in cur.fetchall()}
            cur.execute("SELECT code, id FROM materials")
            material_ids = {str(row["code"]): int(row["id"]) for row in cur.fetchall()}
            cur.executemany(
                """
                INSERT INTO requests (request_number, user_id, material_id, request_date, quantity, status)
                VALUES (%s, %s, %s, CURDATE(), %s, %s)
                """,
                [
                    (1001, users["student"], material_ids["MATH-001"], 1, "Новая"),
                    (1002, users["teacher"], material_ids["PHYS-022"], 3, "В работе"),
                ],
            )
        conn.commit()

    def _get_or_create(self, table: str, name: str) -> int:
        if table not in _REF_TABLES:
            raise ValueError(f"Unknown reference table: {table}")
        name = name.strip()
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
            row = cur.fetchone()
            if row is not None:
                return int(row["id"])
            cur.execute(f"INSERT INTO {table} (name) VALUES (%s)", (name,))
            new_id = int(cur.lastrowid)
        conn.commit()
        return new_id

    def verify_credentials(self, login: str, password: str) -> Optional[UserRecord]:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, r.code, r.name_ru, u.full_name, u.login, u.password_plain
                FROM users u
                JOIN roles r ON r.id = u.role_id
                WHERE u.login = %s
                """,
                (login,),
            )
            row = cur.fetchone()
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
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
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
            )
            rows = cur.fetchall()
        return [self._material_from_row(row) for row in rows]

    def get_material(self, material_id: int) -> Optional[MaterialRecord]:
        for material in self.list_materials():
            if material.id == material_id:
                return material
        return None

    def _material_from_row(self, row: Mapping[str, Any]) -> MaterialRecord:
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
            _num(row["price"]),
            _num(row["discount_percent"]),
        )

    def list_reference(self, table: str) -> list[tuple[int, str]]:
        if table not in _REF_TABLES:
            raise ValueError(f"Unknown reference table: {table}")
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, name FROM {table} ORDER BY name")
            rows = cur.fetchall()
        return [(int(row["id"]), str(row["name"])) for row in rows]

    def next_material_code(self) -> str:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS n FROM materials")
            row = cur.fetchone()
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
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO materials (
                    code, title, description, format_name, pages, available_count,
                    price, discount_percent, subject_id, material_type_id, author_id, provider_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            new_id = int(cur.lastrowid)
        conn.commit()
        return new_id

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
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE materials
                SET code = %s, title = %s, description = %s, format_name = %s, pages = %s,
                    available_count = %s, price = %s, discount_percent = %s,
                    subject_id = %s, material_type_id = %s, author_id = %s, provider_id = %s
                WHERE id = %s
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
        conn.commit()

    def delete_material(self, material_id: int) -> tuple[bool, str]:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM requests WHERE material_id = %s LIMIT 1", (material_id,))
            if cur.fetchone() is not None:
                return False, "Материал уже указан в заявках, поэтому удаление запрещено."
            cur.execute("DELETE FROM materials WHERE id = %s", (material_id,))
        conn.commit()
        return True, ""

    def list_requests(self, user: UserRecord) -> list[dict[str, Any]]:
        conn = self.connect()
        with conn.cursor() as cur:
            if user.role_code == "student":
                cur.execute(
                    """
                    SELECT r.*, u.full_name, m.code, m.title
                    FROM requests r
                    JOIN users u ON u.id = r.user_id
                    JOIN materials m ON m.id = r.material_id
                    WHERE r.user_id = %s
                    ORDER BY r.request_number DESC
                    """,
                    (user.id,),
                )
            else:
                cur.execute(
                    """
                    SELECT r.*, u.full_name, m.code, m.title
                    FROM requests r
                    JOIN users u ON u.id = r.user_id
                    JOIN materials m ON m.id = r.material_id
                    ORDER BY r.request_number DESC
                    """
                )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def update_request_status(self, request_id: int, status: str) -> None:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("UPDATE requests SET status = %s WHERE id = %s", (status, request_id))
        conn.commit()

    def create_request(self, user_id: int, material_id: int, quantity: int) -> None:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(request_number), 1000) + 1 AS n FROM requests")
            row = cur.fetchone()
            cur.execute(
                """
                INSERT INTO requests (request_number, user_id, material_id, request_date, quantity, status)
                VALUES (%s, %s, %s, CURDATE(), %s, 'Новая')
                """,
                (int(row["n"]), user_id, material_id, quantity),
            )
        conn.commit()

    def get_role_id(self, code: str) -> int:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM roles WHERE code = %s", (code,))
            row = cur.fetchone()
        if row is None:
            raise KeyError(code)
        return int(row["id"])

    def list_users(self) -> list[dict[str, Any]]:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.full_name, u.login, r.code AS role_code, r.name_ru AS role_name
                FROM users u
                JOIN roles r ON r.id = u.role_id
                ORDER BY u.id
                """
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]

    def insert_user(self, role_id: int, full_name: str, login: str, password_plain: str) -> None:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (role_id, full_name, login, password_plain) VALUES (%s, %s, %s, %s)",
                (role_id, full_name, login, password_plain),
            )
        conn.commit()

    def user_has_requests(self, user_id: int) -> bool:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM requests WHERE user_id = %s LIMIT 1", (user_id,))
            return cur.fetchone() is not None

    def delete_user(self, user_id: int) -> None:
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM requests WHERE user_id = %s", (user_id,))
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
