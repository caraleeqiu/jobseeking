"""把结构化结果渲染成易读的 Markdown 报告。"""

from src.models import OutreachResult, TailorResult


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {x}" for x in items)


def render_tailor(r: TailorResult, source: str) -> str:
    score_bar = "🟢" if r.match_score >= 75 else "🟡" if r.match_score >= 50 else "🔴"
    gaps = "\n".join(f"- **{g.gap}** — {g.how_to_address}" for g in r.gaps)
    return f"""# 岗位定制报告 · {source}

## {score_bar} 匹配度：{r.match_score}/100
**{r.match_verdict}**

### 范围契合 / 是否值得投
{r.scope_fit_notes}

### 你的优势（针对这个岗位）
{_bullets(r.strengths)}

### 差距 & 怎么补
{gaps}

---

## ✍️ 定制简历要点

### Summary (EN)
{r.tailored_summary_en}

### 个人简介 (中文)
{r.tailored_summary_cn}

### Resume bullets (EN)
{_bullets(r.resume_bullets_en)}

### 简历要点 (中文)
{_bullets(r.resume_bullets_cn)}

---

## 💌 求职信

### Cover Letter (EN)
{r.cover_letter_en}

### 求职信 (中文)
{r.cover_letter_cn}
"""


def render_outreach(r: OutreachResult, source: str) -> str:
    subjects = _bullets(r.subject_lines)
    return f"""# 创始人触达 · {source}

### 切入点（公司功课）
{r.company_angle}

### 痛点假设
{r.pain_point_hypothesis}

### 为什么是你
{r.why_her}

---

## ✉️ 邮件

**Subject lines:**
{subjects}

### Email (EN)
{r.email_en}

### 邮件 (中文)
{r.email_cn}

---

## 💬 LinkedIn DM

### EN
{r.linkedin_dm_en}

### 中文
{r.linkedin_dm_cn}
"""
