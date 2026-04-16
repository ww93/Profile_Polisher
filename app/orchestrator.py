from __future__ import annotations

from app.agents.interviewer import InterviewerAgent
from app.agents.matcher import MatcherAgent
from app.agents.optimizer import OptimizerAgent
from app.agents.parser import ParserAgent
from app.agents.reviewer import ReviewerAgent
from app.schemas import AnalyzeRequest, AnalyzeResponse, ComparisonSummary, MatchResult
from app.services.llm_client import LLMClient
from app.services.parseur_client import ParseurClient


class AnalysisOrchestrator:
    def __init__(self) -> None:
        self.parseur = ParseurClient()
        self.llm_client = LLMClient()
        self.parser_agent = ParserAgent()
        self.matcher_agent = MatcherAgent(self.llm_client)
        self.optimizer_agent = OptimizerAgent(self.llm_client)
        self.interviewer_agent = InterviewerAgent(self.llm_client)
        self.reviewer_agent = ReviewerAgent()

    async def run(self, request: AnalyzeRequest, previous_result: AnalyzeResponse | None = None) -> AnalyzeResponse:
        resume_text = request.resume_text

        if request.parseur_document_id:
            parseur_text = await self.parseur.fetch_document_text(request.parseur_document_id)
            if parseur_text:
                resume_text = parseur_text

        resume, jd = self.parser_agent.run(resume_text=resume_text, jd_text=request.jd_text)
        match = await self.matcher_agent.run(resume=resume, jd=jd, supplement=request.supplement, llm=request.llm)
        optimizations = await self.optimizer_agent.run(
            resume=resume,
            jd=jd,
            match=match,
            supplement=request.supplement,
            llm=request.llm,
        )
        interview_questions = await self.interviewer_agent.run(
            resume=resume,
            jd=jd,
            match=match,
            supplement=request.supplement,
            llm=request.llm,
        )

        draft = AnalyzeResponse(
            match=match,
            optimizations=optimizations,
            interview_questions=interview_questions,
            supplement_applied=request.supplement,
            comparison=self._compare(match, previous_result.match if previous_result else None),
            review={"confidence": "high", "quality_flags": []},
        )
        review = self.reviewer_agent.run(draft)
        draft.review = review
        return draft

    @staticmethod
    def _compare(current: MatchResult, previous: MatchResult | None) -> ComparisonSummary:
        if previous is None:
            return ComparisonSummary(has_previous=False)

        current_strengths = set(current.strengths)
        previous_strengths = set(previous.strengths)
        current_gaps = set(current.gaps)
        previous_gaps = set(previous.gaps)

        return ComparisonSummary(
            has_previous=True,
            score_delta=current.overall_score - previous.overall_score,
            added_strengths=sorted(list(current_strengths - previous_strengths)),
            removed_gaps=sorted(list(previous_gaps - current_gaps)),
        )
