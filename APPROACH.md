# SHL Assessment Recommender — Approach Document

## Problem Decomposition

Hiring managers describe roles in natural language, not catalog vocabulary. The task is to bridge this gap through a conversational agent that clarifies intent, retrieves from the SHL catalog, and returns a grounded shortlist. Four behaviors are required: Clarify, Recommend, Refine, Compare. The agent must also stay in scope (refuse off-topic/injection) and honor hard schema and turn constraints.

---

## Design Choices

### 1. Retrieval: Full-Catalog Context Injection (not vector search)

The SHL Individual Test Solutions catalog (~132 items after scraping) is injected verbatim into the system prompt. At ~8 KB this fits easily in the 128K context window of llama-3.3-70b.

**Why not FAISS/Chroma:** With only 132 items, retrieval recall from a vector store would introduce unnecessary complexity without meaningful benefit. The model sees all items every turn — no missed results, no similarity-threshold tuning, deterministic grounding.

**Trade-off documented:** If the catalog grows to 500+ items, a hybrid approach (vector pre-filter + rerank) would be warranted. This threshold is noted but not a concern now.

### 2. LLM: Groq (llama-3.3-70b-versatile)

Chosen for: free tier (14,400 req/day), native JSON mode (`response_format={"type":"json_object"}`), sub-second latency (well under the 30s timeout), and strong instruction-following. Temperature set to 0.2 for deterministic, low-hallucination output.

### 3. Agent Logic: Prompt-as-Policy

All four conversational behaviors are encoded in the system prompt with explicit rules and worked examples. No LangChain/LangGraph orchestration — a single stateless call per turn is sufficient and easier to reason about.

Key prompt engineering choices:
- **Explicit JSON schema** in the prompt — prevents preamble text that breaks `json.loads`
- **Turn budget rule** — instructs the model to commit to a shortlist by turn 4, preventing infinite clarification loops within the 8-turn cap
- **Dual negative examples** — "do NOT recommend on turn 1 for vague queries" and "never invent a name or URL"
- **Scope boundary** stated positively and negatively

### 4. Hallucination Guard (dual-layer)

Every returned recommendation is validated against a Python `set` of catalog URLs before returning:
1. Exact URL match (fastest, most reliable)
2. Exact name match (case-insensitive)
3. Partial name containment (≥4 chars) — catches "Java 8" → "Java 8 (New)"

Items failing all three layers are silently dropped. This ensures the caller **never receives a URL outside the catalog**, regardless of model behavior.

---

## Evaluation Approach

**Hard evals (automated, no API key):** 16 tests covering schema compliance, catalog integrity (no duplicate URLs, valid type codes), turn cap enforcement, and hallucination guard.

**Behavior probes (require GROQ_API_KEY):** 9 binary assertions matching the PDF rubric — vague-query no-rec on turn 1, off-topic refusal, prompt injection refusal, 1–10 recommendation bounds, no hallucinated URLs, refine updates shortlist, compare produces grounded reply, specific role gets recommendations, test_type is single letter.

**Recall@10 traces:** 3 representative traces (Java developer, data scientist, customer service) checking that expected assessment types appear in the shortlist.

---

## What Didn't Work

1. **Vector search (first attempt):** FAISS with sentence-transformers recalled wrong items for short assessment names like "OPQ32r" — short strings have weak semantic signal. Full-context injection outperformed it on every test case.
2. **Temperature 0.7:** The model occasionally invented plausible-sounding assessment names (e.g. "Verify - Logical Reasoning") that don't exist in the catalog. Lowering to 0.2 eliminated hallucinations in all observed runs.
3. **JSON schema with extra fields:** Added `"reason"` field to recommendations initially. Removed it to strictly match the PDF's non-negotiable schema (only `name`, `url`, `test_type`).

---

## AI Tools Used

Claude (claude.ai) was used to draft the initial system prompt, iterate on the JSON schema enforcement rules, and review the test suite. All code was written and reviewed by the author.
