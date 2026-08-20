# AGENT: DATA & VAULT (Hosting, Message IDs, Token Pipeline)
You are an AI builder: you write the generator script + runbooks yourself; the human only performs Telegram vault steps.

## READ FIRST
1. `master_agent.md` (§4.1, §4.3, §4.4, C3). 2. This file. 3. `planning_v1.md` Phase 2.

## OWNED FILES
`tools/token_generator.py`, `data/master_mapping.json`, `data/vault_runbook.md`, `handoff/frontend_snippet.json`, `handoff/file_map.json`, `handoff/vault_constants.json`.

## WORK PLAN
1. Write `data/vault_runbook.md`: create PRIVATE channel; upload ONE file per message (PDF or ZIP); get each Message ID (forward file message to @getidsbot); get CHANNEL_ID (forward any channel post to @getidsbot or add it temporarily).
2. Emit 🧑 HUMAN ACTION #1 — "Fill the vault table", template:
   ```
   CHANNEL_ID=
   | title | type(pdf/zip) | filename | message_id |
   ```
3. Write `tools/token_generator.py`: reads `data/master_mapping.json` (entries: title,type,message_id); generates a token per entry using `secrets.token_urlsafe(9)`; IDEMPOTENT (keeps existing tokens on re-run); enforces §4.1 regex + uniqueness; writes back master mapping AND emits the three handoff artifacts exactly matching §4.3/§4.4 schemas.
4. When human returns the table: populate `data/master_mapping.json`, run the script, verify artifacts, note artifact paths.
5. COMPLETION NOTE (master §8).

## HANDOFFS
Give: 3 handoff artifacts → consumed by QA (swap) and readable by BACKEND for CHANNEL_ID.
Receive: human table.

## DEFINITION OF DONE
- Every file has a unique opaque token; artifacts validate against contract schemas; runbook is followable by a non-technical human; re-running generator never rotates existing tokens.

## RULES
- Tokens are generated ONLY by your script (C-universal). Never put tokens in `web/` yourself.