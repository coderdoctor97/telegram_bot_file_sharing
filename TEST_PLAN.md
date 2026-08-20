# TEST_PLAN.md — Telegram-Vault File Sharing
QA & Integration Agent — parallel phase (pre-SYNC) + integration phase (post-SYNC)
Contract authority: `master_agent.md` §4/§6/§8 · `agent_qa.md`

---

## PART A — PARALLEL TESTS (run before SYNC-1/2, no handoff artifacts needed)

All tests here use only the SAMPLE data embedded in `web/index.html` and `bot/file_map.json`.

---

### A1 — FRONTEND checklist

| # | Item | Method | Pass criteria |
|---|------|--------|---------------|
| A1-1 | Page renders from embedded JSON only | Open `web/index.html` in a browser (file:// or any static host) | Both SAMPLE entries appear as cards |
| A1-2 | Empty-state triggers on empty array | In DevTools console: `fileDatabase = []`; reload/render | "No files available right now." message visible |
| A1-3 | Deep-link format matches §4.2 | Inspect each button `href` attribute | Starts with `https://t.me/` and contains `?start=sample_pathology_01` (or matching token) |
| A1-4 | Token in link matches §4.1 regex | Run: `python -c "import re; print(bool(re.fullmatch(r'[A-Za-z0-9_-]{10,64}', 'sample_pathology_01')))"` | Prints `True` |
| A1-5 | BOT_USERNAME is placeholder before SYNC-3 | Read `web/index.html` line 202 | Value is `"CHANGE_ME_bot"` |
| A1-6 | Secrecy C2 — no CHANNEL_ID in `web/` | `grep -i "100\|channel" web/index.html` | Zero matches (except the header title string) |
| A1-7 | Secrecy C2 — no Message IDs in `web/` | `grep -E "[0-9]{3,}" web/index.html` | Zero matches for numeric IDs |
| A1-8 | Secrecy C2 — no FILE_MAP reference in `web/` | `grep -i "file_map\|FILE_MAP" web/index.html` | Zero matches |
| A1-9 | Secrecy C2 — no BOT_TOKEN in `web/` | `grep -i "bot_token" web/index.html` | Zero matches |
| A1-10 | Single file, no network requests | Open DevTools Network tab; reload | No network requests beyond the HTML file itself |
| A1-11 | EscapeHtml prevents XSS | In DevTools: add `{"title":"<script>alert(1)</script>","token":"x","type":"pdf"}` to `fileDatabase` | Title renders as literal text; no alert fires |
| A1-12 | Both type badges render correctly | Inspect cards | PDF card shows red badge/ZIP card shows blue badge |

---

### A2 — BACKEND checklist (logic review + static checks)

> These validate design contract compliance of `bot/bot.py` against the frozen spec.
> Full runtime test requires Python environment; see A2-6.

| # | Item | Method | Pass criteria |
|---|------|--------|---------------|
| A2-1 | Bot loads `BOT_TOKEN` and `CHANNEL_ID` from env | `grep -E "os\.environ|getenv" bot/bot.py` | Found; no hardcoded secrets |
| A2-2 | No secrets committed in `bot/` | `grep -iE "123456:ABC\|hard.?code" bot/*.py` | Zero matches |
| A2-3 | `/start <token>` path validates regex §4.1 | `grep "fullmatch\|re\.match" bot/bot.py` | Regex `^[A-Za-z0-9_-]{10,64}$` present |
| A2-4 | `/start` (no arg) returns welcome message | `grep -i "welcome\|no token\|start_help" bot/bot.py` | Branch exists |
| A2-5 | Unknown/invalid token returns polite error (no internal detail) | Read error-handling branch | No mention of FILE_MAP, CHANNEL_ID, or internal structure |
| A2-6 | `requirements.txt` uses `pyTelegramBotAPI` | Read `bot/requirements.txt` | Exact package name present; no extras |
| A2-7 | `bot.file_map.json` schema — all tokens match §4.1 | See `tests/validate_artifacts.py` (cross-check) | Passes validator |
| A2-8 | Bot uses polling, not webhooks (primary mode) | `grep -i "webhook\|setWebhook" bot/bot.py` | Zero matches (or in comments only) |
| A2-9 | Copy message never exposes CHANNEL_ID to user | Inspect `/start` response logic | Response contains only confirmation text; CHANNEL_ID never interpolated into a user-facing string |

---

### A3 — DATA checklist (generator script review)

| # | Item | Method | Pass criteria |
|---|------|--------|---------------|
| A3-1 | Token generator uses `secrets` module | `grep "import secrets\|from secrets" tools/token_generator.py` | Found |
| A3-2 | Token length: `secrets.token_urlsafe(9)` produces ≥10 chars | Run: `python -c "import secrets; t=secrets.token_urlsafe(9); print(len(t), t)"` | Length 10–16 (URL-safe base64 of 9 bytes = 12 chars) |
| A3-3 | Token regex §4.1 enforced | `grep "re.fullmatch\|re.compile" tools/token_generator.py` | Pattern `^[A-Za-z0-9_-]{10,64}$` present |
| A3-4 | Generator is idempotent (preserves existing tokens) | Run generator twice on same `data/master_mapping.json`; diff | Zero diff on second run |
| A3-5 | Generator emits all three handoff artifacts | Inspect script write calls | Writes `handoff/frontend_snippet.json`, `handoff/file_map.json`, `handoff/vault_constants.json` |

---

### A4 — DEVOPS checklist (static file checks)

| # | Item | Method | Pass criteria |
|---|------|--------|---------------|
| A4-1 | `.env.example` has exact env names `BOT_TOKEN`, `CHANNEL_ID` | Read `.env.example` | Both names present, exact case |
| A4-2 | `.env.example` warns against committing `.env` | `grep -i "DO NOT COMMIT\|do not commit" .env.example` | Found |
| A4-3 | `DEPLOYMENT.md` covers PythonAnywhere free path | Read `deploy/DEPLOYMENT.md` | Section titled "PythonAnywhere" or equivalent exists |
| A4-4 | `DEPLOYMENT.md` covers Render alternative | Read `deploy/DEPLOYMENT.md` | Render section exists |
| A4-5 | `DEPLOYMENT.md` covers static frontend hosting | Read `deploy/DEPLOYMENT.md` | Netlify Drop or GitHub Pages section exists |
| A4-6 | `DEPLOYMENT.md` has "add new file" SOP | Read `deploy/DEPLOYMENT.md` | Section on updating files after initial deploy |

---

## PART B — VALIDATOR SCRIPT

`tests/validate_artifacts.py` — see file.

Run: `python tests/validate_artifacts.py handoff/`
Exit 0 on pass; exit 1 on any violation with a descriptive message.

---

## PART C — INTEGRATION PHASE (after SYNC-1 and SYNC-2)

### C1 — Integration swap

Prerequisites: SYNC-1 (Data artifacts in `handoff/`) + SYNC-2 (real `bot_constants.json`).

1. Run `python tests/validate_artifacts.py handoff/`. Fix any violations before proceeding.
2. Read `handoff/frontend_snippet.json`; copy its contents to replace the SAMPLE `fileDatabase` block in `web/index.html` (lines 196–199). Preserve the comment `/* SAMPLE DATA — QA swaps real data at SYNC-3 */` above the new block (or update comment to `/* SWAPPED BY QA AT SYNC-3 */`).
3. Read `handoff/bot_constants.json`; extract `BOT_USERNAME` and replace the placeholder in `web/index.html` line 202.
4. Read `handoff/file_map.json`; write it to `bot/file_map.json` (overwrite sample).
5. Re-run `python tests/validate_artifacts.py handoff/` (post-swap sanity).
6. Re-open `web/index.html` and run A1 checklist again (live data instead of SAMPLE).

### C2 — Secrecy C2 post-swap re-check

After the swap, re-run:
```
grep -iE "channel_id|message_id|FILE_MAP|bot_token" web/index.html
```
Must return zero matches (excluding the title string `Telegram-Vault`).

### C3 — E2E with human

1. Emit 🧑 HUMAN ACTION — Live E2E (see §6 format).
2. Wait for human result.
3. Record pass/fail in `QA_REPORT.md`.

---

## PART D — COMPLETION NOTE TEMPLATE (master §8)

```
FILES CREATED: TEST_PLAN.md, tests/validate_artifacts.py, QA_REPORT.md
HANDOFF ARTIFACTS: web/index.html (swapped fileDatabase + BOT_USERNAME), bot/file_map.json (swapped)
OPEN 🧑 HUMAN ACTIONS: Live E2E confirmation
DEVIATIONS FROM CONTRACT: none
```
