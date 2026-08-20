"""
tools/token_generator.py
========================
Idempotent token generator for the Telegram-Vault File Sharing project.

Reads    : data/master_mapping.json
Writes   : data/master_mapping.json (updated tokens, --apply)
Produces : handoff/frontend_snippet.json
           handoff/file_map.json
           handoff/vault_constants.json

Token rules (master_agent.md §4.1):
  - regex  : ^[A-Za-z0-9_-]{10,64}$
  - source : secrets.token_urlsafe(9)  → 12 url-safe chars (unique, opaque)
  - idempotent: existing tokens are never rotated

Usage:
  python tools/token_generator.py              # dry-run, prints planned changes
  python tools/token_generator.py --apply      # write master_mapping + handoff artifacts

Exit codes:
  0 — success
  1 — fatal error (IO, schema, token collision)
"""

from __future__ import annotations

import hashlib
import json
import secrets
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOKEN_MIN_LEN = 10
TOKEN_MAX_LEN = 64
TOKEN_BYTES = 9  # secrets.token_urlsafe(9) → ~12 chars, within [10, 64]

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_MAPPING_PATH = REPO_ROOT / "data" / "master_mapping.json"
HANDOFF_DIR = REPO_ROOT / "handoff"

FRONTEND_SNIPPET_PATH = HANDOFF_DIR / "frontend_snippet.json"
FILE_MAP_PATH = HANDOFF_DIR / "file_map.json"
VAULT_CONSTANTS_PATH = HANDOFF_DIR / "vault_constants.json"

TOKEN_REGEX_PATTERN = r"^[A-Za-z0-9_-]{10,64}$"

ALLOWED_TYPES = {"pdf", "zip"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_token(token: str) -> None:
    import re
    if not re.match(TOKEN_REGEX_PATTERN, token):
        raise ValueError(
            f"Token '{token}' does not match regex {TOKEN_REGEX_PATTERN}"
        )


def _generate_token(used: set[str]) -> str:
    """Generate a unique opaque token, retrying on collision."""
    for _ in range(100):
        token = secrets.token_urlsafe(TOKEN_BYTES)
        if token not in used:
            return token
    raise RuntimeError("Unable to generate unique token after 100 attempts")


def _load_master_mapping() -> dict:
    if not MASTER_MAPPING_PATH.exists():
        raise FileNotFoundError(
            f"Missing {MASTER_MAPPING_PATH}. "
            "Follow data/vault_runbook.md to create it."
        )
    with MASTER_MAPPING_PATH.open(encoding="utf-8") as fh:
        raw = json.load(fh)

    # Basic schema check
    if "files" not in raw or not isinstance(raw["files"], list):
        raise ValueError(
            f"{MASTER_MAPPING_PATH}: expected top-level 'files' list."
        )
    for i, entry in enumerate(raw["files"]):
        for key in ("title", "type", "message_id", "token"):
            if key not in entry:
                raise ValueError(
                    f"{MASTER_MAPPING_PATH} entry[{i}]: missing '{key}'."
                )
        if entry["type"] not in ALLOWED_TYPES:
            raise ValueError(
                f"{MASTER_MAPPING_PATH} entry[{i}]: type '{entry['type']}' "
                f"not in {ALLOWED_TYPES}."
            )
    return raw


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def plan_tokens(mapping: dict) -> tuple[dict, list[str]]:
    """
    Return a new mapping dict with all tokens filled in and a list of
    human-readable change lines.
    Existing tokens are preserved (idempotent).
    """
    changes: list[str] = []
    used_tokens: set[str] = set()
    new_files = []

    for entry in mapping["files"]:
        # Collect all tokens already present (pre-existing + generated earlier
        # in this loop) to enforce uniqueness.
        if "token" in entry and entry["token"]:
            used_tokens.add(entry["token"])

    for entry in mapping["files"]:
        old_token = entry.get("token", "")
        if old_token:
            # Idempotent: keep existing token
            used_tokens.add(old_token)
            continue
        new_token = _generate_token(used_tokens)
        used_tokens.add(new_token)
        entry["token"] = new_token
        changes.append(
            f"  NEW  '{entry['title']}' -> token={new_token}  "
            f"(message_id={entry['message_id']})"
        )
        new_files.append(entry)

    return mapping, changes, new_files


def build_handoffs(mapping: dict) -> tuple[dict, dict, dict]:
    """
    Build the three handoff artifacts from the completed mapping.

    Returns (frontend_snippet, file_map, vault_constants) dicts.
    """
    # --- handoff/frontend_snippet.json  (§4.3) --------------------------
    file_database = [
        {
            "title": entry["title"],
            "token": entry["token"],
            "type": entry["type"],
        }
        for entry in mapping["files"]
    ]
    frontend_snippet = {"fileDatabase": file_database}

    # --- handoff/file_map.json  (§4.4) -----------------------------------
    file_map = {entry["token"]: entry["message_id"] for entry in mapping["files"]}

    # --- handoff/vault_constants.json  (CHANNEL_ID for Backend) ----------
    vault_constants = {"CHANNEL_ID": mapping.get("CHANNEL_ID", "")}

    return frontend_snippet, file_map, vault_constants


def _print_summary(
    mapping: dict,
    changes: list[str],
    new_files: list[dict],
    apply: bool,
) -> None:
    print("=" * 60)
    print("TOKEN GENERATOR — " + ("APPLY" if apply else "DRY-RUN"))
    print("=" * 60)

    if not changes:
        print("  No new entries — all tokens already assigned.")
    else:
        print(f"  {len(changes)} new token(s) generated:")
        for line in changes:
            print(line)

    print(f"\n  Total entries in master_mapping: {len(mapping['files'])}")
    print(f"  CHANNEL_ID: {mapping.get('CHANNEL_ID', '(empty)')}")

    if apply:
        print("\n  Written:")
        print(f"    {MASTER_MAPPING_PATH}")
        print(f"    {FRONTEND_SNIPPET_PATH}")
        print(f"    {FILE_MAP_PATH}")
        print(f"    {VAULT_CONSTANTS_PATH}")
    else:
        print("\n  (dry-run — no files written. Re-run with --apply to commit.)")

    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    apply = "--apply" in sys.argv

    # 1. Load
    print(f"Loading {MASTER_MAPPING_PATH} ...")
    mapping = _load_master_mapping()

    # 2. Validate pre-existing tokens
    for entry in mapping["files"]:
        tok = entry.get("token")
        if tok:
            try:
                _validate_token(tok)
            except ValueError as exc:
                print(f"FATAL: {exc}", file=sys.stderr)
                return 1

    # 3. Plan / generate
    mapping, changes, new_files = plan_tokens(mapping)

    # 4. Validate newly generated tokens
    for entry in new_files:
        _validate_token(entry["token"])

    # 5. Uniqueness check
    all_tokens = [e["token"] for e in mapping["files"]]
    if len(all_tokens) != len(set(all_tokens)):
        dupes = [t for t in all_tokens if all_tokens.count(t) > 1]
        print(f"FATAL: duplicate tokens detected: {set(dupes)}", file=sys.stderr)
        return 1

    # 6. Build handoffs
    frontend_snippet, file_map, vault_constants = build_handoffs(mapping)

    # 7. Print summary
    _print_summary(mapping, changes, new_files, apply)

    # 8. Commit (if --apply)
    if apply:
        if not mapping.get("CHANNEL_ID"):
            print(
                "WARNING: CHANNEL_ID is empty in master_mapping. "
                "handoff/vault_constants.json will carry an empty value.",
                file=sys.stderr,
            )
        _write_json(MASTER_MAPPING_PATH, mapping)
        _write_json(FRONTEND_SNIPPET_PATH, frontend_snippet)
        _write_json(FILE_MAP_PATH, file_map)
        _write_json(VAULT_CONSTANTS_PATH, vault_constants)
        print("\n  [OK] All artifacts written.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
