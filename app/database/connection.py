import sqlite3

from app.config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Создаёт и возвращает подключение к SQLite."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10,
    )
    connection.row_factory = sqlite3.Row

    return connection


def init_db() -> None:
    """Создаёт таблицу заявок и необходимые индексы."""
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                phone_key TEXT NOT NULL,
                interest TEXT NOT NULL,
                comment TEXT NOT NULL DEFAULT '',
                ad_source TEXT NOT NULL DEFAULT '',
                utm_source TEXT NOT NULL DEFAULT '',
                utm_medium TEXT NOT NULL DEFAULT '',
                utm_campaign TEXT NOT NULL DEFAULT '',
                utm_content TEXT NOT NULL DEFAULT '',
                utm_term TEXT NOT NULL DEFAULT '',
                landing TEXT NOT NULL DEFAULT '',
                referrer TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (
                    datetime('now', 'localtime')
                )
            )
            """
        )

        # Миграция существующей базы:
        # добавляем новые поля, если их ещё нет.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(leads)"
            ).fetchall()
        }

        migrations = {
            "phone_key": "TEXT NOT NULL DEFAULT ''",
            "comment": "TEXT NOT NULL DEFAULT ''",
            "ad_source": "TEXT NOT NULL DEFAULT ''",
            "utm_source": "TEXT NOT NULL DEFAULT ''",
            "utm_medium": "TEXT NOT NULL DEFAULT ''",
            "utm_campaign": "TEXT NOT NULL DEFAULT ''",
            "utm_content": "TEXT NOT NULL DEFAULT ''",
            "utm_term": "TEXT NOT NULL DEFAULT ''",
            "landing": "TEXT NOT NULL DEFAULT ''",
            "referrer": "TEXT NOT NULL DEFAULT ''",
            "created_at": (
                "TEXT NOT NULL DEFAULT "
                "(datetime('now', 'localtime'))"
            ),
        }

        for column_name, column_type in migrations.items():
            if column_name not in columns:
                connection.execute(
                    f"ALTER TABLE leads "
                    f"ADD COLUMN {column_name} {column_type}"
                )

        # Восстанавливаем ключи телефонов для старых записей.
        rows = connection.execute(
            """
            SELECT id, phone
            FROM leads
            WHERE phone_key = ''
            """
        ).fetchall()

        for row in rows:
            digits = "".join(
                char for char in row["phone"] if char.isdigit()
            )

            connection.execute(
                """
                UPDATE leads
                SET phone_key = ?
                WHERE id = ?
                """,
                (digits[-9:], row["id"]),
            )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_leads_phone_created
            ON leads (phone_key, created_at)
            """
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()