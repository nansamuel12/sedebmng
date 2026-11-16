import sys
import asyncio
import logging

from telegram.ext import Application

from config import BOT_TOKEN, DEBUG, PORT, WEBHOOK_URL
from database import init_db, session_scope
from handlers.register import register_handlers
from services import store

# Fix for Python 3.10+ / Windows event loop issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO,
)
logger = logging.getLogger(__name__)


async def clear_webhook(app: Application):
    """Local mode: if an online (webhook) setup was used before, switch Telegram back to polling."""
    await app.bot.delete_webhook()


def main():
    init_db()
    with session_scope() as db:
        store.purge_old_updates(db)

    if WEBHOOK_URL:
        # Online (Render): Telegram calls us, nothing has to keep asking.
        from webhook import run_webhook
        app = Application.builder().token(BOT_TOKEN).updater(None).build()
        register_handlers(app)
        logger.info("Starting in WEBHOOK mode on port %s", PORT)
        asyncio.run(run_webhook(app, WEBHOOK_URL, PORT))
    else:
        # On your own PC: the bot keeps asking Telegram.
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        app = Application.builder().token(BOT_TOKEN).post_init(clear_webhook).build()
        register_handlers(app)
        logger.info("Starting in POLLING mode (local)")
        app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()


# Vercel looks for an object called "app" in main.py (the code above only runs on your PC / Render).
from serverless import app as _serverless_app  # noqa: E402

app = _serverless_app
