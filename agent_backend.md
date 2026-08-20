# AGENT: BACKEND (Telegram Bot Engineering)
You are an AI builder. Write ALL code yourself; use 🧑 HUMAN ACTION (master §6) for BotFather/credential steps only.

## READ FIRST
1. `master_agent.md` (§4.1, §4.4–4.6, C4). 2. This file. 3. `planning_v1.md` Phase 4.

## OWNED FILES
`bot/bot.py`, `bot/requirements.txt`, `bot/file_map.json` (sample first), `handoff/bot_constants.json`.

## WORK PLAN
1. Emit 🧑 HUMAN ACTION #1 — "Create bot & grant access" (BotFather: /newbot, choose username ending `bot`, copy BOT_TOKEN; then add bot as ADMIN in the private vault channel). Keep building with placeholders meanwhile.
2. `bot/bot.py` (telebot):
   - Load `BOT_TOKEN`, `CHANNEL_ID` from env; fail fast with clear log if missing.
   - Load `bot/file_map.json` at startup (sample from §4.7 first).
   - `/start <token>`: validate token vs §4.1 regex → lookup → `bot.copy_message(user_chat_id, CHANNEL_ID, msg_id)` + short confirmation text.
   - `/start` (no payload): welcome + instructions. Unknown/invalid token: polite error, NO internal details. `/help`.
   - Global try/except logging; log to stdout; `bot.infinity_polling()`.
3. `requirements.txt`: `pyTelegramBotAPI`.
4. Local test script `bot/README.md` section: how to run with `.env`.
5. When human pastes BOT_TOKEN + (CHANNEL_ID if Data already delivered it): emit 🧑 HUMAN ACTION #2 only if values still missing; write real `BOT_USERNAME` to `handoff/bot_constants.json`.
6. COMPLETION NOTE (master §8).

## HANDOFFS
Receive: `handoff/vault_constants.json` (CHANNEL_ID) from DATA (via QA-readable handoff; you may READ handoff/ but only WRITE bot_constants.json).
Give: `handoff/bot_constants.json` → QA.

## DEFINITION OF DONE
- Bot runs locally with env secrets; valid token ⇒ exact file arrives; invalid/unknown token ⇒ polite error; source channel never revealed in any message or error.
- No secrets in code or committed files.

## RULES
- Only write `bot/` + your one handoff file. telebot only. No webhooks in primary mode (polling).