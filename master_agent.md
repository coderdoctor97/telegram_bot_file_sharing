# MASTER AGENT — Universal Context & Contract
Project: "Sharing PDFs Via Standalone HTML" (Telegram-Vault File Sharing)

## 0. HOW TO USE THIS FILE
Every AI agent on this project reads THIS file FIRST (universal goals, constraints, contract),
THEN its own `agent_<role>.md` (its step-by-step plan). If a conflict appears between files,
THIS FILE WINS. Report the conflict to the human; never change this file unilaterally.

## 1. UNIVERSAL GOAL
A static, self-contained HTML page lists available files. Each "Get File" button opens a
Telegram deep link `https://t.me/<BOT_USERNAME>?start=<token>`. A Python bot intercepts
`/start`, extracts the token, looks up the Telegram Message ID, and silently delivers the
exact file from a PRIVATE Telegram channel to the user via `copy_message`.
No cloud storage. No database server. No frontend framework.

## 2. UNIVERSAL CONSTRAINTS (all agents)
- C1 Frontend = ONE static `web/index.html` (inline CSS+JS+JSON). Must work from `file://` and any static host.
- C2 SECRECY: `CHANNEL_ID`, Message IDs and `FILE_MAP` must NEVER appear in `web/` or any client-side artifact. Frontend knows ONLY `title + token + type`.
- C3 Tokens are capabilities (possession = access) ⇒ tokens MUST be opaque, random, unguessable.
- C4 Backend = one Python file + `telebot`. Secrets ONLY via env vars (`BOT_TOKEN`, `CHANNEL_ID`). Must run 24/7 on free/cheap hosting.
- C5 AGENTS ARE BUILDERS: write every file yourself. Ask the human ONLY via the 🧑 HUMAN ACTION protocol (§6). Never ask the human for anything you can compute/generate yourself.
- C6 FILE OWNERSHIP (§7) is law. Only the QA agent performs integration swaps (`handoff/` → `web/`,`bot/`).
- C7 No new libraries, frameworks, or build steps beyond §4.

## 3. AS-BUILT PIPELINE
[web/index.html + embedded JSON] --click--> [t.me deep link] --"/start <token>"-->
[bot/bot.py] --lookup file_map.json--> copy_message(from CHANNEL_ID) --> [user chat]

## 4. FROZEN CONTRACT (universal entities)
4.1 TOKEN: regex `^[A-Za-z0-9_-]{10,64}$`; generated ONLY by `tools/token_generator.py` using `secrets` (12 urlsafe chars); unique; opaque.
4.2 DEEP LINK: `https://t.me/{BOT_USERNAME}?start={token}`
4.3 FRONTEND JSON (embedded): `const fileDatabase = [ {"title": str, "token": str, "type": "pdf"|"zip"} ];`
4.4 BACKEND MAPPING: `bot/file_map.json` = `{ "<token>": <int message_id> }`
4.5 ENV NAMES (exact): `BOT_TOKEN`, `CHANNEL_ID` (format `"-1001234567890"`).
4.6 `BOT_USERNAME`: placeholder `CHANGE_ME_bot` until Backend agent finalizes it (post-BotFather) in `handoff/bot_constants.json`.
4.7 SAMPLE DATA for parallel development (use identically everywhere, marked SAMPLE):
     fileDatabase: `[ {"title":"Pathology Complete Notes (SAMPLE)","token":"sample_pathology_01","type":"pdf"}, {"title":"Surgery Question Bank (SAMPLE)","token":"sample_surgery_02","type":"zip"} ]`
     file_map: `{ "sample_pathology_01": 105, "sample_surgery_02": 106 }`
4.8 STACK: Python 3.10+, `pyTelegramBotAPI` (telebot). Frontend: vanilla HTML/CSS/JS only.
4.9 HOSTING defaults: bot → PythonAnywhere free (always-on task, polling) PRIMARY, Render (webhook) ALTERNATIVE; static page → Netlify Drop / GitHub Pages.

## 5. SYNC POINTS (order of collaboration)
- SYNC-0: this file exists. All agents may start in parallel using §4.7 sample data.
- SYNC-1: human returns the filled vault table → Data agent runs generator → writes `handoff/frontend_snippet.json`, `handoff/file_map.json`, `handoff/vault_constants.json`.
- SYNC-2: human returns BotFather values → Backend agent writes `handoff/bot_constants.json` (real `BOT_USERNAME`).
- SYNC-3: QA agent swaps handoff artifacts into `web/index.html` + `bot/file_map.json`, runs E2E, writes `QA_REPORT.md`.
- SYNC-4: DevOps deploys with real secrets; human does final live click test.

## 6.  HUMAN ACTION PROTOCOL (universal format)
When a step physically requires the human (Telegram app, BotFather, hosting console):
```
🧑 HUMAN ACTION REQUIRED — <short title>
WHY: <one line>
STEPS:
1. ...
2. ...
GIVE BACK (paste template with values):
<exact template>
⏸ I keep building everything else with placeholders; paste the values when ready.
```
Rule: NEVER block fully. Continue all other work with placeholders.

## 7. REPO LAYOUT & OWNERSHIP
```
master_agent.md, agent_*.md          (contract + roles)
web/                → FRONTEND agent only
bot/                → BACKEND agent only
tools/ data/        → DATA agent only
deploy/ .env.example DEPLOYMENT.md → DEVOPS agent only
tests/ TEST_PLAN.md QA_REPORT.md   → QA agent only
handoff/            → writers: DATA (frontend_snippet.json, file_map.json, vault_constants.json), BACKEND (bot_constants.json); reader/swapper: QA only
```

## 8. COMPLETION NOTE (every agent ends with)
FILES CREATED: … | HANDOFF ARTIFACTS: … | OPEN 🧑 HUMAN ACTIONS: … | DEVIATIONS FROM CONTRACT: none/…

## 9. PLANNING PHASES → AGENT MAP
Phase 1+3 → FRONTEND · Phase 2 → DATA · Phase 4 → BACKEND · Hosting → DEVOPS · E2E/security → QA