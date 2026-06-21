"""岗位发现 / 推送 —— 第三条腿。

从真实招聘板（Greenhouse / Ashby）拉 100% 真实在招的 marketing/growth 岗位，
再用候选人画像逐个打分排序，输出可直接看、链接可点的推送清单。

数据源是真岗位，不会幻觉公司或链接。公司清单见 config/companies.yaml。
"""

from . import jobsource, llm
from .models import JobDiscovery
from .profile import build_system

TASK = """\
TASK: Score and rank the REAL job postings below for this candidate.

You are given a list of currently-open jobs pulled directly from company career
boards (each has a real company, role, location, and URL). For each one:
- Set company, role, location, source_url EXACTLY from the data given. Never change
  the URL or invent one.
- Score match_score 0-100 on fit: growth/marketing skill match AND the candidate's
  scope preferences (stage, function, geo, work-mode, dealbreakers in the profile).
  Sector is open — don't penalise a role for its vertical; judge the growth/marketing fit.
- why_relevant: one sharp line on why it fits (or doesn't) this candidate.
- founder_or_team: only if you genuinely know it, else 'unknown'.
- how_to_apply: specific and actionable (apply via the URL; add 'also DM founder on
  LinkedIn' when it's a small/early team worth a direct approach).
- visa_geo_flag: honest flag if the location implies onsite/work-authorization risk
  for this candidate; remote/remote-friendly → 'none'.
Sort leads by match_score descending. Include every job given (don't drop any).
"""


def run(profile: dict, focus: str = "", limit: int = 30) -> JobDiscovery:
    real_jobs = jobsource.fetch_all()
    if not real_jobs:
        # 数据源为空（网络/清单问题）时，返回空结果而不是幻觉
        return JobDiscovery(leads=[], summary="未从招聘板拉到岗位，请检查网络或 config/companies.yaml。")
    # 一次打分太多会超 token；截断到 limit 个（公司轮流取，保证多样性）
    real_jobs = real_jobs[:limit]

    lines = [
        f"{i}. company={j['company']} | role={j['role']} | location={j['location']} | url={j['url']}"
        for i, j in enumerate(real_jobs, 1)
    ]
    focus_note = f"\n\nExtra emphasis this run: {focus}" if focus else ""
    user = (
        "REAL OPEN JOBS (pulled from company career boards — use these exactly):\n\n"
        + "\n".join(lines)
        + focus_note
    )
    system = build_system(profile, TASK)
    return llm.generate(system, user, JobDiscovery, max_output_tokens=24000)
