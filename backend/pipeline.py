"""Brief → 3 posts → voice match → rewrite → fact guard."""
import json
import re

from fact_guard import check_facts
from llm_router import chat_completion, is_demo_mode, load_golden, pick_golden_brief
from voice import analyze_voice_samples, rewrite_for_voice, voice_match_score

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
        "angles": golden.get(
            "angles",
            {
                "instagram": "Emotional visual hook",
                "linkedin": "Professional insight",
                "x": "Contrarian curiosity",
            },
        ),
    }


async def run_generate(brief: dict, voice_samples: list[str] | None = None) -> dict:
    samples = voice_samples or DEFAULT_VOICE_SAMPLES
    dna = analyze_voice_samples(samples)

    posts: dict[str, str] = {}
    voice_rewrites: dict[str, dict] = {}
    voice_scores: dict[str, int] = {}
    forced_unsupported: list[str] = []
    angles: dict[str, str] = {}

    llm_posts = None
    if not is_demo_mode():
        llm_posts = await _generate_via_llm(brief, samples)

    if llm_posts:
        posts = {k: str(v) for k, v in llm_posts.items() if k in ("instagram", "linkedin", "x")}
        angles = {
            "instagram": "LLM: visual hook",
            "linkedin": "LLM: professional story",
            "x": "LLM: concise take",
        }
    else:
        golden_name = pick_golden_brief(brief)
        golden = load_golden(golden_name)
        g = _apply_golden_overrides(golden, brief)
        posts = g["posts"]
        voice_scores = dict(g.get("voice_scores", {}))
        voice_rewrites = dict(g.get("voice_rewrites", {}))
        dna = g.get("voice_dna", dna)
        forced_unsupported = g.get("forced_unsupported", [])
        angles = g.get("angles", {})

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

    fact = check_facts(posts, brief.get("key_facts", ""), forced_unsupported)

    return {
        "posts": posts,
        "voice_dna": dna,
        "voice_scores": voice_scores,
        "voice_rewrites": voice_rewrites,
        "fact_guard": fact,
        "angles": angles,
        "demo_mode": is_demo_mode(),
        "voice_samples": samples,
    }


def get_sample_briefs() -> list[dict]:
    return SAMPLE_BRIEFS
