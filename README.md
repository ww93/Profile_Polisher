# Profile Polisher (Multi-Agent + LLM-Enhanced)

This repository contains a multi-agent resume/JD analysis backend and a React + Vite frontend with a left/right split layout.

## Key update: BYOK LLM analysis

The platform now supports **Bring Your Own Key (BYOK)** LLM analysis.
Users can input their own API key/base URL/model in the UI, and the backend will use those credentials for deep JD matching and project optimization.

When no LLM config is provided, the system falls back to deterministic rule-based logic.

## Architecture

Backend agents:

1. **Parser Agent**: normalize resume/JD data.
2. **Matcher Agent**: LLM-first semantic matching + evidence extraction.
3. **Optimizer Agent**: LLM-first resume/project rewrite optimization.
4. **Interviewer Agent**: LLM-first interview question generation.
5. **Reviewer Agent**: apply quality checks.

A single orchestrator coordinates these agents and iterative refinement.

## Prompt strategy

Prompts are optimized for high textual analysis depth with strict JSON outputs:

- conservative scoring
- evidence-grounded reasoning
- gap-priority optimization
- role-specific interview signal generation

See: `app/agents/prompts.py`.

## API

### `POST /analyze` (multipart/form-data)

Fields:

- `jd_text` (required)
- `resume_file` (optional, `PDF`/`DOCX`)
- `resume_text` (optional fallback)
- `parseur_document_id` (optional)
- `supplement_json` (optional JSON string)
- `llm_config_json` (optional JSON string: `api_key`, `base_url`, `model`, `temperature`)
- `previous_result_json` (optional JSON string for diff/comparison)

Rules:

- One of `resume_file`, `resume_text`, or `parseur_document_id` must be provided.
- If `llm_config_json` is present, JD analysis + optimization + interview generation use LLM.
- If LLM call fails, fallback rules are applied.

## Parseur integration

Environment variables:

- `PARSEUR_API_TOKEN`
- `PARSEUR_MAILBOX_ID`

If Parseur is not configured or unavailable, backend falls back to file/text input.

## Run backend

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`  
Backend default URL: `http://localhost:8000`

## Testing Guide

See `TESTING_README.md` for backend/frontend run and integration test steps.
