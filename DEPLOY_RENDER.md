# Put FineBot online for free (Render + Neon)

Render runs the bot. Neon keeps the data (fines never get erased).
Button names on the websites can change a little. The idea stays the same.

## 0. Safety first (5 minutes)
1. Telegram -> @BotFather -> send `/revoke` -> choose your bot -> copy the NEW token.
2. Put the `.gitignore` from this folder in your project, then run:
   ```
   git rm -r --cached .
   git add .
   git commit -m "online version"
   git push
   ```
   Now `.env` and `*.db` are no longer on GitHub (they stay on your PC).

## 1. Neon (the database)
1. Open https://neon.tech and sign up. Create a project, name it `finebot`.
2. Click **Connect**. TURN OFF "Connection pooling" so the address has no `-pooler` in it.
3. Copy the connection string. It starts with `postgresql://`. Keep it private.

## 2. Keep your old data (optional)
Only if you want Hanna, Konjit and the old fines in the new database.
On your PC, in the project folder (the one with finebot_v2.db):
```
pip install -r requirements.txt
python migrate_to_postgres.py "PASTE_THE_NEON_STRING_HERE"
```
It prints how many users and entries were copied. Run it only once.
Skip this step if you want to start empty.

## 3. Render (the host)
1. Open https://render.com and sign in with GitHub.
2. **New +** -> **Web Service** -> choose your repo `MoneyMNG`.
3. Fill in:
   - Name: `finebot`
   - Language: Python 3
   - Root Directory: leave empty (if `main.py` is not on the repo's first page, write the folder name)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Instance Type: **Free**
4. **Environment Variables** -> add:
   | Name | Value |
   |---|---|
   | `BOT_TOKEN` | the NEW token from @BotFather |
   | `BOT_PASSWORD` | your password |
   | `DATABASE_URL` | the Neon string |
   | `PYTHON_VERSION` | `3.12.7` (if Render says it does not know this version, pick a 3.12 version it lists) |
5. **Advanced** -> Health Check Path: `/healthz`
6. Click **Create Web Service**. Wait until the log says `Webhook set to https://...onrender.com/telegram`.
7. Open your bot in Telegram and send `/start`.

## 4. After it is live
- The free plan sleeps after about 15 minutes without messages. The first message after that waits about a minute, then everything is normal.
- Do NOT run `python main.py` on your PC with the same token. A token can use only one way (online or local) at a time. To test on your PC, make a second bot in @BotFather.
- Update the bot: change the code, `git push`. Render redeploys by itself.
- Copy of the data: Neon keeps it. You can also open it with DB Browser using the Neon connection details, or ask me for a backup script.

## If something does not work
On your PC run `python check.py` first. It tells you in simple words what is wrong.
Render -> your service -> **Logs**. Send me the last 20 lines.
