"""真实岗位数据源 —— 从公司公开招聘板 API 拉真实在招岗位。

支持 Greenhouse 和 Ashby（覆盖绝大多数 AI 创业公司）。
拉回来的全是真岗位、带真链接，不会幻觉。

公司清单在 config/companies.yaml 里维护，格式：
  greenhouse: [heygen, ...]   # board token
  ashby: [photoroom, ...]     # job board name
"""

import json
import pathlib
import urllib.request

import yaml

COMPANIES_PATH = "config/companies.yaml"

# 只保留增长/营销相关岗位的关键词（标题命中任一即保留）
MARKETING_KEYWORDS = [
    "growth", "marketing", "marketer", "demand", "acquisition", "lifecycle",
    "brand", "content", "community", "creator", "social", "seo", "performance",
    "gtm", "go-to-market", "partnerships", "影响", "增长", "营销", "运营",
]

# 负向过滤：标题命中这些则排除（工程/设计/招聘/销售等，虽带 growth 等词但不是 mkt 岗）
EXCLUDE_KEYWORDS = [
    "engineer", "designer", "developer", "recruiter", "sourcer", "intern",
    "account executive", "compliance", "data scientist", "analyst",
    "software", "swe", "design engineer",
]


def _get(url: str, timeout: int = 15) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _is_marketing(title: str) -> bool:
    t = title.lower()
    if any(k in t for k in EXCLUDE_KEYWORDS):
        return False
    return any(k in t for k in MARKETING_KEYWORDS)


def from_greenhouse(token: str) -> list[dict]:
    """从 Greenhouse 公开 board API 拉岗位。"""
    data = _get(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs")
    if not data:
        return []
    out = []
    for j in data.get("jobs", []):
        title = j.get("title", "")
        if not _is_marketing(title):
            continue
        out.append({
            "company": token,
            "role": title,
            "location": (j.get("location") or {}).get("name", "?"),
            "url": j.get("absolute_url", ""),
        })
    return out


def from_ashby(name: str) -> list[dict]:
    """从 Ashby 公开 job-board API 拉岗位。"""
    data = _get(f"https://api.ashbyhq.com/posting-api/job-board/{name}")
    if not data:
        return []
    out = []
    for j in data.get("jobs", []):
        title = j.get("title", "")
        if not _is_marketing(title):
            continue
        out.append({
            "company": name,
            "role": title,
            "location": j.get("locationName") or j.get("location") or "?",
            "url": j.get("jobUrl") or j.get("applyUrl") or "",
        })
    return out


def load_companies(path: str = COMPANIES_PATH) -> dict:
    p = pathlib.Path(path)
    if not p.exists():
        return {"greenhouse": [], "ashby": []}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def fetch_all(path: str = COMPANIES_PATH) -> list[dict]:
    """从清单里所有公司拉真实 marketing/growth 岗位，去重返回。"""
    cfg = load_companies(path)
    jobs: list[dict] = []
    for token in cfg.get("greenhouse", []) or []:
        jobs.extend(from_greenhouse(token))
    for name in cfg.get("ashby", []) or []:
        jobs.extend(from_ashby(name))
    # 按 (company, role) 去重
    seen, uniq = set(), []
    for j in jobs:
        key = (j["company"].lower(), j["role"].lower())
        if key not in seen:
            seen.add(key)
            uniq.append(j)
    return _interleave(uniq)


def _interleave(jobs: list[dict]) -> list[dict]:
    """各公司轮流取，避免前几家公司占满名额。"""
    by_co: dict[str, list[dict]] = {}
    for j in jobs:
        by_co.setdefault(j["company"], []).append(j)
    out, buckets = [], list(by_co.values())
    i = 0
    while any(buckets):
        b = buckets[i % len(buckets)]
        if b:
            out.append(b.pop(0))
        i += 1
        if i % len(buckets) == 0:
            buckets = [b for b in buckets if b]
            i = 0
    return out
