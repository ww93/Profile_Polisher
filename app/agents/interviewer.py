from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas import InterviewQuestion, JDNormalized, ResumeNormalized, SupplementInput


class InterviewerAgent(BaseAgent):
    name = "interviewer"

    def run(
        self,
        resume: ResumeNormalized,
        jd: JDNormalized,
        supplement: SupplementInput | None = None,
    ) -> list[InterviewQuestion]:
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
