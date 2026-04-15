from __future__ import annotations

import re

from app.agents.base import BaseAgent
from app.schemas import JDNormalized, ResumeNormalized


class ParserAgent(BaseAgent):
    name = "parser"

    def run(self, resume_text: str, jd_text: str) -> tuple[ResumeNormalized, JDNormalized]:
        resume_skills = self._extract_skills(resume_text)
        jd_must = self._extract_must_have_skills(jd_text)

        resume_projects = [
            line.strip("- •")
            for line in resume_text.splitlines()
            if any(token in line.lower() for token in ("project", "项目", "experience", "经历"))
        ]

        resume = ResumeNormalized(raw_text=resume_text, skills=resume_skills, projects=resume_projects)
        jd = JDNormalized(raw_text=jd_text, must_have_skills=jd_must, nice_to_have_skills=[])
        return resume, jd

    @staticmethod
    def _extract_skills(text: str) -> list[str]:
        common = [
            "python",
            "java",
            "go",
            "kubernetes",
            "docker",
            "sql",
            "react",
            "node",
            "fastapi",
            "redis",
            "aws",
        ]
        lower = text.lower()
        return [s for s in common if re.search(rf"\b{re.escape(s)}\b", lower)]

    @staticmethod
    def _extract_must_have_skills(text: str) -> list[str]:
        return ParserAgent._extract_skills(text)
