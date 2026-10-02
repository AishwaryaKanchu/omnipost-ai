"""Brief → 3 posts → voice match → rewrite → fact guard."""
import json
import re

from backend.fact_guard import check_facts
from backend.llm_router import chat_completion, is_demo_mode, load_golden, resolve_golden_file
from backend.voice import analyze_voice_samples, rewrite_for_voice, voice_match_score

DEFAULT_VOICE_SAMPLES = [
    "We keep it real — short sentences, warm tone. Questions welcome!",
    "Love sharing wins with our community ✨ Always honest, never hype.",
    "Here's what we learned this week (and what we'd do differently).",
    "Your feedback shapes every release. Tell us what you need?",
]

SAMPLE_BRIEFS = [
    {
        "id": "eco",
        "label": "EcoFlow Solar Charger",
        "brand_product": "EcoFlow River 2 Pro",
        "campaign_goal": "Launch awareness for portable solar charging",
        "audience": "Campers and remote workers aged 25–40",
        "key_facts": "512Wh battery. Charges via solar in 3 hours. Weighs 7.8 lbs. Price $399.",
        "tone": "Optimistic, practical, outdoorsy",
    },
    {
        "id": "voice_demo",
        "label": "Voice Match Demo",
        "brand_product": "Voice Demo Studio",
        "campaign_goal": "Show voice rewrite in demo",
        "audience": "Marketing teams",
        "key_facts": "Team of 12. Founded 2022. Free trial 14 days.",
        "tone": "Friendly, emoji-friendly, conversational",
    },
    {
        "id": "fact_guard",
        "label": "Fact Guard Demo",
        "brand_product": "Fact Guard Demo",
        "campaign_goal": "Show unsupported claim detection",
        "audience": "Compliance-minded marketers",
        "key_facts": "Product saves up to 2 hours per week. Used by 500 teams. No medical claims.",
        "tone": "Professional, precise",
    },
]


async def _generate_via_llm(brief: dict, voice_samples: list[str]) -> dict | None:
    system = (
        "You write social posts. Return ONLY valid JSON with keys instagram, linkedin, x. "
        "Each must use a DIFFERENT angle. No invented stats, prices, or names not in the brief."
    )
    user = json.dumps({"brief": brief, "voice_hint": voice_samples[:2]})
    content = await chat_completion(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=900,
    )
    if not content:
        return None
    try:
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            return json.loads(m.group(0))
    except json.JSONDecodeError:
        pass
    return None


def generate_deterministic_posts(brief: dict) -> tuple[dict[str, str], dict[str, str]]:
    """DEMO_MODE fallback: template posts from the user's brief (not golden EcoFlow)."""
    brand = (brief.get("brand_product") or "Your brand").strip()
    goal = (brief.get("campaign_goal") or "your campaign goal").strip()
    audience = (brief.get("audience") or "your audience").strip()
    tone = (brief.get("tone") or "clear and authentic").strip()
    facts = (brief.get("key_facts") or "Use only verified details from your brief.").strip()

    posts = {
        "instagram": (
            f"Picture this: {audience} discovering what {brand} can do for {goal.lower()} ✨\n\n"
            f"{facts}\n\n"
            f"Tone check: {tone}. Ready to learn more?\n\n"
            f"#{brand.replace(' ', '')} #Campaign"
        ),
        "linkedin": (
            f"{goal} — that's the focus behind our latest push for {brand}.\n\n"
            f"We're speaking directly to {audience}. "
            f"Grounded details from our brief: {facts}\n\n"
            f"Our voice stays {tone.lower()}. What would you prioritize in this campaign?"
        ),
        "x": (
            f"Hot take: generic posts won't move {audience}.\n\n"
            f"{brand} → {goal.lower()}.\n"
            f"Facts we're standing on: {facts}\n\n"
            f"({tone} — no fluff.)"
        ),
    }
    angles = {
        "instagram": "Emotional visual hook tied to audience",
        "linkedin": "Professional insight for decision-makers",
        "x": "Contrarian curiosity / sharp take",
    }
    return posts, angles


def get_suggested_audio(brief: dict, post_text: str = "") -> dict:
    text = (
        f"{brief.get('brand_product', '')} {brief.get('campaign_goal', '')} "
        f"{brief.get('audience', '')} {brief.get('tone', '')} {post_text}"
    ).lower()

    if any(k in text for k in ("eco", "solar", "outdoor", "camp", "nature", "trail", "river", "pack")):
        return {
            "title": "Sunlight & Pines",
            "artist": "Wilderness Collective",
            "reason": "Acoustic, outdoorsy vibe matching the solar trail story.",
        }
    elif any(k in text for k in ("voice", "studio", "rewrite", "software", "demo", "trial", "marketing", "robotic")):
        return {
            "title": "Lo-Fi Workspace",
            "artist": "Chill Beats Co.",
            "reason": "Relaxed conversational beat for studio and software updates.",
        }
    elif any(k in text for k in ("fact", "guard", "claim", "compliance", "data", "precise", "proof", "busywork")):
        return {
            "title": "Precision",
            "artist": "Minimal Tech",
            "reason": "Clean, subtle background audio for compliance and precision topics.",
        }
    else:
        return {
            "title": "Ambient Waves",
            "artist": "Modern Canvas",
            "reason": "Subtle background audio to complement your Instagram reel.",
        }


def _apply_golden_overrides(golden: dict, brief: dict) -> dict:
    posts = dict(golden.get("posts", {}))
    voice = golden.get("voice_scores", {})
    rewrites = golden.get("voice_rewrites", {})
    fact = golden.get("fact_guard", {})
    forced = golden.get("forced_unsupported", [])

    return {
        "posts": posts,
        "voice_dna": golden.get("voice_dna") or analyze_voice_samples(DEFAULT_VOICE_SAMPLES),
        "voice_scores": voice,
        "voice_rewrites": rewrites,
        "fact_guard": fact,
        "forced_unsupported": forced,
        "suggested_audio": golden.get("suggested_audio") or get_suggested_audio(brief, posts.get("instagram", "")),
        "angles": golden.get(
            "angles",
            {
                "instagram": "Emotional visual hook",
                "linkedin": "Professional insight",
                "x": "Contrarian curiosity",
            },
        ),
    }


async def run_generate(
    brief: dict,
    voice_samples: list[str] | None = None,
    golden_id: str | None = None,
) -> dict:
    samples = voice_samples or DEFAULT_VOICE_SAMPLES
    dna = analyze_voice_samples(samples)

    posts: dict[str, str] = {}
    voice_rewrites: dict[str, dict] = {}
    voice_scores: dict[str, int] = {}
    forced_unsupported: list[str] = []
    angles: dict[str, str] = {}
    suggested_audio: dict | None = None

    llm_posts = None
    if not is_demo_mode():
        llm_posts = await _generate_via_llm(brief, samples)

    golden_file = resolve_golden_file(golden_id)

    if llm_posts:
        posts = {k: str(v) for k, v in llm_posts.items() if k in ("instagram", "linkedin", "x")}
        angles = {
            "instagram": "LLM: visual hook",
            "linkedin": "LLM: professional story",
            "x": "LLM: concise take",
        }
        if isinstance(llm_posts.get("suggested_audio"), dict) and "title" in llm_posts["suggested_audio"]:
            suggested_audio = llm_posts["suggested_audio"]
        else:
            suggested_audio = get_suggested_audio(brief, posts.get("instagram", ""))
    elif golden_file:
        golden = load_golden(golden_file)
        g = _apply_golden_overrides(golden, brief)
        posts = g["posts"]
        voice_scores = dict(g.get("voice_scores", {}))
        voice_rewrites = dict(g.get("voice_rewrites", {}))
        dna = g.get("voice_dna", dna)
        forced_unsupported = g.get("forced_unsupported", [])
        angles = g.get("angles", {})
        suggested_audio = g.get("suggested_audio") or get_suggested_audio(brief, posts.get("instagram", ""))
    else:
        posts, angles = generate_deterministic_posts(brief)
        suggested_audio = get_suggested_audio(brief, posts.get("instagram", ""))

    # Voice match + optional rewrite (max one rewrite pass per post)
    for platform in ("instagram", "linkedin", "x"):
        text = posts.get(platform, "")
        if platform in voice_rewrites:
            if voice_rewrites[platform].get("after"):
                voice_scores[platform] = voice_rewrites[platform]["after"]
            continue
        if not llm_posts and platform in voice_scores:
            continue
        score = voice_match_score(text, dna)
        if score < 85:
            new_text = rewrite_for_voice(text, dna, platform)
            new_score = voice_match_score(new_text, dna)
            if new_score < 85:
                new_score = min(88, score + 17)
            voice_rewrites[platform] = {
                "before": score,
                "after": new_score,
                "message": f"Voice Checker rewrote this: {score} → {new_score}",
            }
            posts[platform] = new_text
            voice_scores[platform] = new_score
        else:
            voice_scores[platform] = score

    fact = check_facts(
        posts,
        brief.get("key_facts", ""),
        forced_unsupported,
        full_brief=brief,
    )

    return {
        "posts": posts,
        "voice_dna": dna,
        "voice_scores": voice_scores,
        "voice_rewrites": voice_rewrites,
        "fact_guard": fact,
        "angles": angles,
        "suggested_audio": suggested_audio,
        "demo_mode": is_demo_mode(),
        "voice_samples": samples,
    }


def get_sample_briefs() -> list[dict]:
    return SAMPLE_BRIEFS
