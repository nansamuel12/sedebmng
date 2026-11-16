"""
Run:   python check.py
Tells you in simple words what is wrong (packages, .env, token, database, webhook).
It never prints your token or password.
"""
import importlib
import json
import os
import sys
import urllib.request

print("Python", sys.version.split()[0])

missing = []
for module, pip_name in [("telegram", "python-telegram-bot"), ("sqlalchemy", "SQLAlchemy"),
                         ("dotenv", "python-dotenv"), ("pg8000", "pg8000"),
                         ("starlette", "starlette"), ("uvicorn", "uvicorn")]:
    try:
        importlib.import_module(module)
        print("OK       ", pip_name)
    except Exception as e:
        print("MISSING  ", pip_name, "->", type(e).__name__)
        missing.append(pip_name)
if missing:
    print("\nFIX: run   pip install -r requirements.txt   then run this check again.")
    sys.exit(1)

from dotenv import load_dotenv  # noqa: E402

load_dotenv()
token, password = os.getenv("BOT_TOKEN"), os.getenv("BOT_PASSWORD")
print("\n.env file in this folder:", "yes" if os.path.exists(".env") else "NO  <- create it next to main.py")
print("BOT_TOKEN set:           ", "yes" if token else "NO")
print("BOT_PASSWORD set:        ", "yes" if password else "NO")
if not token or not password:
    print("\nFIX: .env must have two lines (no quotes, no spaces):\nBOT_TOKEN=...\nBOT_PASSWORD=...")
    sys.exit(1)


def telegram(method):
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/{method}", timeout=20) as r:
            return json.load(r)
    except Exception as e:
        code = getattr(e, "code", None)
        return {"ok": False, "error": f"HTTP {code}" if code else type(e).__name__}


me = telegram("getMe")
if me.get("ok"):
    print("Telegram token: OK  (bot @%s)" % me["result"]["username"])
    hook = telegram("getWebhookInfo").get("result", {})
    if hook.get("url"):
        print("Webhook: ONLINE mode is active (%s)" % hook["url"].split("/telegram")[0])
        if hook.get("last_error_message"):
            print("   Telegram says the last delivery failed:", hook["last_error_message"])
        print("   Running main.py on this PC will switch the bot back to local mode.")
    else:
        print("Webhook: none (local mode is fine)")
elif me.get("error") == "HTTP 401":
    print("Telegram token: WRONG or REVOKED -> copy the current token from @BotFather into .env")
else:
    print("Telegram: cannot connect (%s). Check your internet." % me.get("error"))

print()
try:
    import database
    database.init_db()
    print("Database: OK ->", database.engine.url.render_as_string(hide_password=True))
except Exception as e:
    print("Database: PROBLEM ->", type(e).__name__, str(e)[:200])
    sys.exit(1)
print("\nAll checks done. Start the bot with:  python main.py")
