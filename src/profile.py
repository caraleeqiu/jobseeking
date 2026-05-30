"""加载求职画像，并构建可被 prompt 缓存的 system 上下文。

画像内容稳定、体积较大，放进 system 并打 cache 断点，
这样反复处理多个岗位时能命中缓存、省钱省时间。
"""

import pathlib

import yaml

DEFAULT_PROFILE_PATH = "config/profile.yaml"

PERSONA = (
    "You are an elite career strategist and copywriter who places senior "
    "growth and founding-marketing leaders into startups (Series A and beyond). "
    "You write tight, specific, founder-facing copy. You never invent facts, "
    "metrics, or employers beyond the candidate profile provided. You optimize "
    "for the candidate getting a reply from a founder, not for sounding generic."
)


def load_profile(path: str = DEFAULT_PROFILE_PATH) -> dict:
    p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"找不到画像文件 {path}。请先把 config/profile.example.yaml "
            f"复制为 config/profile.yaml 并填写你的信息。"
        )
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _profile_text(profile: dict) -> str:
    # sort_keys=False 保持顺序稳定，利于缓存命中
    return yaml.safe_dump(profile, allow_unicode=True, sort_keys=False)


def build_system(profile: dict, task_instructions: str) -> str:
    """拼成 system instruction：人设 + 画像 + 任务说明。

    画像稳定且较大，Gemini 2.5 会对重复前缀做隐式缓存，多个岗位连跑能省。
    """
    return (
        PERSONA
        + "\n\nCANDIDATE PROFILE (authoritative source of truth):\n\n"
        + _profile_text(profile)
        + "\n\n"
        + task_instructions
    )
