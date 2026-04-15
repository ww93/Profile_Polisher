from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas import AnalyzeResponse, ReviewResult


class ReviewerAgent(BaseAgent):
    name = "reviewer"

    def run(self, response: AnalyzeResponse) -> ReviewResult:
        flags: list[str] = []

        if response.match.overall_score < 50:
            flags.append("Low overall match score; recommend stronger project evidence and targeted skill additions.")

        if not response.optimizations:
            flags.append("No optimization suggestions generated.")

        confidence = "high"
        if flags:
            confidence = "medium"
        if len(flags) > 2:
            confidence = "low"

        return ReviewResult(confidence=confidence, quality_flags=flags)
