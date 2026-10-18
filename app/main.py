from http.server import ThreadingHTTPServer

from app.api.lead_handler import LeadRequestHandler
from app.config import HOST, PORT
from app.database.connection import init_db


def create_server() -> ThreadingHTTPServer:
    """Инициализирует базу и создаёт HTTP-сервер."""
    init_db()

    server = ThreadingHTTPServer(
        (HOST, PORT),
        LeadRequestHandler,
    )

    return server


def run() -> None:
    """Запускает сервер и корректно завершает его."""
    server = create_server()

    print(f"Сайт доступен по адресу: http://{HOST}:{PORT}")
    print("Для остановки нажмите Ctrl+C.")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nОстановка сервера...")

    finally:
        server.server_close()
        print("Сервер остановлен.")