# Vault Runbook — Telegram File Vault Setup

Follow these steps to populate the vault table. No technical skill required.

---

## Prerequisites
- A Telegram account (you).
- A Telegram bot token from [@BotFather](https://t.me/BotFather) — the Backend agent handles this; you only need the channel steps here.

---

## Step 1 — Create a PRIVATE Channel

1. Open Telegram → New Channel → **Private**.
2. Name it (e.g., "My File Vault").
3. **Add your bot as an admin** to the channel: Channel settings → Administrators → Add Admin → search for your bot username → give it **Send Messages** permission only.
4. **Copy the Channel ID** (format: `-1001234567890`):
   - Forward any post from the channel to [@getidsbot](https://t.me/getidsbot).
   - It will reply with the Channel ID. Save it.

---

## Step 2 — Upload Each File

For every file you want in the vault:

1. Open the private channel.
2. Send the file (PDF or ZIP only) as a **document** (not as media gallery).
3. After uploading, **forward that message** to [@getidsbot](https://t.me/getidsbot).
4. @getidsbot replies with the **Message ID** (a positive integer, e.g., `42`). Save it.

> 💡 Tip: Upload files one at a time and record Message IDs immediately. Do not delete or re-order messages in the channel — Message IDs must stay stable.

---

## Step 3 — Fill the Vault Table

Copy the template below, replace the `...` placeholders, and paste it back to the AI:

```
CHANNEL_ID=-100xxxxxxxxxx
| title | type | filename | message_id |
| My Study Notes | pdf | notes.pdf | 42 |
| Question Bank | zip | qbank.zip | 43 |
```

- **title**: human-readable name shown on the website.
- **type**: `pdf` or `zip` (lowercase).
- **filename**: original file name (for your reference; not used in the frontend).
- **message_id**: integer from @getidsbot (Step 2).

Add one row per file. Minimum 1 row.

---

## Step 4 — Return to AI

Paste the completed table back. The AI will:
1. Write `data/master_mapping.json`.
2. Run `tools/token_generator.py`.
3. Produce the three handoff artifacts (`handoff/frontend_snippet.json`, `handoff/file_map.json`, `handoff/vault_constants.json`).
4. Hand off to QA and Backend agents.

---

## FAQ

**Q: Can I use a public channel?**  
A: No. Files must live in a private channel. The bot delivers via `copy_message`; the channel stays hidden from users.

**Q: What if @getidsbot is down?**  
A: Try [@myidbot](https://t.me/myidbot) — forward the channel message there for the same Message ID.

**Q: Do I re-upload if I change a file?**  
A: Yes — each version gets a new Message ID. Delete the old row and add a new one in the vault table.

**Q: Can I add more files later?**  
A: Yes. Re-run this runbook for new files only. The token generator is idempotent: existing tokens never change.
