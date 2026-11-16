# FineBot v2 — fines between two people (Telegram)

Simple rules, very few taps.

## How people use it

1. **First time only:** send `/start`, type the password. Never asked again.
2. Tap **🔗 Invite**, send the link to the other person. When they tap it, you are connected.
3. **➕ Give Fine** → type amount (`50` or `75.5`) → type a reason (or Skip).
   The other person gets a message with **✅ Accept / ❌ Reject** buttons.
4. **💰 I Paid** → tap *Paid all* or type the amount.
   The person who received it gets **✅ Yes, received / ❌ No** buttons.
5. **📊 Balance** shows who owes what, interest, and the date of the next +1%.
   **🔔 Pending** shows requests waiting for you (and lets you cancel your own).
   **📋 History** shows the last entries.

No IDs to copy, no commands to remember.

## Business rules

| Rule | How it works |
|---|---|
| Fine | Sender creates it. **Only the other person** can accept or reject. Counts only after accept. |
| Payment | The person who owes says "I paid X". **Only the receiver** can accept or reject. Counts only after accept. |
| Adding | Every accepted fine is added together. |
| Subtracting | Every accepted payment is subtracted. |
| Interest | After every full 7 days, **1% of the unpaid fine amount** is added. Simple interest: never 1% of interest. Rate: `WEEKLY_INTEREST_PERCENT` in `.env`. |
| Payment order | Interest first, then the fine amount; oldest fine first. |
| Paid | A fine with nothing left is **paid** and stops growing. |
| Safety | You cannot pay more than you owe; you cannot answer your own request; amounts must be a positive number (whole or decimal, max 2 decimals). |
| Both directions | A can fine B and B can fine A. Balance shows each direction and the net. |

Money is stored in integer cents, and the balance is recalculated from history every time, so it is always exact and always up to date (no daily job).

## Put it online for free
Two free ways, no PC needed: **DEPLOY_VERCEL.md** (Vercel + Neon) or **DEPLOY_RENDER.md** (Render + Neon).
On Render the bot uses a webhook; on your PC it uses polling. The mode is chosen automatically.

## Run on your PC

```bash
pip install -r requirements.txt
cp .env.example .env     # then set BOT_TOKEN and BOT_PASSWORD
python main.py
```

Or copy your existing `.env` here — same variable names.
Uses a **new** database file `finebot_v2.db`; your old `finebot.db` is untouched.

Optional `.env`: `CURRENCY=Birr`, `WEEKLY_INTEREST_PERCENT=1`, `DEBUG=false`.

## Tests

```bash
pip install pytest
python -m pytest tests
```
Covers the money rules, permissions, and a full two-person conversation.

## Structure

```
main.py              start the bot (webhook on Render, polling on your PC)
webhook.py           receives Telegram messages online, /healthz check, duplicate protection
serverless.py        the same, for Vercel (one request = one message); /set-webhook
migrate_to_postgres.py  copy finebot_v2.db into the online database
config.py / database.py / models.py
services/money.py    parse "50" / "75.5", format amounts
services/ledger.py   pure add / subtract / weekly 1% logic
services/store.py    database actions + permission checks
handlers/start.py    password (once), invite links
handlers/flow.py     menu buttons, amount / reason steps
handlers/callbacks.py  Accept / Reject / Cancel / Paid-all buttons
handlers/ui.py       keyboards and message texts
```
