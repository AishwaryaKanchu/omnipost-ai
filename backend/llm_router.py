"""OpenAI-compatible LLM router with cache and DEMO fallback."""
import hashlib
import json
import os
from pathlib import Path

import httpx

CACHE_DIR = Path(__file__).resolve().parent / "data" / "cache"
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"


def is_demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "0").strip() in ("1", "true", "True", "yes")


def _cache_key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _read_cache(key: str) -> dict | None:
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _write_cache(key: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    path.write_text(json.dumps(data), encoding="utf-8")


def load_golden(name: str) -> dict:
    path = GOLDEN_DIR / f"{name}.json"
    if not path.exists():
        path = GOLDEN_DIR / "default.json"
    return json.loads(path.read_text(encoding="utf-8"))


GOLDEN_ID_MAP = {
    "eco": "eco_brief",
    "voice_demo": "voice_rewrite",
    "fact_guard": "fact_guard",
}


def resolve_golden_file(golden_id: str | None) -> str | None:
    """Demo tab only: map sample brief id to golden JSON filename stem."""
    if not golden_id:
        return None
    return GOLDEN_ID_MAP.get(golden_id)


async def chat_completion(messages: list[dict], max_tokens: int = 1200) -> str | None:
    """Single LLM call. Returns None on failure."""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if is_demo_mode() or not api_key:
        return None

    base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    key = _cache_key({"url": base, **payload})
    cached = _read_cache(key)
    if cached and "content" in cached:
        return cached["content"]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            _write_cache(key, {"content": content})
            return content
    except Exception:
        return None


def provider_label() -> str:
    if is_demo_mode() or not os.getenv("LLM_API_KEY", "").strip():
        return "DEMO MODE"
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    return f"OpenAI-compatible · {model}"
