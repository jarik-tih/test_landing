import json
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlsplit

from app.config import FRONTEND_DIR, MAX_REQUEST_SIZE
from app.services.lead_service import (
    DuplicateLeadError,
    submit_lead,
)
from app.validators.lead_validator import LeadValidationError


class LeadRequestHandler(SimpleHTTPRequestHandler):
    """HTTP-обработчик сайта и API заявок."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=str(FRONTEND_DIR),
            **kwargs,
        )

    def send_json(self, status_code: int, payload: dict) -> None:
        """Отправляет клиенту JSON-ответ."""
        body = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        """Обрабатывает POST-запросы."""
        path = urlsplit(self.path).path

        if path != "/api/lead":
            self.send_json(
                404,
                {"message": "Маршрут не найден."},
            )
            return

        # Проверяем размер тела запроса.
        try:
            content_length = int(
                self.headers.get("Content-Length", "")
            )
        except ValueError:
            self.send_json(
                400,
                {"message": "Некорректный размер запроса."},
            )
            return

        if content_length <= 0:
            self.send_json(
                400,
                {"message": "Пустой запрос."},
            )
            return

        if content_length > MAX_REQUEST_SIZE:
            self.send_json(
                413,
                {"message": "Слишком большой запрос."},
            )
            return

        # Разбираем JSON.
        try:
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))

        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(
                400,
                {"message": "Некорректный JSON."},
            )
            return

        if not isinstance(payload, dict):
            self.send_json(
                400,
                {"message": "Ожидался JSON-объект."},
            )
            return

        # Передаём обработку бизнес-логике.
        try:
            message = submit_lead(payload)

        except LeadValidationError as error:
            self.send_json(
                400,
                {"message": str(error)},
            )
            return

        except DuplicateLeadError as error:
            self.send_json(
                409,
                {"message": str(error)},
            )
            return

        except Exception:
            # Не отправляем клиенту детали внутренней ошибки.
            self.log_error("Ошибка при сохранении заявки")

            self.send_json(
                500,
                {
                    "message": (
                        "Не удалось сохранить заявку. "
                        "Попробуйте позже."
                    )
                },
            )
            return

        self.send_json(
            201,
            {
                "ok": True,
                "message": message,
            },
        )

    def log_message(self, format: str, *args) -> None:
        """Сохраняет стандартное логирование HTTP-сервера."""
        super().log_message(format, *args)