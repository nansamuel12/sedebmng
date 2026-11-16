import hashlib
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Local: a SQLite file.  Online (Render): paste the Neon/Postgres address here.
_raw_db = os.getenv("DATABASE_URL", "sqlite:///finebot_v2.db").strip()
if _raw_db.startswith("postgres://"):
    _raw_db = "postgresql://" + _raw_db[len("postgres://"):]
if _raw_db.startswith("postgresql://"):
    _raw_db = "postgresql+psycopg://" + _raw_db[len("postgresql://"):]
DATABASE_URL = _raw_db

# Online mode (webhook). Render sets RENDER_EXTERNAL_URL and PORT by itself.
# If PUBLIC_URL is empty, the bot runs locally in polling mode (python main.py).
PORT = int(os.getenv("PORT", "10000"))
PUBLIC_URL = (os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")

CURRENCY = os.getenv("CURRENCY", "Birr")
WEEKLY_INTEREST_PERCENT = int(os.getenv("WEEKLY_INTEREST_PERCENT", "1"))

# --- Online (webhook) mode: used when the bot runs on Render. ---
# Render sets RENDER_EXTERNAL_URL and PORT by itself. On your own PC leave both empty
# and the bot uses normal polling.
WEBHOOK_URL = (os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is missing. Create a file named .env next to main.py:\n\n"
        "BOT_TOKEN=your_bot_token_here\n"
        "BOT_PASSWORD=your_password_here\n"
    )

if not BOT_PASSWORD:
    raise ValueError("BOT_PASSWORD is missing in .env (it is asked once when a user joins).")

# Secret that Telegram must send with every webhook call (derived from the token,
# so you do not have to set anything).
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or hashlib.sha256(BOT_TOKEN.encode()).hexdigest()[:48]

# Secret that Telegram sends with every webhook call, so nobody else can fake updates.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or hashlib.sha256(
    ("finebot:" + BOT_TOKEN).encode()
).hexdigest()[:40]
