from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from baseline import COMPARE_DATA
from learning import get_preferences, record_edit
from llm_router import is_demo_mode, provider_label
from pipeline import get_sample_briefs, run_generate

app = FastAPI(title="OmniPost AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BriefIn(BaseModel):
    brand_product: str = ""
    campaign_goal: str = ""
    audience: str = ""
    key_facts: str = ""
    tone: str = ""
    voice_samples: list[str] = Field(default_factory=list)
    golden_id: str | None = None


class LearnIn(BaseModel):
    platform: str
    before: str
    after: str


class ApproveIn(BaseModel):
    platform: str
    content: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "demo_mode": is_demo_mode(),
        "provider": provider_label(),
    }


@app.get("/samples")
def samples():
    return {"briefs": get_sample_briefs()}


@app.get("/compare")
def compare():
    return COMPARE_DATA


@app.get("/learning")
def learning_prefs():
    return {"preferences": get_preferences()}


@app.post("/generate")
async def generate(body: BriefIn):
    brief = body.model_dump(exclude={"voice_samples", "golden_id"})
    result = await run_generate(brief, body.voice_samples or None, golden_id=body.golden_id)
    return result


@app.post("/learn")
def learn(body: LearnIn):
    return record_edit(body.platform, body.before, body.after)


@app.post("/approve")
def approve(body: ApproveIn):
    return {
        "approved": True,
        "platform": body.platform,
        "message": f"Approved for {body.platform} (copy-only — no auto-publish)",
    }
