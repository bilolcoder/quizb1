import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Loyihaning asosiy papkasi
BASE_DIR = Path(__file__).resolve().parent

# Windows konsolida UTF-8 ni to'g'ri ko'rsatish
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# .env faylini yuklash
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
_admin_id_raw = os.getenv("ADMIN_ID", "7548230903").strip()
try:
    ADMIN_ID = int(_admin_id_raw)
except ValueError:
    ADMIN_ID = 7548230903

# Fayl yo‘llari
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

QUESTIONS_FILE = DATA_DIR / "questions.json"
DATABASE_PATH = DATA_DIR / "quizbot.db"
LOG_FILE = BASE_DIR / "bot.log"


def setup_logging():
    """Bot uchun konsol va faylga log yozish tizimini sozlaydi."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, encoding="utf-8")
        ]
    )
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
