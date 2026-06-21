"""岗位发现 / 推送 —— 第三条腿。

给定候选人画像，联网搜符合赛道+偏好的真实在招岗位，
用画像打分排序，输出一份可直接看的岗位推送清单。

流程：
1. research()：用 Google Search grounding 联网捞一批真实公司/岗位线索（纯文本）。
2. generate()：把线索 + 画像喂给模型，结构化成打分排序的 JobDiscovery。
"""

from . import llm
from .models import JobDiscovery
from .profile import build_system

# 联网检索的提示词：让 grounding 去捞真实、在招、对口的岗位
SEARCH_QUERY = """\
Find REAL, currently-open job postings (2026) that fit this candidate.

Candidate in one line: {headline}
Target functions: {functions}
Target sectors: AI video / image / creative / companion / music / creator tools /
AI education, plus consumer AI products with overseas/global expansion.
Preferred: startups Series A+, remote or remote-friendly, founder-reachable.
Also surface Chinese-founded teams going global (ex-ByteDance / TikTok / CapCut lineage).

Extra focus from the user this run: {focus}

For each opportunity, find: company, role title, what they do, location/remote policy,
founder or team background, and how to apply (careers page, LinkedIn, or founder DM).
Prefer companies actively hiring growth/marketing. Return concrete names and URLs,
not generic advice. Aim for 8-12 distinct, real opportunities.
"""

TASK = """\
TASK: From the web-research notes below, produce a ranked job-discovery list for the candidate.

Rules:
- Only include REAL companies named in the notes. Do NOT invent companies or roles.
- Score each 0-100 on fit, factoring BOTH skill match AND the candidate's scope
  preferences (stage, function, geo, work-mode, dealbreakers in the profile).
- Be honest in visa_geo_flag: if a role is US-onsite or needs work authorization the
  candidate may lack, say so. Remote/relocation-friendly or Chinese-team roles → 'none'.
- Sort leads by match_score descending.
- how_to_apply must be specific and actionable for THIS candidate.
"""


def run(profile: dict, focus: str = "") -> JobDiscovery:
    system = build_system(profile, TASK)
    headline = profile.get("headline", "Growth / founding marketing leader, AI products")
    prefs = profile.get("preferences", {})
    functions = ", ".join(prefs.get("target_functions", ["Growth Marketing"]))

    notes = llm.research(
        SEARCH_QUERY.format(
            headline=headline,
            functions=functions,
            focus=focus or "(none — use the full target list)",
        )
    )
    user = (
        "WEB-RESEARCH NOTES (real companies/roles found online):\n\n"
        + (notes or "(research returned empty; rely on nothing and return an empty list)")
    )
    return llm.generate(system, user, JobDiscovery)
