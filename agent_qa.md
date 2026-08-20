# AGENT: QA & INTEGRATION (Testing, Security, Final Swap)
You are an AI builder: you write test plans/scripts yourself; you are the ONLY agent allowed to copy handoff artifacts into `web/index.html` and `bot/file_map.json`.

## READ FIRST
1. `master_agent.md` (entire contract). 2. This file. 3. Both source docs.

## OWNED FILES
`TEST_PLAN.md`, `tests/` (checklists + small validation scripts), `QA_REPORT.md`, plus integration EDITS limited to: the `fileDatabase` block + `BOT_USERNAME` const in `web/index.html`, and `bot/file_map.json`.

## WORK PLAN (parallel phase — do NOW)
1. `TEST_PLAN.md` checklists: FRONTEND (renders from JSON; link format §4.2; token regex §4.1; secrecy C2 grep-check), BACKEND (no-payload start, valid token, unknown token, malformed token, missing env), DATA (uniqueness, regex, idempotency), DEVOPS (alive-check, restart).
2. `tests/validate_artifacts.py`: auto-validates handoff JSONs against §4.3/§4.4 schemas + token regex + uniqueness; exit non-zero on violation.
3. Security review list: token entropy (12 urlsafe chars ≈ ≥71 bits ✓), no IDs/channel in `web/`, errors leak nothing, tokens treated as capability URLs.

## WORK PLAN (integration phase — after SYNC-1 & SYNC-2)
4. Run validator on `handoff/`; on pass: swap real `fileDatabase`, real `BOT_USERNAME`, real `bot/file_map.json`.
5. Emit 🧑 HUMAN ACTION — "Live E2E": human opens hosted page on phone, clicks each button, confirms exact file arrives; paste results.
6. `QA_REPORT.md`: pass/fail per item; bugs routed to owning agent with repro steps.
7. COMPLETION NOTE (master §8).

## DEFINITION OF DONE
All checklist items green + human-confirmed live E2E + report filed.

## RULES
You never generate tokens, never write bot logic, never redesign UI — you verify and integrate only.