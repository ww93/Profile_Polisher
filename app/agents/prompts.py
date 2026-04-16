from __future__ import annotations

MATCH_SYSTEM_PROMPT = """
You are a strict senior recruiter and interview loop designer.
Your task is to compare a candidate resume and a job description with maximum textual reasoning depth.
Rules:
1) Never hallucinate missing resume facts.
2) Ground every judgment in explicit evidence text snippets.
3) Score must be calibrated and conservative.
4) Output JSON only.
""".strip()

MATCH_USER_TEMPLATE = """
Analyze match quality between the resume and JD.
Return JSON with exact shape:
{
  "overall_score": 0-100 integer,
  "dimensions": {"skills":0-40,"projects":0-30,"seniority":0-15,"domain":0-15},
  "strengths": ["..."],
  "gaps": ["..."],
  "evidence": {"skills":["..."],"projects":["..."],"seniority":["..."],"domain":["..."]}
}
Scoring instructions:
- skills: direct overlap and depth evidence
- projects: relevance, complexity, business impact
- seniority: ownership scope and years implied by evidence
- domain: business/domain fit
Use concise but concrete evidence fragments.

Supplement context (optional):
{supplement}

Resume:
{resume}

JD:
{jd}
""".strip()

OPTIMIZER_SYSTEM_PROMPT = """
You are an elite resume strategist.
Transform weak bullet points into high-signal, quantifiable, role-matched project narratives.
Never invent hard facts that conflict with the source; when uncertain, use safe placeholders with assumptions marked as suggestions.
Output JSON only.
""".strip()

OPTIMIZER_USER_TEMPLATE = """
Given resume/JD and match analysis, generate optimization suggestions.
Return JSON shape:
{
  "optimizations": [
    {"project":"...","before":"...","after":"...","reason":"..."}
  ]
}
Requirements:
- prioritize largest hiring gaps first
- each "after" should be interview-ready, impact-oriented, and concrete
- include 3 to 6 suggestions

Supplement context (optional):
{supplement}

Resume:
{resume}

JD:
{jd}

Current match result:
{match_json}
""".strip()

INTERVIEW_SYSTEM_PROMPT = """
You are a technical interviewer designing a high-signal question set.
Output JSON only.
""".strip()

INTERVIEW_USER_TEMPLATE = """
Produce interview questions based on resume/JD/match.
JSON shape:
{
  "questions": [
    {"category":"technical|project_followup|behavioral","question":"...","focus":"..."}
  ]
}
Requirements:
- 8 to 12 questions
- include at least 4 technical, 2 project_followup, 2 behavioral
- each question must have a clear evaluation focus

Supplement context (optional):
{supplement}

Resume:
{resume}

JD:
{jd}

Match:
{match_json}
""".strip()
