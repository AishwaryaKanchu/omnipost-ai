"""Persist simple edit-learning preferences."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
PREFS_FILE = DATA_DIR / "learning_prefs.json"


def _load() -> dict:
    if PREFS_FILE.exists():
        return json.loads(PREFS_FILE.read_text(encoding="utf-8"))
    return {"edits": [], "preferences": {}}


def _save(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PREFS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_edit(platform: str, before: str, after: str) -> dict:
    data = _load()
    entry = {"platform": platform, "before_len": len(before), "after_len": len(after)}
    data["edits"].append(entry)

    prefs = data.setdefault("preferences", {})
    if len(after) < len(before) * 0.85:
        prefs["prefer_shorter"] = prefs.get("prefer_shorter", 0) + 1
    if "!" in after and "!" not in before:
        prefs["more_exclamations"] = prefs.get("more_exclamations", 0) + 1
    if "#" in after and "#" not in before:
        prefs["more_hashtags"] = prefs.get("more_hashtags", 0) + 1

    _save(data)
    return {"learned": True, "message": "Learned from your edit ✓", "preferences": prefs}


def get_preferences() -> dict:
    return _load().get("preferences", {})
