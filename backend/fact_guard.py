"""Compare post claims against brief key facts."""
import re

NUMERIC_CLAIM = re.compile(
    r"\b(\d+(?:\.\d+)?%?|\$\d+(?:\.\d+)?|\d{4})\b"
)
NAME_LIKE = re.compile(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b")


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def extract_claims(text: str) -> list[str]:
    claims = []
    for m in NUMERIC_CLAIM.finditer(text):
        claims.append(m.group(1))
    for m in NAME_LIKE.finditer(text):
        claims.append(m.group(0))
    return claims


def check_facts(posts: dict[str, str], brief_facts: str, forced_unsupported: list[str] | None = None) -> dict:
    """
    Returns per-platform fact status.
    forced_unsupported: demo claims that should show as unsupported.
    """
    fact_norm = _normalize(brief_facts)
    forced = {_normalize(c) for c in (forced_unsupported or [])}
    result = {}

    for platform, text in posts.items():
        claims = extract_claims(text)
        unsupported = []
        grounded = []

        for claim in claims:
            cn = _normalize(claim)
            if cn in forced or claim in (forced_unsupported or []):
                unsupported.append(claim)
            elif cn in fact_norm or claim.lower() in fact_norm:
                grounded.append(claim)
            elif re.match(r"^\d", claim):
                unsupported.append(claim)
            elif " " in claim and claim.lower() not in fact_norm:
                unsupported.append(claim)

        # Also flag full forced strings in text
        for fu in forced_unsupported or []:
            if fu.lower() in text.lower() and fu not in unsupported:
                unsupported.append(fu)

        status = "grounded" if not unsupported else "mixed" if grounded else "unsupported"
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
            "label": "🟢 Grounded" if status == "grounded" else "🔴 Unsupported" if status == "unsupported" else "🟡 Mixed",
        }

    return result
