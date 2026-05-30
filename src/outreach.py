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


RESEARCH_QUERY = """\
Research this company and founder for a personalized cold outreach. Find facts
from roughly the last 6-12 months that a candidate could authentically
reference: recent funding rounds, product launches, market/geo expansion,
notable hires, and the founder's public posts or background. Return a short
bulleted brief with sources/links. If you cannot verify something, omit it —
do not guess.

Here is what the candidate already knows:
{notes}
"""


def research_company(company_notes: str) -> str:
    """联网补充公司近期动态；失败则返回空串（不影响主流程）。"""
    import sys

    try:
        brief = llm.research(RESEARCH_QUERY.format(notes=company_notes))
        if brief:
            print("   （已联网补充公司近期动态）", file=sys.stderr)
        return brief
    except Exception as e:  # 网络/权限问题不应让整个流程挂掉
        print(f"   （联网检索跳过：{e}）", file=sys.stderr)
        return ""


def run(company_notes: str, profile: dict, research_brief: str = "") -> OutreachResult:
    system = build_system(profile, TASK)
    user = f"COMPANY & FOUNDER NOTES:\n\n{company_notes}"
    if research_brief:
        user += (
            "\n\nWEB-RESEARCHED FACTS (verified online; use these too, but still "
            "do NOT invent anything beyond them):\n\n" + research_brief
        )
    return llm.generate(system, user, OutreachResult)
