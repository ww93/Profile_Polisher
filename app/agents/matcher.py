from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas import JDNormalized, MatchResult, ResumeNormalized, ScoreDimensions, SupplementInput


class MatcherAgent(BaseAgent):
    name = "matcher"

    def run(self, resume: ResumeNormalized, jd: JDNormalized, supplement: SupplementInput | None = None) -> MatchResult:
        required = set(jd.must_have_skills)
        actual = set(resume.skills)
        hit = required.intersection(actual)
        miss = required - actual

        skills_weight = 40
        projects_weight = 30
        if supplement and "projects" in supplement.focus_sections:
            projects_weight = 40
            skills_weight = 30

        skills_score = min(skills_weight, int((len(hit) / max(len(required), 1)) * skills_weight))
        projects_score = projects_weight if resume.projects else 10
        seniority_score = 15
        domain_score = 15
        total = min(100, skills_score + projects_score + seniority_score + domain_score)

        strengths = [f"Has required skill: {x}" for x in sorted(hit)]
        gaps = [f"Missing required skill: {x}" for x in sorted(miss)]
        evidence = {"skills": [f"Detected in resume: {x}" for x in sorted(hit)]}

        if supplement and supplement.candidate_context:
            strengths.append("Applied user-supplied candidate context in evaluation")
        if supplement and supplement.job_constraints:
            evidence.setdefault("job_constraints", []).append(supplement.job_constraints)

        return MatchResult(
            overall_score=total,
            dimensions=ScoreDimensions(
                skills=skills_score,
                projects=projects_score,
                seniority=seniority_score,
                domain=domain_score,
            ),
            strengths=strengths,
            gaps=gaps,
            evidence=evidence,
        )
