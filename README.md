

# OmniPost AI

## Project Overview

OmniPost AI is a hackathon-ready social media campaign assistant that takes one campaign brief and turns it into platform-specific post ideas for Instagram, LinkedIn, and X. It helps marketing teams generate content, improve brand voice consistency, detect unsupported claims, and refine copy before approval.

 It can generate three different post angles from a single brief, check how well each post matches a target voice, flag risky or unsupported claims, and allow users to edit the final content before approving it.

## Technologies Used

### Backend
- Python 3.11
- FastAPI
- Pydantic
- Uvicorn
- python-dotenv

### Frontend
- React
- Vite
- Tailwind CSS

### AI / Content Pipeline
- OpenAI-compatible LLM integration (optional)
- Demo/golden fallback mode for no-API-key usage
- Built-in voice analysis and fact-checking logic

## Repository Structure

```bash
omnipost-ai/
├── backend/
│   ├── baseline.py
│   ├── fact_guard.py
│   ├── golden/
│   ├── learning.py
│   ├── llm_router.py
│   ├── main.py
│   ├── music.py
│   ├── pipeline.py
│   ├── test_music.py
│   ├── test_pipeline.py
│   └── voice.py
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── .env.example
├── requirements.txt
├── vercel.json
├── README.md
├── .gitignore
└── .python-version
```

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd omnipost-ai
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Copy environment variables

```bash
cp .env.example .env
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
```

## Environment Variables

The project uses a sample environment file:

```env
DEMO_MODE=1
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### Notes
- `DEMO_MODE=1` allows the app to work without external API keys.
- If you want live AI generation, set `DEMO_MODE=0` and provide valid API values.

## How to Run the Project

### Start the backend

From the project root:

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Start the frontend

Open a second terminal and run:

```bash
cd frontend
npm run dev
```

Then visit:

```text
http://localhost:5173
```

The frontend is configured to call the backend at:

```text
http://127.0.0.1:8000
```

## Features

- Studio mode for generating posts from a campaign brief
- Voice DNA analysis to compare brand tone
- Fact Guard checks for unsupported claims
- Demo tab with built-in examples
- Compare page for benchmark-style review
- Edit + approval workflow for final copy

## API Highlights

- `GET /health` — app health and demo status
- `POST /generate` — generate platform-specific social posts
- `POST /learn` — save user editing preferences
- `POST /approve` — approve final post content
- `GET /samples` — demo briefs
- `GET /compare` — compare baseline and generated output

## Demo Flow

1. Open the Demo section.
2. Select a sample brief.
3. Generate outputs for Instagram, LinkedIn, and X.
4. Review voice-match suggestions.
5. Check fact-guard warnings.
6. Refine content in the Studio view.
7. Approve the final version.
8. you can also write your own brief and it shows the output 


