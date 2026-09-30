"""Compare post claims against the full campaign brief."""
import re

NUMERIC_CLAIM = re.compile(
    r"(?:\$?\d[\d,]*(?:\.\d+)?%?|\b\d+(?:\.\d+)?(?:%|wh|lbs|hr|hours|days|teams?)\b)",
    re.IGNORECASE,
)
NAME_LIKE = re.compile(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b")


def _normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[\$,€£]", "", s)
    s = s.replace("%", " percent ")
    s = re.sub(r"[^\w\s.]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _normalize_number(s: str) -> str:
    digits = re.sub(r"[^\d.]", "", s)
    if not digits:
        return ""
    if "." in digits:
        try:
            return str(float(digits)).rstrip("0").rstrip(".")
        except ValueError:
            return digits
    return str(int(digits)) if digits.isdigit() else digits


def brief_corpus(brief_facts: str, full_brief: dict | None = None) -> str:
    parts = [brief_facts or ""]
    if full_brief:
        for key in ("brand_product", "campaign_goal", "audience", "tone", "key_facts"):
            val = full_brief.get(key) or ""
            if val and val not in parts:
                parts.append(val)
    return " ".join(parts)


def extract_claims(text: str) -> list[str]:
    claims: list[str] = []
    seen = set()
    for m in NUMERIC_CLAIM.finditer(text):
        c = m.group(0).strip()
        if c.lower() not in seen:
            seen.add(c.lower())
            claims.append(c)
    for m in NAME_LIKE.finditer(text):
        c = m.group(0).strip()
        if c.lower() not in seen:
            seen.add(c.lower())
            claims.append(c)
    return claims


def _claim_in_corpus(claim: str, corpus_raw: str, corpus_norm: str) -> bool:
    if not claim.strip():
        return True

    claim_lower = claim.lower()
    if claim_lower in corpus_raw.lower():
        return True

    claim_norm = _normalize_text(claim)
    if claim_norm and claim_norm in corpus_norm:
        return True

    num = _normalize_number(claim)
    if num:
        corpus_nums = re.findall(r"\d[\d,]*(?:\.\d+)?", corpus_raw)
        for cn in corpus_nums:
            if _normalize_number(cn) == num:
                return True
        if re.search(rf"(?<!\d){re.escape(num)}(?!\d)", _normalize_number(corpus_raw.replace(",", ""))):
            return True

    # Multi-word proper names: each significant token appears in brief
    if " " in claim:
        words = [w for w in re.findall(r"[A-Za-z]+", claim) if len(w) > 2]
        if words and all(w.lower() in corpus_norm for w in words):
            return True

    return False


def check_facts(
    posts: dict[str, str],
    brief_facts: str,
    forced_unsupported: list[str] | None = None,
    full_brief: dict | None = None,
) -> dict:
    corpus_raw = brief_corpus(brief_facts, full_brief)
    corpus_norm = _normalize_text(corpus_raw)
    forced = {_normalize_text(c) for c in (forced_unsupported or [])}
    result = {}

    for platform, text in posts.items():
        claims = extract_claims(text)
        unsupported = []
        grounded = []

        for claim in claims:
            cn = _normalize_text(claim)
            if cn in forced or claim in (forced_unsupported or []):
                unsupported.append(claim)
            elif _claim_in_corpus(claim, corpus_raw, corpus_norm):
                grounded.append(claim)
            elif re.search(r"\d", claim):
                unsupported.append(claim)
            elif " " in claim and not _claim_in_corpus(claim, corpus_raw, corpus_norm):
                unsupported.append(claim)

        for fu in forced_unsupported or []:
            if fu.lower() in text.lower() and fu not in unsupported:
                unsupported.append(fu)

        if unsupported and grounded:
            status = "mixed"
        elif unsupported:
            status = "unsupported"
        else:
            status = "grounded"

        result[platform] = {
            "status": status,
            "grounded_claims": grounded,
            "unsupported_claims": list(dict.fromkeys(unsupported)),
            "label": "🟢 Grounded"
            if status == "grounded"
            else "🔴 Unsupported"
            if status == "unsupported"
            else "🟡 Mixed",
        }

    return result
