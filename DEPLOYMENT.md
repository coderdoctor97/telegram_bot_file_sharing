# DEPLOYMENT.md — Telegram-Vault File Sharing
> Full deployment guide for non-expert humans.
> Follow sections in order: ① Bot (Primary) → ② Bot (Alternative) → ③ Static Page → ④ Add a New File Later

---

## TABLE OF CONTENTS
1. [Prerequisites](#prerequisites)
2. [① PRIMARY: Deploy Bot on PythonAnywhere (Free, Polling)](#primary-deploy-bot-on-pythonanywhere)
3. [② ALTERNATIVE: Deploy Bot on Render (Free, Webhook)](#alternative-deploy-bot-on-render)
4. [③ Deploy Static Page on Netlify Drop (Zero-Config) or GitHub Pages](#deploy-static-page)
5. [④ Add a New File Later (SOP)](#add-a-new-file-later-sop)
6. [Secrets Hygiene & Rotation](#secrets-hygiene--rotation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:
- A Telegram account.
- A bot token from **@BotFather** → `/newbot` → save the token (format: `123456:ABC-DEF...`).
- A **private Telegram channel** for storing your files. Add @RawDataBot to it and copy the channel ID (format: `-1001234567890`).
- All project files committed in this repo (especially `bot/bot.py`, `bot/file_map.json`, `bot/requirements.txt`, `web/index.html`).

---

## ① PRIMARY: Deploy Bot on PythonAnywhere (Free, Polling)

PythonAnywhere free tier gives you a **always-on task** that wakes up every 5 minutes — enough for a low-traffic polling bot.

> **Why PythonAnywhere primary?** It's genuinely free (no credit card needed), supports long-running polling tasks, and is the industry-standard beginner host.

---

### Step 1 — Create a PythonAnywhere Account
1. Go to https://www.pythonanywhere.com
2. Sign up with the **"Beginner" (free)** account.
3. Verify your email.

---

### Step 2 — Upload Your Bot Code

**Option A — Git (recommended if your repo is on GitHub/GitLab):**
1. Open a **Bash console** from the Consoles tab.
2. Run:
   ```bash
   git clone https://github.com/<your_username>/telegram-vault-file-sharing.git
   cd telegram-vault-file-sharing
   ```

**Option B — Manual upload (if not on Git):**
1. Go to the **Files** tab in your PythonAnywhere dashboard.
2. Navigate to `/home/<your_username>/`.
3. Upload the `bot/` folder contents.

---

### Step 3 — Set Up Virtualenv & Install Dependencies

In a **Bash console**:
```bash
cd /home/<your_username>/telegram-vault-file-sharing
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pytelegrambotapi
```

---

### Step 4 — Create `.env` with Your Secrets

In the Bash console:
```bash
nano .env
```

Paste the following (replace placeholder values):
```
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
CHANNEL_ID=-1001234567890
BOT_USERNAME=YourBotUsername_bot
PORT=10000
```

Press `Ctrl+O` → `Enter` to save, `Ctrl+X` to exit nano.

> ⚠️ `.env` is in `.gitignore`. It will NOT be uploaded if you use git.

---

### Step 5 — (Alternative to .env) Set Env Vars in the Web Dashboard

If you prefer not to use a `.env` file, set variables here:
1. Go to **Files** tab → open the file `bot/bot.py` in the editor.
2. Confirm it loads env vars using `os.environ.get("BOT_TOKEN")` or `python-dotenv`.
3. Or use the **Web** tab → **Environ vars / Secrets** (PythonAnywhere supports this in paid tiers; free tier uses `.env`).

---

### Step 6 — Create an Always-On Task

1. Go to the **Tasks** tab in your PythonAnywhere dashboard.
2. Click **"Create a new task"**.
3. Enter this command (adjust paths):
   ```
   /home/<your_username>/.virtualenvs/telegram-vault-file-sharing/venv/bin/python3 /home/<your_username>/telegram-vault-file-sharing/bot/bot.py
   ```
   > To find your exact virtualenv path, run in Bash:
   > `echo $VIRTUAL_ENV/bin/python3` (after `source venv/bin/activate`)
4. Set the schedule to **"Every 5 minutes"** (or leave as Always-on).
5. Click **"Create"**.

> **Note:** Free tier "always-on" tasks fire every 5 minutes. If your bot uses polling (long-poll loop), it will keep running inside each task window. If the task dies, it restarts automatically at the next 5-minute mark.

---

### Step 7 — Verify It's Working

1. Open Telegram → find your bot → send `/start`.
2. Bot should respond (or send the sample file if using SAMPLE data).
3. Check logs in the **Tasks** tab → click the task → **"Log"**.
4. Any errors appear there. Common fixes in [Troubleshooting](#troubleshooting).

---

### Step 8 — Restart Procedure

Whenever you update `bot.py` or `file_map.json`:
1. Go to **Tasks** tab.
2. Find your task → click **"Cancel"** to stop it.
3. Re-upload updated files (Files tab or re-push via git).
4. Click **"Create a new task"** with the same command.
5. Verify with `/start` test.

---

## ② ALTERNATIVE: Deploy Bot on Render (Free, Webhook)

Render's free tier auto-sleeps after 15 minutes of inactivity. It uses **webhooks**, not polling. Use this if your bot is higher-traffic or you prefer webhooks.

---

### Step 1 — Push Code to GitHub

Your repo must be public (or connected to Render via GitHub).

---

### Step 2 — Create a Render Blueprint

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**.
3. Connect your GitHub repo.
4. Render will detect `deploy/render.yaml` automatically.
5. Click **"Apply"**.

---

### Step 3 — Set Environment Variables

In the Render Dashboard → your service → **Environment** tab:
| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | Your bot token from @BotFather |
| `CHANNEL_ID` | `-1001234567890` (your channel ID) |
| `BOT_USERNAME` | `YourBotUsername_bot` |
| `PORT` | `10000` |

Click **"Save Changes"** → Render will redeploy.

---

### Step 4 — Set the Telegram Webhook

After first deploy completes, open a terminal and run:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://teleral-vault-bot.onrender.com/webhook"
```
> Replace `telegram-vault-bot` with your actual Render service name.
> Replace `/webhook` with the route your `bot.py` exposes for webhook updates.

---

### Step 5 — Verify

Send `/start` to your bot in Telegram. Check Render logs via Dashboard → **Logs** tab.

---

### Render Caveats
| Issue | Mitigation |
|-------|-----------|
| Free tier sleeps after 15 min idle | Use PythonAnywhere primary, or keep-alive ping (cron job calling any URL every 10 min) |
| Ephemeral filesystem | `file_map.json` must be committed to repo; dynamic updates require redeploy |
| Webhook only (no polling) | Ensure `bot.py` uses `Updater + Dispatcher` (python-telegram-bot) or Flask/FastAPI endpoint |

---

## ③ Deploy Static Page

The `web/index.html` file is fully self-contained — no build step, no server needed.

---

### Option A — Netlify Drop (Fastest, 30 seconds)

1. Go to https://app.netlify.com/drop
2. Drag the `web/` folder from your project onto the page.
3. Netlify gives you a public URL instantly: `https://random-name.netlify.app`.
4. (Optional) In site settings → **Domain management** → add a custom domain.

> **To update later:** drag the folder again — Netlify overwrites the previous deploy.

---

### Option B — GitHub Pages

1. Push `web/index.html` to a GitHub repo.
2. Go to repo → **Settings** → **Pages**.
3. Set **Source** to: branch `main` / folder `/web` (or `/root` if `index.html` is at repo root).
4. Your page is live at: `https://<username>.github.io/<repo-name>/`.

---

## ④ Add a New File Later (SOP)

Follow these 5 steps whenever you want to add a new file to the vault:

```
STEP 1 — Upload file to your private Telegram channel
         • Send the file as a message in your private channel
         • Note the Message ID (hover over the message → "Copy link" → last number)
         • Example: https://t.me/c/-1001234567890/107  →  Message ID = 107

STEP 2 — Generate a new opaque token
         • Run: python tools/token_generator.py
         • It prints a random 12-char string, e.g. "aB3xK9pL2mQr"
         • Save this token — it becomes the user-facing link fragment.

STEP 3 — Update the master mapping (bot/file_map.json)
         • Open bot/file_map.json
         • Add entry: "aB3xK9pL2mQr": 107
         • (The Data agent's generator automates this — see tools/.)

STEP 4 — Update the frontend (web/index.html)
         • Open web/index.html
         • Find const fileDatabase = [...]
         • Add entry: {"title": "New File Title", "token": "aB3xK9pL2mQr", "type": "pdf"}
         • Re-deploy the static page (drag to Netlify Drop or push to GitHub).

STEP 5 — Restart the bot task
         • PythonAnywhere: Tasks tab → Cancel old task → Create new task with same command.
         • Render: push updated file_map.json → Render auto-redeploys.
```

> ⚠️ **Security reminder:** Never paste the Message ID or token in `web/index.html`. The frontend sees ONLY `title + token + type`. All sensitive IDs stay server-side.

---

## ⑤ Secrets Hygiene & Rotation

| Practice | How |
|----------|-----|
| Never commit `.env` | `.env` is in `.gitignore` — verify with `git check-ignore .env` |
| Rotate BOT_TOKEN | 1. @BotFather → `/token` → revoke old, get new. 2. Update `.env` and/or hosting dashboard. 3. Restart bot task. |
| Rotate CHANNEL_ID | Change the private channel → update `.env` → update `file_map.json` → restart bot |
| Audit `.gitignore` | Confirm `*.env`, `.env`, `.env.local` are listed |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Bot not responding to /start | Task not running | Check Tasks tab; re-create the task |
| `ModuleNotFoundError: No module named 'telebot'` | Deps not installed | Run `pip install pytelegrambotapi` in the venv |
| `KeyError` on token lookup | `file_map.json` missing or stale | Verify file uploaded; restart task |
| Bot works then stops | Free tier task timeout | Normal on PythonAnywhere — task auto-restarts every 5 min |
| Webhook not firing on Render | Wrong webhook URL | Check `setWebhook` call matches Render URL + route |
| 404 on static page | Wrong upload location | Netlify Drop needs `index.html` at root of dragged folder |

---

## Files in This Guide

| File | Purpose |
|------|---------|
| `.env.example` | Template for secrets — copy to `.env` and fill in |
| `deploy/pythonanywhere_console_steps.md` | Bash console commands for PythonAnywhere |
| `deploy/render.yaml` | Render Blueprint spec — upload via dashboard |

---

## Completion Checklist (Tick all)

- [ ] Bot is alive (send `/start` → get a response)
- [ ] Static page is publicly reachable (paste URL into incognito tab)
- [ ] `file_map.json` matches your channel Message IDs
- [ ] `web/index.html` `fileDatabase` matches `file_map.json` tokens
- [ ] `.env` exists but is NOT committed to git
- [ ] "Add a new file" SOP bookmarked or printed
