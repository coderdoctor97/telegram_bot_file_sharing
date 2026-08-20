"""
bot/bot.py — Telegram-Vault File Sharing bot
Receives /start <token>, maps to Message ID, silently copy_message's the file
from a private vault channel to the user.
"""
import json
import logging
import os
import re
import sys

import telebot
from telebot import types
from dotenv import load_dotenv

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("vault_bot")

# ─── Token validation (master §4.1) ───────────────────────────────────────────
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{10,64}$")

# ─── Env / secrets ────────────────────────────────────────────────────────────
load_dotenv()

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "").strip()
CHANNEL_ID = os.environ.get("CHANNEL_ID", "").strip()

if not BOT_TOKEN:
    log.error("BOT_TOKEN env var is missing. Set it before running the bot.")
    sys.exit(1)
if not CHANNEL_ID:
    log.error("CHANNEL_ID env var is missing. Set it before running the bot.")
    sys.exit(1)

# ─── File map ─────────────────────────────────────────────────────────────────
FILE_MAP_PATH = os.path.join(os.path.dirname(__file__), "file_map.json")

try:
    with open(FILE_MAP_PATH, encoding="utf-8") as fh:
        FILE_MAP: dict[str, int] = json.load(fh)
    log.info("Loaded %d token(s) from %s", len(FILE_MAP), FILE_MAP_PATH)
except FileNotFoundError:
    log.error("file_map.json not found at %s. Run the data agent first.", FILE_MAP_PATH)
    sys.exit(1)
except (json.JSONDecodeError, ValueError) as exc:
    log.error("file_map.json is malformed: %s", exc)
    sys.exit(1)

# ─── Bot instance ─────────────────────────────────────────────────────────────
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ─── Handlers ─────────────────────────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def handle_start(message: types.Message) -> None:
    """Handle /start with optional token payload."""
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)

    if len(parts) == 1:
        # No token — welcome message
        bot.reply_to(
            message,
            "👋 Welcome to <b>Telegram-Vault</b>!\n\n"
            "Browse the file list and tap <b>Get File</b> to receive your document "
            "directly here.\n\n"
            "Use /help for more info.",
        )
        return

    payload = parts[1].strip()

    # Validate token format
    if not TOKEN_RE.match(payload):
        bot.reply_to(
            message,
            "⚠️ That link looks invalid. "
            "Please use a link from the official file list.",
        )
        log.warning("Malformed token from user %s: %r", message.from_user.id, payload)
        return

    # Look up message ID
    msg_id = FILE_MAP.get(payload)
    if msg_id is None:
        bot.reply_to(
            message,
            "⚠️ This file link is no longer valid or does not exist. "
            "Please check the file list and try again.",
        )
        log.info("Unknown token from user %s: %s", message.from_user.id, payload)
        return

    # Deliver the file silently via copy_message
    user_id = message.chat.id
    try:
        bot.copy_message(
            chat_id=user_id,
            from_chat_id=int(CHANNEL_ID),
            message_id=int(msg_id),
        )
        log.info(
            "Delivered file to user %s (token=%s, msg_id=%s)",
            user_id, payload, msg_id,
        )
    except telebot.apihelper.ApiException as exc:
        log.error("copy_message failed for user %s token=%s: %s", user_id, payload, exc)
        bot.reply_to(
            message,
            "⚠️ Could not deliver the file right now. "
            "Please try again later or contact support.",
        )
        return

    # Confirmation (no internal details revealed)
    bot.reply_to(
        message,
        "✅ File delivered! Check above 👆",
    )


@bot.message_handler(commands=["help"])
def handle_help(message: types.Message) -> None:
    """Show usage instructions."""
    bot.reply_to(
        message,
        "📚 <b>Telegram-Vault Help</b>\n\n"
        "1. Open the file list page.\n"
        "2. Tap <b>Get File</b> on any document.\n"
        "3. You'll receive the file right here in this chat.\n\n"
        "That's it — no accounts, no cloud storage, no hassle.",
    )


@bot.message_handler(func=lambda _: True)
def handle_unknown(message: types.Message) -> None:
    """Catch-all for unrecognised messages."""
    bot.reply_to(
        message,
        "I didn't understand that. Use /start with a file link, or /help for info.",
    )

# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("Starting Telegram-Vault bot (polling mode)…")
    try:
        bot.infinity_polling(skip_pending=True)
    except KeyboardInterrupt:
        log.info("Bot stopped by user.")
        sys.exit(0)
    except Exception as exc:
        log.critical("Bot crashed: %s", exc, exc_info=True)
        sys.exit(1)
