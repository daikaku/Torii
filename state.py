import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"


def load_state() -> dict[str, Any]:
    """Load the posting state from disk."""
    if not STATE_FILE.exists():
        return {"posted_ids": []}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict[str, Any]) -> None:
    """Save the posting state to disk."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
