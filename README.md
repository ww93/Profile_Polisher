# Profile Polisher (Multi-Agent + Web UI)

This repository contains a multi-agent resume/JD analysis backend and a React + Vite frontend with a **left/right split layout** inspired by productivity coding tools.

## Architecture

Backend agents:

1. **Parser Agent**: normalize resume/JD data.
2. **Matcher Agent**: compute score and skill evidence.
3. **Optimizer Agent**: generate rewrite suggestions.
4. **Interviewer Agent**: generate interview follow-up questions.
5. **Reviewer Agent**: apply quality checks.

An orchestrator executes these agents and supports iterative refinement with structured supplement input.

## Frontend capabilities

- Left panel: resume upload (`PDF` / `DOCX`), resume text fallback, JD input, Parseur document ID, supplement form.
- Right panel: match score, gap analysis, optimizations, interview questions, and version comparison.
- Supplement is **not chatbot UI**; it is a structured form for follow-up requirements.

## API

### `POST /analyze` (multipart/form-data)

Fields:

- `jd_text` (required)
- `resume_file` (optional, `PDF`/`DOCX`)
- `resume_text` (optional fallback)
- `parseur_document_id` (optional)
- `supplement_json` (optional JSON string)
- `previous_result_json` (optional JSON string for diff/comparison)

Rules:

- One of `resume_file`, `resume_text`, or `parseur_document_id` must be provided.
- If a previous result is provided, backend returns comparison delta.

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
