# bot/ — Telegram-Vault Backend

## Prerequisites

- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- The bot added as **admin** in the private vault channel
- `CHANNEL_ID` (format `-1001234567890`) for that channel

## Setup

```bash
cd bot
pip install -r requirements.txt
```

## Configure secrets

Create a `.env` file (never commit it):

```env
BOT_TOKEN=123456:ABC-DEF...
CHANNEL_ID=-1001234567890
```

## Run locally (polling — primary mode)

```bash
python bot.py
```

## Test checklist

| Scenario                         | Expected result                          |
|----------------------------------|------------------------------------------|
| `/start` (no token)              | Welcome message                          |
| `/start sample_pathology_01`     | File silently delivered + ✅ confirmation |
| `/start unknown_token_xyz`       | Polite "link invalid" error              |
| `/help`                          | Usage instructions                       |
| Any other message                | "I didn't understand that" catch-all     |

No internal details (channel ID, message IDs) are ever sent to users.

## Files

| File               | Purpose                              |
|--------------------|--------------------------------------|
| `bot.py`           | Main bot (polling, telebot only)     |
| `requirements.txt` | Python dependencies                  |
| `file_map.json`    | `{token: message_id}` — sample first |
