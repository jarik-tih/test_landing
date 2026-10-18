from app.config import DUPLICATE_WINDOW_SECONDS
from app.database.connection import get_connection
from app.models.lead import Lead


def create_lead(lead: Lead) -> bool:
    """
    Сохраняет заявку.

    Возвращает:
        True — заявка сохранена;
        False — за последние 10 минут уже была заявка
                с таким номером.
    """
    connection = get_connection()

    try:
        # Не даём двум параллельным запросам одновременно
        # пройти проверку дубликата и сохранить обе заявки.
        connection.execute("BEGIN IMMEDIATE")

        duplicate = connection.execute(
            """
            SELECT 1
            FROM leads
            WHERE phone_key = ?
              AND datetime(created_at) >=
                  datetime(
                      'now',
                      'localtime',
                      ?
                  )
            LIMIT 1
            """,
            (
                lead.phone_key,
                f"-{DUPLICATE_WINDOW_SECONDS} seconds",
            ),
        ).fetchone()

        if duplicate:
            connection.rollback()
            return False

        connection.execute(
            """
            INSERT INTO leads (
                name,
                phone,
                phone_key,
                interest,
                comment,
                ad_source,
                utm_source,
                utm_medium,
                utm_campaign,
                utm_content,
                utm_term,
                landing,
                referrer,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                datetime('now', 'localtime')
            )
            """,
            (
                lead.name,
                lead.phone,
                lead.phone_key,
                lead.interest,
                lead.comment,
                lead.ad_source,
                lead.utm_source,
                lead.utm_medium,
                lead.utm_campaign,
                lead.utm_content,
                lead.utm_term,
                lead.landing,
                lead.referrer,
            ),
        )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()