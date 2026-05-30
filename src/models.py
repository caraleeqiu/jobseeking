"""结构化输出的数据模型（Pydantic）。

这些类定义了 Claude 必须返回的字段。所有字段都是必填，
工具会用它们渲染成最终的 Markdown 报告。
"""

from pydantic import BaseModel, Field


# ---------- 腿 A：岗位定制 ----------

class GapItem(BaseModel):
    gap: str = Field(description="A real gap between the candidate and this role")
    how_to_address: str = Field(
        description="Concrete way to address it: reframe, upskill, or handle in the cover letter"
    )


class TailorResult(BaseModel):
    match_score: int = Field(description="0-100 fit score, factoring skills AND scope preferences")
    match_verdict: str = Field(description="One-line verdict on whether to pursue this role")
    scope_fit_notes: str = Field(
        description="How the role aligns with the candidate's stage/function/geo/work-mode preferences; flag any dealbreakers"
    )
    strengths: list[str] = Field(description="Concrete strengths for THIS role, citing real metrics")
    gaps: list[GapItem] = Field(description="Honest gaps with how to address each")
    tailored_summary_en: str = Field(description="A tailored professional summary, English")
    tailored_summary_cn: str = Field(description="A tailored professional summary, Chinese")
    resume_bullets_en: list[str] = Field(description="5-7 rewritten/reordered resume bullets for this JD, English")
    resume_bullets_cn: list[str] = Field(description="5-7 rewritten/reordered resume bullets for this JD, Chinese")
    cover_letter_en: str = Field(description="~200-word founder-friendly cover letter, English")
    cover_letter_cn: str = Field(description="Cover letter, Chinese")


# ---------- 腿 B：创始人触达 ----------

class OutreachResult(BaseModel):
    company_angle: str = Field(description="What to reference about the company to show genuine homework")
    pain_point_hypothesis: str = Field(description="A specific marketing/growth pain this company likely has")
    why_her: str = Field(description="Why this candidate is uniquely positioned to solve it")
    subject_lines: list[str] = Field(description="3 short, high-open-rate email subject lines")
    email_en: str = Field(description="Personalized cold outreach email to the founder, English")
    email_cn: str = Field(description="Cold outreach email, Chinese")
    linkedin_dm_en: str = Field(description="Short LinkedIn DM (<60 words), English")
    linkedin_dm_cn: str = Field(description="Short LinkedIn DM, Chinese")
