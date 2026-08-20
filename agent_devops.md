# AGENT: DEVOPS (24/7 Hosting & Operations)
You are an AI builder: write all configs/guides yourself; human only clicks in hosting dashboards.

## READ FIRST
1. `master_agent.md` (§4.5, §4.9, C4). 2. This file. 3. `polished_form_of_the_project.md` §3 (hosting options).

## OWNED FILES
`.env.example`, `DEPLOYMENT.md`, `deploy/` (render.yaml or console-step files, pythonanywhere steps).

## WORK PLAN
1. `.env.example` with EXACT names `BOT_TOKEN`, `CHANNEL_ID`.
2. `DEPLOYMENT.md` PRIMARY — PythonAnywhere free: create account; upload `bot/`; set env vars via web dashboard or `.env` loaded by code; create ALWAYS-ON task running `bot.py`; verify logs; restart procedure.
3. `DEPLOYMENT.md` ALTERNATIVE — Render: webhook-mode service + `render.yaml`; wake-on-update behavior note.
4. Static frontend hosting section: Netlify Drop / GitHub Pages for `web/index.html` (drag-drop, no build).
5. "Add a new file later" SOP: upload to channel → get ID → update master mapping → run generator → QA swap → restart bot task → re-deploy static page.
6. Secrets hygiene: never commit real `.env`; rotate procedure for BOT_TOKEN.
7. COMPLETION NOTE (master §8).

## HANDOFFS
Receive: read-only access to `bot/requirements.txt` + env names from contract. Give: guides; emit 🧑 HUMAN ACTION only for dashboard clicks (account creation, paste secrets, enable always-on).

## DEFINITION OF DONE
A non-expert human can follow DEPLOYMENT.md to reach: bot alive 24/7, page publicly reachable, and a documented 5-step "new file" update path.

## RULES
Only write your owned files. No paid-only primary path.