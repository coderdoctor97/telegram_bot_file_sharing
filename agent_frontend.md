# AGENT: FRONTEND (UI + JavaScript Integration)
You are an AI builder. You write ALL code yourself. The human is only the operator for steps that require a physical account action (you have none here — expect ZERO human actions).

## READ FIRST
1. `master_agent.md` (contract §4.3, §4.7, secrecy C2). 2. This file. 3. `planning_v1.md` Phases 1 & 3 as spec.

## OWNED FILES
`web/index.html` (single file; inline CSS + JS + JSON). Nothing else.

## WORK PLAN (one step at a time, checkpoint each)
1. Skeleton: lightweight single-page HTML, no external frameworks/CDNs, mobile-friendly, minimalist readable list layout.
2. Embed `const fileDatabase = [ …SAMPLE from master §4.7… ]` with comment `/* SAMPLE DATA — QA swaps real data at SYNC-3 */`.
3. JS renderer: read the array, render one card per item: title, type badge (PDF/ZIP), "Get File" button.
4. Deep-link binding: button `href = "https://t.me/" + BOT_USERNAME + "?start=" + token`, with `const BOT_USERNAME = "CHANGE_ME_bot" // QA swaps at SYNC-3`. Open in new tab.
5. Polish: empty-state message if array empty; tiny footer; no console errors; works via `file://`.
6. Self-check against DoD, then write COMPLETION NOTE (master §8).

## HANDOFFS
Receive: none directly. Give: none directly. (QA swaps real JSON + real BOT_USERNAME into your file at SYNC-3.)

## DEFINITION OF DONE
- Page renders purely from embedded JSON; adding an entry to the array auto-renders a new button.
- Every button produces a link matching master §4.2 with a token matching §4.1 regex.
- ZERO occurrences of: channel id, message ids, FILE_MAP, bot token anywhere in `web/`.
- Single file, no network requests, works offline.

## RULES
- Never edit files outside `web/`. Never add frameworks. Never hardcode real tokens (you will never receive them).