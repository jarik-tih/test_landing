import requests

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def notify_new_lead(lead_data: dict) -> None:
    """Отправляет уведомление о новой заявке в Telegram."""

    text = (
        f"☕ <b>Новая заявка</b>\n\n"
        f"<b>Имя:</b> {lead_data.get('name')}\n"
        f"<b>Телефон:</b> {lead_data.get('phone')}\n"
        f"<b>Интерес:</b> {lead_data.get('interest')}\n"
        f"<b>Комментарий:</b> {lead_data.get('comment') or '—'}\n"
        f"<b>Источник:</b> {lead_data.get('source')}\n"
    )

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=5.0,
        )
        response.raise_for_status()

    except requests.RequestException as error:
        pass