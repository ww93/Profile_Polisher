from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas import JDNormalized, MatchResult, OptimizationSuggestion, ResumeNormalized, SupplementInput


class OptimizerAgent(BaseAgent):
    name = "optimizer"

    def run(
        self,
        resume: ResumeNormalized,
        jd: JDNormalized,
        match: MatchResult,
        supplement: SupplementInput | None = None,
    ) -> list[OptimizationSuggestion]:
        suggestions: list[OptimizationSuggestion] = []
        for gap in match.gaps[:3]:
            missing = gap.replace("Missing required skill: ", "")
            before = "Worked on backend services."
            after = (
                f"Designed and delivered backend services with {missing}, improving throughput by 30% "
                f"and reducing incident rate by 20%."
            )
            suggestions.append(
                OptimizationSuggestion(
                    project="General Backend Project",
                    before=before,
                    after=after,
                    reason=f"JD highlights {missing} as required; add direct evidence with measurable impact.",
                )
            )

        if supplement and supplement.optimization_goal:
            suggestions.insert(
                0,
                OptimizationSuggestion(
                    project="User Requested Focus",
                    before="Current bullet points are generic and impact-light.",
                    after=f"Reframe bullets to align with goal: {supplement.optimization_goal}",
                    reason="Applied user follow-up optimization requirement.",
                ),
            )

        if not suggestions:
            suggestions.append(
                OptimizationSuggestion(
                    project="Primary Project",
                    before="Built internal platform features.",
                    after="Built and scaled internal platform features adopted by 3 teams, cutting release cycle time by 25%.",
                    reason="Quantified outcomes improve interview signal quality.",
                )
            )

        return suggestions
