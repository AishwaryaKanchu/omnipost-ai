"""Voice DNA metrics and Voice Match scoring."""
import re
from statistics import mean


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[.!?]+\s+", text.strip())
    return [p for p in parts if p.strip()]


def analyze_voice_samples(samples: list[str]) -> dict:
    if not samples:
        return {
            "avg_sentence_length": 12.0,
            "emoji_rate": 0.0,
            "hashtag_rate": 0.0,
            "exclamation_rate": 0.0,
            "question_rate": 0.0,
            "cta_style": "soft",
        }

    emoji_re = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "]+",
        flags=re.UNICODE,
    )
    lengths = []
    emoji_counts = []
    hashtag_counts = []
    excl = []
    questions = []
    cta_hits = 0

    for text in samples:
        sents = _sentences(text)
        words = text.split()
        lengths.append(len(words) / max(len(sents), 1))
        emoji_counts.append(len(emoji_re.findall(text)))
        hashtag_counts.append(len(re.findall(r"#\w+", text)))
        excl.append(text.count("!") / max(len(text), 1))
        questions.append(text.count("?") / max(len(text), 1))
        lower = text.lower()
        if any(w in lower for w in ("shop", "buy", "learn more", "sign up", "link in bio", "dm us")):
            cta_hits += 1

    avg_len = mean(lengths) if lengths else 12.0
    cta_style = "direct" if cta_hits >= len(samples) / 2 else "soft"

    return {
        "avg_sentence_length": round(avg_len, 2),
        "emoji_rate": round(sum(emoji_counts) / max(len(samples), 1), 2),
        "hashtag_rate": round(sum(hashtag_counts) / max(len(samples), 1), 2),
        "exclamation_rate": round(mean(excl) * 100, 2),
        "question_rate": round(mean(questions) * 100, 2),
        "cta_style": cta_style,
    }


def _post_features(text: str) -> dict:
    sents = _sentences(text)
    words = text.split()
    emoji_re = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "]+",
        flags=re.UNICODE,
    )
    return {
        "avg_sentence_length": len(words) / max(len(sents), 1),
        "emoji_rate": len(emoji_re.findall(text)),
        "hashtag_rate": len(re.findall(r"#\w+", text)),
        "exclamation_rate": text.count("!") / max(len(text), 1) * 100,
        "question_rate": text.count("?") / max(len(text), 1) * 100,
    }


def voice_match_score(text: str, dna: dict) -> int:
    f = _post_features(text)
    diffs = [
        abs(f["avg_sentence_length"] - dna["avg_sentence_length"]) / max(dna["avg_sentence_length"], 1),
        abs(f["emoji_rate"] - dna["emoji_rate"]) / max(dna["emoji_rate"] + 1, 1),
        abs(f["hashtag_rate"] - dna["hashtag_rate"]) / max(dna["hashtag_rate"] + 1, 1),
        abs(f["exclamation_rate"] - dna["exclamation_rate"]) / max(dna["exclamation_rate"] + 1, 1),
        abs(f["question_rate"] - dna["question_rate"]) / max(dna["question_rate"] + 1, 1),
    ]
    avg_diff = mean(diffs)
    score = int(max(0, min(100, 100 - avg_diff * 35)))
    return score


def rewrite_for_voice(text: str, dna: dict, platform: str) -> str:
    """Simple local rewrite to bump voice match (demo-friendly)."""
    lines = text.strip()
    if dna.get("emoji_rate", 0) >= 1 and "✨" not in lines and platform == "instagram":
        lines = "✨ " + lines
    if dna.get("question_rate", 0) > 2 and "?" not in lines:
        lines = lines.rstrip(".") + " — what do you think?"
    if dna.get("hashtag_rate", 0) >= 2 and platform == "instagram" and "#" not in lines:
        lines += "\n\n#BrandVoice #Community"
    if dna.get("exclamation_rate", 0) > 1 and "!" not in lines and platform != "linkedin":
        lines = lines.rstrip(".") + "!"
    return lines
