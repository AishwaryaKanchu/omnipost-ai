# OmniPost AI

Hackathon MVP: **one brief → three platform-native posts (Instagram, LinkedIn, X) → Voice Match → Fact Guard → edit → approve.**

No database, no auth, no auto-publishing. Works **without API keys** when `DEMO_MODE=1`.

## Quick start

### Backend (Python 3.11)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r ../requirements.txt
copy ..\.env.example ..\.env
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). API calls proxy to `http://127.0.0.1:8000`.

## Demo flow (2 minutes)

1. Open **Demo** tab → **Voice Match Demo** → Run demo → see `Voice Checker rewrote this: 71 → 88` on Instagram.
2. **Fact Guard Demo** → unsupported claims flagged on X.
3. **Studio** → edit a post → **Learned from your edit ✓** → **Approve** / **Copy**.

Footer shows **DEMO MODE** or your LLM provider when configured.

## Environment

| Variable | Description |
|----------|-------------|
| `DEMO_MODE=1` | Golden responses only, no external AI |
| `LLM_API_KEY` | OpenAI-compatible API key |
| `LLM_BASE_URL` | Default `https://api.openai.com/v1` |
| `LLM_MODEL` | Default `gpt-4o-mini` |

If the LLM call fails, the app falls back to golden/demo responses.

## API

- `GET /health`
- `POST /generate` — brief JSON → posts, voice scores, fact guard
- `POST /learn` — record edit preferences
- `POST /approve` — mark approved (copy-only)
- `GET /samples` — demo briefs
- `GET /compare` — baseline vs OmniPost (labeled demo data)

## Project layout

```
backend/          FastAPI, pipeline, voice, fact guard, golden/
frontend/         React + Vite + Tailwind
```

## License

MIT — hackathon project.
