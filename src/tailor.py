"""腿 A：把一段 JD 变成定制报告（匹配度 + 定制简历 + 求职信）。"""

from src import llm
from src.models import TailorResult
from src.profile import build_system

TASK = """\
TASK: Given a JOB DESCRIPTION (in the user message), produce a tailoring report.

Rules:
- match_score (0-100): weigh BOTH skill fit AND the candidate's stated scope
  preferences (company_stage, target_functions, geos, work_mode). If the role
  hits a dealbreaker or is clearly out of scope, say so in scope_fit_notes and
  score it low — be honest, do not inflate.
- strengths: specific to THIS role; cite the candidate's real numbers (ARR, MAU,
  ROAS, %, etc.). No vague claims.
- gaps: be honest about what's missing or weaker; for each, give a concrete way
  to address it (reframe an existing experience, quick upskill, or handle it in
  the cover letter).
- resume bullets: rewrite and REORDER the candidate's existing achievements to
  mirror this JD's priorities and keywords. Never fabricate. Pull metrics only
  from the profile. 5-7 bullets, each starting with a strong verb.
- cover letter: ~200 words, founder-friendly, lead with a 0-to-1 venture win,
  show she understands their stage, end with a soft call to talk.
- Provide English AND Chinese versions for summary, bullets, and cover letter.
  Chinese should read natively, not like a translation.
"""


def run(jd_text: str, profile: dict) -> TailorResult:
    system = build_system(profile, TASK)
    user = f"JOB DESCRIPTION:\n\n{jd_text}"
    return llm.generate(system, user, TailorResult)
