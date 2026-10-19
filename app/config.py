from pathlib import Path
import os
from dotenv import load_dotenv

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Фронтенд и база данных
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "leads.sqlite3"

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

# Ограничения
MAX_REQUEST_SIZE = 20_000
DUPLICATE_WINDOW_SECONDS = 600

load_dotenv(BASE_DIR / ".env")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")