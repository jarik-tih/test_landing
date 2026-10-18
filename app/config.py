from pathlib import Path


# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Фронтенд и база данных
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "leads.sqlite3"

# HTTP-сервер
HOST = "127.0.0.1"
PORT = 8000

# Ограничения
MAX_REQUEST_SIZE = 20_000
DUPLICATE_WINDOW_SECONDS = 600