"""
tests/validate_artifacts.py
Telegram-Vault File Sharing - Handoff Artifact Validator
QA agent: validates S4.3/S4.4 schemas, token regex S4.1, and uniqueness.
Exit 0 on pass; exit 1 with a human-readable error list on any violation.

Usage:
    python tests/validate_artifacts.py [handoff_dir]

Defaults to "handoff/" relative to the project root
(script is at <root>/tests/).

Contract references: master_agent.md S4.1, S4.3, S4.4, C2, C3
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# Ensure UTF-8 stdout (Windows console fix)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Frozen contract constants (mirror master_agent.md S4) ──────────────────
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{10,64}$")
FRONTEND_SCHEMA_VERSION = "1.0"
# Minimum entropy: 12 url-safe chars from secrets.token_urlsafe(9) ≈ 71 bits
MIN_TOKEN_LENGTH = 10
MAX_TOKEN_LENGTH = 64
ALLOWED_TYPES = {"pdf", "zip"}

# Fields that must NEVER appear in the frontend JSON (C2 secrecy)
FORBIDDEN_FRONTEND_FIELDS = {
    "channel_id", "message_id", "channelId", "messageId",
    "FILE_MAP", "file_map", "bot_token", "BOT_TOKEN",
}

# Fields that MUST be present in the frontend JSON (S4.3)
REQUIRED_FRONTEND_FIELDS = {"title", "token", "type"}


# ── Helpers ───────────────────────────────────────────────────────────────

def die(messages):
    """Print all error messages and exit 1."""
    print("VALIDATION FAILED")
    for msg in messages:
        print(f"  FAIL {msg}")
    sys.exit(1)


def ok(msg):
    print(f"  OK  {msg}")


def load_json(path, label):
    """Load a JSON file; die with a clear message if missing or malformed."""
    if not path.exists():
        die([f"Missing file: {path}  ({label})"])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die([f"Invalid JSON in {path}: {exc}"])
    return data


def unwrap_frontend_snippet(data):
    """Accept both raw array (S4.3 strict) and wrapped {'fileDatabase':[...]} form
    used by the Data agent when emitting the handoff artifact.
    Returns the array on success, None on failure (caller appends error).
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "fileDatabase" in data and isinstance(data["fileDatabase"], list):
            return data["fileDatabase"]
    return None


# ── Validators ────────────────────────────────────────────────────────────

def validate_frontend_snippet(frontend, used_tokens, errors):
    """Validate the S4.3 frontend_snippet.json array.
    Returns the set of tokens seen (for cross-file uniqueness check).
    """
    ok(f"frontend_snippet.json: {len(frontend)} entries found")

    if not isinstance(frontend, list):
        errors.append("frontend_snippet.json: root must be a JSON array")
        return used_tokens

    for idx, entry in enumerate(frontend):
        label = f"frontend_snippet.json entry [{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: must be a JSON object")
            continue

        # Required fields
        missing = REQUIRED_FRONTEND_FIELDS - entry.keys()
        if missing:
            errors.append(f"{label}: missing required fields: {sorted(missing)}")

        # Forbidden fields (C2 secrecy)
        lower_keys = {k.lower() for k in entry.keys()}
        leaked = FORBIDDEN_FRONTEND_FIELDS & lower_keys
        if leaked:
            errors.append(
                f"{label}: SECRECY VIOLATION - forbidden field(s): {sorted(leaked)}"
            )

        # Title
        title = entry.get("title", "")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{label}: 'title' must be a non-empty string")

        # Type
        ftype = entry.get("type", "")
        if ftype not in ALLOWED_TYPES:
            errors.append(
                f"{label}: 'type' must be one of {sorted(ALLOWED_TYPES)}, got: {ftype!r}"
            )

        # Token
        token = entry.get("token", "")
        if not isinstance(token, str):
            errors.append(f"{label}: 'token' must be a string")
        else:
            if not (MIN_TOKEN_LENGTH <= len(token) <= MAX_TOKEN_LENGTH):
                errors.append(
                    f"{label}: token length {len(token)} outside "
                    f"[{MIN_TOKEN_LENGTH},{MAX_TOKEN_LENGTH}]"
                )
            if not TOKEN_RE.match(token):
                errors.append(
                    f"{label}: token {token!r} does not match regex "
                    r"^[A-Za-z0-9_-]{10,64}$"
                )
            if token in used_tokens:
                errors.append(f"{label}: DUPLICATE token - {token!r} already used")
            else:
                used_tokens.add(token)

    return used_tokens


def validate_file_map(file_map, used_tokens, errors):
    """Validate the S4.4 file_map.json mapping."""
    ok(f"file_map.json: {len(file_map)} mappings found")

    if not isinstance(file_map, dict):
        errors.append("file_map.json: root must be a JSON object")
        return

    for token, msg_id in file_map.items():
        label = f"file_map.json key {token!r}"

        # Token must match S4.1
        if not isinstance(token, str) or not TOKEN_RE.match(token):
            errors.append(f"{label}: token does not match regex ^[A-Za-z0-9_-]{{10,64}}$")

        # Message ID must be a positive integer
        if not isinstance(msg_id, int) or isinstance(msg_id, bool) or msg_id <= 0:
            errors.append(
                f"{label}: message_id must be a positive integer, got: {msg_id!r}"
            )

    # Cross-check: every token in file_map must exist in frontend_snippet
    frontend_tokens = used_tokens
    map_only = set(file_map.keys()) - frontend_tokens
    if map_only:
        errors.append(
            "file_map.json has tokens not present in frontend_snippet.json: "
            f"{sorted(map_only)}"
        )

    # Cross-check: every frontend token should ideally appear in file_map
    # (warning, not fatal - some tokens may be generated but not yet uploaded)
    front_only = frontend_tokens - set(file_map.keys())
    if front_only:
        print(
            f"  NOTE frontend_snippet.json tokens missing from file_map.json: "
            f"{sorted(front_only)}  (informational - tokens without a mapped message)"
        )


def validate_vault_constants(vault, errors):
    """Validate the vault_constants.json from Data agent."""
    ok("vault_constants.json: checking CHANNEL_ID format")

    if not isinstance(vault, dict):
        errors.append("vault_constants.json: root must be a JSON object")
        return

    channel_id = vault.get("CHANNEL_ID", "")
    if not isinstance(channel_id, str):
        errors.append("vault_constants.json: CHANNEL_ID must be a string")
        return

    # S4.5: format "-1001234567890"
    if not re.fullmatch(r"-100\d{10,}", channel_id):
        errors.append(
            f"vault_constants.json: CHANNEL_ID {channel_id!r} "
            r"must match format -100\d{10,}"
        )


def validate_bot_constants(bot, errors):
    """Validate bot_constants.json from Backend agent."""
    ok("bot_constants.json: checking BOT_USERNAME")

    if not isinstance(bot, dict):
        errors.append("bot_constants.json: root must be a JSON object")
        return

    username = bot.get("BOT_USERNAME", "")
    if not isinstance(username, str) or not username:
        errors.append("bot_constants.json: BOT_USERNAME must be a non-empty string")
        return

    if username == "CHANGE_ME_bot":
        errors.append(
            "bot_constants.json: BOT_USERNAME is still the placeholder "
            "'CHANGE_ME_bot' - Backend agent has not finalized it yet (S4.6)"
        )

    # Telegram bot usernames: 5-32 chars, alphanumeric + underscores
    if not re.fullmatch(r"[A-Za-z0-9_]{5,32}", username):
        errors.append(
            f"bot_constants.json: BOT_USERNAME {username!r} does not look like "
            "a valid Telegram bot username (5-32 alphanumeric/underscore chars)"
        )


def validate_web_secrecy(web_path, errors):
    """C2 grep-check: ensure no secrets leak into web/index.html."""
    ok("web/index.html: secrecy C2 grep-check")

    if not web_path.exists():
        errors.append(f"web/index.html not found at {web_path}")
        return

    content = web_path.read_text(encoding="utf-8")

    # Patterns that indicate a secrecy leak
    leak_patterns = [
        (r"-100\d{8,}", "CHANNEL_ID-like value"),
        (r"\b\d{5,}\b", "bare numeric ID (possible message_id)"),
        ("FILE_MAP", "FILE_MAP reference"),
        ("file_map", "file_map reference in frontend"),
        (r"\b\d+:[A-Za-z0-9_-]{20,}\b", "BOT_TOKEN pattern (<id>:<hash>)"),
    ]

    for pattern, desc in leak_patterns:
        matches = re.findall(pattern, content)
        if matches:
            errors.append(
                f"C2 SECRECY VIOLATION in web/index.html: "
                f"{desc} - found: {matches[:3]}"
            )


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    # Resolve handoff dir: argument or default to <script_dir>/../handoff
    script_dir = Path(__file__).resolve().parent
    if len(sys.argv) > 1:
        handoff_dir = Path(sys.argv[1]).resolve()
    else:
        handoff_dir = (script_dir.parent / "handoff").resolve()

    project_root = script_dir.parent
    web_path = project_root / "web" / "index.html"

    errors = []

    print("=" * 60)
    print("Telegram-Vault - Handoff Artifact Validator")
    print("  Handoff dir :", handoff_dir)
    print("  Web file    :", web_path)
    print("=" * 60)

    # ── Load handoff artifacts ───────────────────────────────────────────
    frontend_path = handoff_dir / "frontend_snippet.json"
    file_map_path = handoff_dir / "file_map.json"
    vault_path    = handoff_dir / "vault_constants.json"
    bot_path      = handoff_dir / "bot_constants.json"

    frontend_raw   = load_json(frontend_path, "frontend_snippet.json (S4.3)")
    file_map_data  = load_json(file_map_path, "file_map.json (S4.4)")
    vault_data     = load_json(vault_path,    "vault_constants.json")
    bot_data       = load_json(bot_path,      "bot_constants.json")

    frontend_data = unwrap_frontend_snippet(frontend_raw)
    if frontend_data is None:
        errors.append(
            "frontend_snippet.json: root must be a JSON array or "
            '{"fileDatabase":[...]} object'
        )
        frontend_data = []

    # ── Validate each artifact ──────────────────────────────────────────
    print()
    print("[*] Frontend snippet validation (S4.3 + C2)")
    used_tokens = set()
    used_tokens = validate_frontend_snippet(frontend_data, used_tokens, errors)

    print()
    print("[*] File map validation (S4.4 + S4.1)")
    validate_file_map(file_map_data, used_tokens, errors)

    print()
    print("[*] Vault constants validation (S4.5)")
    validate_vault_constants(vault_data, errors)

    print()
    print("[*] Bot constants validation (S4.6)")
    validate_bot_constants(bot_data, errors)

    # ── Cross-artifact token uniqueness ─────────────────────────────────
    print()
    print("[*] Cross-artifact token uniqueness (C3)")
    all_frontend_tokens = used_tokens
    all_map_tokens = set(file_map_data.keys()) if isinstance(file_map_data, dict) else set()
    dupes = all_frontend_tokens & all_map_tokens
    if dupes:
        ok(f"Tokens consistent across frontend + file_map: {len(dupes)} shared")
    else:
        errors.append(
            "No tokens shared between frontend_snippet.json and file_map.json"
        )

    # All frontend tokens must be unique (already checked per-entry, double-check)
    if len(all_frontend_tokens) != len(frontend_data):
        errors.append(
            f"Duplicate tokens detected across entries: "
            f"{len(all_frontend_tokens)} unique of {len(frontend_data)}"
        )

    # ── C2 web secrecy check ─────────────────────────────────────────────
    print()
    print("[*] Web secrecy C2 check")
    validate_web_secrecy(web_path, errors)

    # ── Report ──────────────────────────────────────────────────────────
    print()
    if errors:
        die(errors)

    print()
    print("=" * 60)
    print("ALL CHECKS PASSED - handoff artifacts are valid.")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
