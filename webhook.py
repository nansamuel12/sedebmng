"""
Online mode: Telegram sends every message to  https://<your-site>/telegram
Also answers GET /healthz so the host (or an uptime monitor) can check the bot is alive.
Used by Render (webhook.run_webhook) and by Vercel (serverless.py).
"""
import hmac
import logging

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application

from config import WEBHOOK_SECRET
from database import session_scope
from services import store

logger = logging.getLogger(__name__)
HOOK_PATH = "/telegram"
ALLOWED_UPDATES = ["message", "callback_query"]


def make_asgi_app(bot, secret: str, handle_update, extra_routes=()) -> Starlette:
    """handle_update(update) is an async function that does the real work."""

    async def telegram(request: Request) -> Response:
        got = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(got.encode(), secret.encode()):
            return PlainTextResponse("forbidden", status_code=403)
        try:
            update = Update.de_json(await request.json(), bot)
        except Exception:
            return PlainTextResponse("bad request", status_code=400)
        if update is None:
            return PlainTextResponse("bad request", status_code=400)
        with session_scope() as db:
            fresh = store.claim_update(db, update.update_id)
        if not fresh:                       # Telegram retried: already handled
            return Response()
        try:
            await handle_update(update)
        except Exception:
            logger.exception("Error while handling update %s", update.update_id)
        return Response()                   # always 200, so Telegram does not resend

    async def health(request: Request) -> Response:
        return PlainTextResponse("OK")

    return Starlette(routes=[
        Route(HOOK_PATH, telegram, methods=["POST"]),
        Route("/healthz", health, methods=["GET", "HEAD"]),
        Route("/", health, methods=["GET", "HEAD"]),
        *extra_routes,
    ])


async def run_webhook(application: Application, base_url: str, port: int):
    """Render: a normal long-running web service."""
    app = make_asgi_app(application.bot, WEBHOOK_SECRET, application.update_queue.put)
    server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info"))
    async with application:
        await application.start()
        await application.bot.set_webhook(
            url=f"{base_url}{HOOK_PATH}", allowed_updates=ALLOWED_UPDATES, secret_token=WEBHOOK_SECRET,
        )
        logger.info("Webhook set to %s%s", base_url, HOOK_PATH)
        await server.serve()      # runs until the host stops the app
        await application.stop()
