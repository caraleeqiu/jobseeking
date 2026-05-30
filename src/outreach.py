"""腿 B：给一家公司 + 创始人信息，生成个性化创始人触达。"""

from src import llm
from src.models import OutreachResult
from src.profile import build_system

TASK = """\
TASK: Given notes about a COMPANY and its FOUNDER (in the user message), write a
highly personalized cold outreach to the founder. The candidate prefers reaching
out to founders directly rather than applying through ATS.

Rules:
- company_angle: reference something specific and real from the notes (recent
  raise, launch, market, hire). If the notes are thin, work only with what's
  given — do NOT invent news or facts.
- pain_point_hypothesis: name a concrete growth/marketing pain a company at this
  stage likely faces, that the candidate can own.
- why_her: tie her real 0-to-1 wins / market experience / AI-leverage to that
  pain. Be specific, not flattering.
- email: short (120-160 words), no fluff, no "I came across your company".
  Open with the angle, land the value, one clear ask (a 15-min chat). Sound like
  a peer operator, not a job applicant.
- subject_lines: 3 short ones that a busy founder would actually open.
- linkedin_dm: under 60 words, even punchier than the email.
- Provide English AND Chinese versions. Chinese should read natively.
"""


def run(company_notes: str, profile: dict) -> OutreachResult:
    system = build_system(profile, TASK)
    user = f"COMPANY & FOUNDER NOTES:\n\n{company_notes}"
    return llm.generate(system, user, OutreachResult)
