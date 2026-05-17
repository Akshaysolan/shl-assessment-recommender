# SHL Assessment Recommender
**SHL Labs AI Intern Take-home Assignment**

Conversational FastAPI agent that recommends SHL Individual Test Solutions via natural dialogue.
Powered by **Groq** (llama-3.3-70b) — free, fast, JSON-native.

---

## Project Structure

```
shl_recommender/                ← project root
│
├── app/                        ← Application (all runtime code)
│   ├── __init__.py
│   ├── main.py                 ← FastAPI app + Groq agent + validation
│   └── catalog.json            ← 132 SHL Individual Test Solutions
│
├── tests/                      ← Test suite
│   ├── __init__.py
│   └── test_agent.py           ← 30 tests: hard evals + behavior probes + recall
│
├── deployment/                 ← Deploy configs (do not edit for local dev)
│   ├── Dockerfile
│   ├── Procfile                ← Render / Railway / Heroku
│   └── render.yaml             ← Render one-click config
│
├── scripts/                    ← Helper shell scripts
│   ├── install.sh              ← pip install
│   ├── run.sh                  ← start server
│   └── test.sh                 ← run tests (auto-detects key)
│
├── APPROACH.md                 ← 2-page design document (submission requirement)
├── requirements.txt            ← Python dependencies
├── .env.example                ← Copy to .env and fill in key
└── README.md                   ← This file
```

---

## Commands — Step by Step

### Step 1 — Unzip & enter project
```bash
unzip shl_recommender.zip
cd shl_recommender
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
# or
bash scripts/install.sh
```

### Step 3 — Set your Groq API key (free at console.groq.com)
```bash
# Option A: environment variable (this session only)
export GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# Option B: .env file (persists across sessions)
cp .env.example .env
nano .env   # paste your key
```

### Step 4 — Start the server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# or
bash scripts/run.sh
```

Open in browser:
- Home:         http://localhost:8000
- Swagger UI:   http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Step 5 — Test it
```bash
# Quick curl test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"I am hiring a Java developer who works with stakeholders"}]}'

# Unit tests only (no API key needed) — 16 tests
python -m pytest tests/ -v -k "not Live and not Recall and not Behavior"

# Full test suite — 30 tests (needs GROQ_API_KEY)
python -m pytest tests/ -v

# Or use the script (auto-detects key)
bash scripts/test.sh
```

---

## API Reference

### `GET /health`
```json
{"status": "ok"}
```

### `POST /chat`
Stateless — send the full conversation history every call.

**Request:**
```json
{
  "messages": [
    {"role": "user",      "content": "Hiring a Java developer who works with stakeholders"},
    {"role": "assistant", "content": "Sure. What is seniority level?"},
    {"role": "user",      "content": "Mid-level, around 4 years"}
  ]
}
```

**Response (non-negotiable schema per assignment PDF):**
```json
{
  "reply": "Got it. Here are 5 assessments that fit a mid-level Java dev with stakeholder needs.",
  "recommendations": [
    {"name": "Java 8 (New)",  "url": "https://www.shl.com/products/product-catalog/view/java-8-new/",  "test_type": "K"},
    {"name": "OPQ32r",        "url": "https://www.shl.com/products/product-catalog/view/opq32r/",       "test_type": "P"}
  ],
  "end_of_conversation": false
}
```

| Field | Type | Notes |
|---|---|---|
| `reply` | string | Agent's conversational message |
| `recommendations` | array | Empty while clarifying/refusing; 1–10 items when shortlisting |
| `end_of_conversation` | bool | `true` only when task is complete |
| `recommendations[].name` | string | Exact name from SHL catalog |
| `recommendations[].url` | string | Exact URL from SHL catalog |
| `recommendations[].test_type` | string | Single letter: A/B/C/D/E/K/P/S |

---

## Deploy (Free Platforms)

### Render ⭐ (recommended — 750 hrs/month free, no credit card)
1. Push project to GitHub
2. render.com → **New Web Service** → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add env var: `GROQ_API_KEY` = `gsk_...`
6. Click **Deploy** → live in ~2 min, health check allowed 2 min cold start ✓

### Railway (free $5/month credit)
1. railway.app → New Project → Deploy from GitHub
2. Add variable: `GROQ_API_KEY` = `gsk_...`
3. Auto-detects `Procfile` → deploys automatically

### Hugging Face Spaces (always free)
1. huggingface.co/spaces → New Space → SDK: **Docker**
2. Upload all files → Settings → Secrets → add `GROQ_API_KEY`

### Docker / VPS
```bash
cd shl_recommender
cp deployment/Dockerfile .
docker build -t shl-recommender .
docker run -p 8000:8000 -e GROQ_API_KEY=gsk_... shl-recommender
```

---

## Scoring Alignment (from PDF)

| Criterion | How this project satisfies it |
|---|---|
| Schema compliance | `ChatResponse` Pydantic model enforces `reply`, `recommendations`, `end_of_conversation` on every response |
| Catalog-only URLs | dual-layer validation: exact URL → exact name → partial name; hallucinations dropped |
| Turn cap (max 8) | enforced in endpoint before calling Groq |
| 30s timeout | Groq llama-3.3-70b responds in <2s; cold start on Render is <2 min |
| Vague query → clarify | System prompt rule: "Never recommend on turn 1 for vague queries" |
| Off-topic → refuse | System prompt rule: refuse with one sentence, keep recommendations empty |
| Refine | Prompt rule: "update shortlist in place; do NOT start over" |
| Compare | Prompt rule: "base answer only on catalog data" |
| Prompt injection | Handled by scope refusal rule |

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| fastapi | 0.115.12 | Web framework |
| uvicorn | 0.34.2 | ASGI server |
| groq | ≥1.2.0 | Groq LLM SDK |
| pydantic | ≥2.0 | Schema validation |
