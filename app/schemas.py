from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SupplementInput(BaseModel):
    candidate_context: str | None = None
    job_constraints: str | None = None
    optimization_goal: str | None = None
    focus_sections: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    jd_text: str = Field(..., min_length=1)
    parseur_document_id: str | None = None
    supplement: SupplementInput | None = None


class ResumeNormalized(BaseModel):
    raw_text: str
    projects: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class JDNormalized(BaseModel):
    raw_text: str
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)


class ScoreDimensions(BaseModel):
    skills: int
    projects: int
    seniority: int
    domain: int


class MatchResult(BaseModel):
    overall_score: int
    dimensions: ScoreDimensions
    strengths: list[str]
    gaps: list[str]
    evidence: dict[str, list[str]]


class OptimizationSuggestion(BaseModel):
    project: str
    before: str
    after: str
    reason: str


class InterviewQuestion(BaseModel):
    category: Literal["technical", "project_followup", "behavioral"]
    question: str
    focus: str


class ReviewResult(BaseModel):
    confidence: Literal["high", "medium", "low"]
    quality_flags: list[str] = Field(default_factory=list)


class ComparisonSummary(BaseModel):
    has_previous: bool = False
    score_delta: int = 0
    added_strengths: list[str] = Field(default_factory=list)
    removed_gaps: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    match: MatchResult
    optimizations: list[OptimizationSuggestion]
    interview_questions: list[InterviewQuestion]
    review: ReviewResult
    supplement_applied: SupplementInput | None = None
    comparison: ComparisonSummary = Field(default_factory=ComparisonSummary)


class AnalyzeFormPayload(BaseModel):
    jd_text: str
    resume_text: str | None = None
    parseur_document_id: str | None = None
    supplement: SupplementInput | None = None
    previous_result: dict[str, Any] | None = None
