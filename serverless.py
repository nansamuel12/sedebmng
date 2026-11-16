"""
Vercel: no program stays running. Each Telegram message starts this app for a moment,
the update is handled inside the request, and the answer is sent before it ends.
"""
import hmac
import logging

from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from telegram import Bot, Update
from telegram.ext import Application

from config import BOT_PASSWORD, BOT_TOKEN, WEBHOOK_SECRET
from database import init_db, session_scope
from handlers.register import register_handlers
from services import store
from webhook import ALLOWED_UPDATES, HOOK_PATH, make_asgi_app

logger = logging.getLogger(__name__)
_db_ready = False


def _ensure_db():
    """Once per cold start: make sure tables exist and forget old update ids."""
    global _db_ready
    if not _db_ready:
        init_db()
        with session_scope() as db:
            store.purge_old_updates(db)
        _db_ready = True


async def process(update: Update):
    _ensure_db()
    # A fresh Application per message: nothing is kept between requests.
    application = Application.builder().token(BOT_TOKEN).updater(None).build()
    register_handlers(application)
    async with application:                 # starts and cleanly stops the Telegram connection
        # Attach the update to THIS request's started bot (the one that was used to read
        # the request was never started).
        update = Update.de_json(update.to_dict(), application.bot)
        await application.process_update(update)


async def set_webhook(request: Request):
    """Open once in your browser:  https://<project>.vercel.app/set-webhook?key=<BOT_PASSWORD>"""
    key = request.query_params.get("key", "")
    if not hmac.compare_digest(key.encode(), BOT_PASSWORD.encode()):
        return PlainTextResponse("forbidden", status_code=403)
    host = request.headers.get("x-forwarded-host") or request.url.hostname
    url = f"https://{host}{HOOK_PATH}"
    bot = Bot(BOT_TOKEN)
    async with bot:
        await bot.set_webhook(url=url, allowed_updates=ALLOWED_UPDATES, secret_token=WEBHOOK_SECRET)
    return PlainTextResponse(f"Webhook set to {url}\nNow open your bot in Telegram and send /start")


app = make_asgi_app(Bot(BOT_TOKEN), WEBHOOK_SECRET, process,
                    extra_routes=[Route("/set-webhook", set_webhook, methods=["GET"])])
