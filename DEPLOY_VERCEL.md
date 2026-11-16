# Put FineBot online for free with Vercel (+ Neon database)

Vercel starts the bot for a moment each time Telegram sends a message, then stops it.
Neon keeps the data (fines are never erased).
Button names on the websites can change a little. The idea stays the same.

## 0. Send the NEW code to GitHub (important)
Your Vercel error came from the OLD code on GitHub. Replace the files with this folder, then:
```
git rm -r --cached .
git add .
git commit -m "vercel version"
git push
```
The `.gitignore` keeps `.env` and `*.db` off GitHub.
Also: Telegram -> @BotFather -> `/revoke` -> copy the NEW token (the old one was public).

## 1. Neon (database)
1. https://neon.tech -> create a project `finebot`.
2. Region: pick one close to Vercel's function region (Vercel's default is usually Washington D.C., so Neon "US East").
3. Click **Connect**, turn OFF "Connection pooling" (no `-pooler` in the address), copy the `postgresql://...` string.

## 2. Keep old data (optional, once)
On your PC, in the folder with `finebot_v2.db`:
```
pip install -r requirements.txt
python migrate_to_postgres.py "PASTE_THE_NEON_STRING"
```

## 3. Vercel
1. https://vercel.com -> Add New -> Project -> import `MoneyMNG`. Leave Root Directory empty.
2. Open **Environment Variables** BEFORE clicking Deploy and add:
   | Name | Value |
   |---|---|
   | `BOT_TOKEN` | the NEW token |
   | `BOT_PASSWORD` | your password |
   | `DATABASE_URL` | the Neon string |
3. Click **Deploy** (or **Redeploy** if it failed before).
4. When it says the deployment is ready, copy your address, for example `money-mng.vercel.app`.

## 4. Tell Telegram where the bot lives (once)
Open this in your browser (use your own address and password):
```
https://money-mng.vercel.app/set-webhook?key=YOUR_BOT_PASSWORD
```
You should see: `Webhook set to https://money-mng.vercel.app/telegram`.
This link contains your password: do not share it.
Now open your bot in Telegram and send `/start`.

## If it does not answer
- Vercel project -> Settings -> **Deployment Protection**: if protection is on for Production, turn it off. Otherwise Vercel blocks Telegram.
- Vercel project -> **Logs**: look for the red error and send me the last lines.
- On your PC run `python check.py`. It shows whether Telegram says the last delivery failed.
- A free function has a short time limit per message (about 10 seconds, check Vercel's current limit). The first message after a quiet time is a little slower.

## Remember
- A bot token can use only ONE way at a time. If you run `python main.py` on your PC, it switches the bot back to local mode and Vercel stops receiving messages. Open the `/set-webhook` link again to go online again. To test on your PC, make a second bot in @BotFather.
