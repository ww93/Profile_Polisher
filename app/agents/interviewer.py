from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.prompts import INTERVIEW_SYSTEM_PROMPT, INTERVIEW_USER_TEMPLATE
from app.schemas import InterviewQuestion, JDNormalized, LLMConfig, MatchResult, ResumeNormalized, SupplementInput
from app.services.llm_client import LLMClient


class InterviewerAgent(BaseAgent):
    name = "interviewer"

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def run(
        self,
        resume: ResumeNormalized,
        jd: JDNormalized,
        match: MatchResult,
        supplement: SupplementInput | None = None,
        llm: LLMConfig | None = None,
    ) -> list[InterviewQuestion]:
        if llm:
            try:
                payload = await self.llm_client.chat_json(
                    config=llm,
                    system_prompt=INTERVIEW_SYSTEM_PROMPT,
                    user_prompt=INTERVIEW_USER_TEMPLATE.format(
                        supplement=(supplement.model_dump_json(indent=2) if supplement else "None"),
                        resume=resume.raw_text,
                        jd=jd.raw_text,
                        match_json=match.model_dump_json(indent=2),
                    ),
                )
                return [InterviewQuestion.model_validate(item) for item in payload.get("questions", [])][:12]
            except Exception:
                pass

        questions: list[InterviewQuestion] = []

        for skill in jd.must_have_skills[:5]:
            questions.append(
                InterviewQuestion(
                    category="technical",
                    question=f"How have you applied {skill} in production, and what trade-offs did you make?",
                    focus="Depth of technical decision-making",
                )
            )

        questions.append(
            InterviewQuestion(
                category="project_followup",
                question="Choose one core project and explain architecture, bottlenecks, and outcome metrics.",
                focus="System design clarity and impact ownership",
            )
        )
        questions.append(
            InterviewQuestion(
                category="behavioral",
                question="Tell me about a disagreement with a teammate and how you resolved it.",
                focus="Collaboration and conflict management",
            )
        )

        if supplement and supplement.job_constraints:
            questions.insert(
                0,
                InterviewQuestion(
                    category="technical",
                    question=f"Given this hiring constraint: '{supplement.job_constraints}', what would you prioritize first in your first 90 days?",
                    focus="Role prioritization under explicit constraints",
                ),
            )

        return questions
