from __future__ import annotations

import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.orchestrator import AnalysisOrchestrator
from app.schemas import AnalyzeRequest, AnalyzeResponse, LLMConfig, SupplementInput
from app.services.document_parser import DocumentParser

app = FastAPI(title="Profile Polisher API", version="0.3.0")
orchestrator = AnalysisOrchestrator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    jd_text: str = Form(...),
    resume_text: str | None = Form(default=None),
    parseur_document_id: str | None = Form(default=None),
    supplement_json: str | None = Form(default=None),
    llm_config_json: str | None = Form(default=None),
    previous_result_json: str | None = Form(default=None),
    resume_file: UploadFile | None = File(default=None),
) -> AnalyzeResponse:
    inferred_resume_text = (resume_text or "").strip()

    if resume_file is not None:
        payload = await resume_file.read()
        try:
            inferred_resume_text = DocumentParser.parse(resume_file.filename or "resume", payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not inferred_resume_text and not parseur_document_id:
        raise HTTPException(status_code=400, detail="Either resume_text, resume_file, or parseur_document_id must be provided.")

    supplement = None
    if supplement_json:
        supplement = SupplementInput.model_validate_json(supplement_json)

    llm = None
    if llm_config_json:
        llm = LLMConfig.model_validate_json(llm_config_json)

    previous_result = None
    if previous_result_json:
        previous_result = AnalyzeResponse.model_validate(json.loads(previous_result_json))

    request = AnalyzeRequest(
        resume_text=inferred_resume_text or "From Parseur",
        jd_text=jd_text,
        parseur_document_id=parseur_document_id,
        supplement=supplement,
        llm=llm,
    )

    return await orchestrator.run(request, previous_result=previous_result)
