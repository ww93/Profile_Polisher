from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.prompts import OPTIMIZER_SYSTEM_PROMPT, OPTIMIZER_USER_TEMPLATE
from app.schemas import JDNormalized, LLMConfig, MatchResult, OptimizationSuggestion, ResumeNormalized, SupplementInput
from app.services.llm_client import LLMClient


class OptimizerAgent(BaseAgent):
    name = "optimizer"

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def run(
        self,
        resume: ResumeNormalized,
        jd: JDNormalized,
        match: MatchResult,
        supplement: SupplementInput | None = None,
        llm: LLMConfig | None = None,
    ) -> list[OptimizationSuggestion]:
        if llm:
            try:
                payload = await self.llm_client.chat_json(
                    config=llm,
                    system_prompt=OPTIMIZER_SYSTEM_PROMPT,
                    user_prompt=OPTIMIZER_USER_TEMPLATE.format(
                        supplement=(supplement.model_dump_json(indent=2) if supplement else "None"),
                        resume=resume.raw_text,
                        jd=jd.raw_text,
                        match_json=match.model_dump_json(indent=2),
                    ),
                )
                return [OptimizationSuggestion.model_validate(item) for item in payload.get("optimizations", [])][:6]
            except Exception:
                pass

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
