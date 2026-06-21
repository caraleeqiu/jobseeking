#!/usr/bin/env python3
"""求职 Copilot —— 命令行入口。

用法：
  python main.py tailor   jobs/example-job.md
  python main.py outreach companies/example-company.md

产出会写到 output/ 目录下的同名 .md 文件，并在终端打印路径。
"""

import argparse
import datetime
import pathlib
import re
import sys

from src import discover, outreach, render, tailor
from src.profile import load_profile

OUTPUT_DIR = pathlib.Path("output")

# 按日期归档的三个子目录
CAT_JOB_SCAN = "01-job-scan"      # 工作轮训：摘要 + 完整 JD
CAT_TAILORED = "02-tailored"      # 简历自定义结果
CAT_APPLICATIONS = "03-applications"  # 投递结果：触达文案 + 追踪表


def _slug(path: str) -> str:
    stem = pathlib.Path(path).stem
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-") or "result"


def _read(path: str) -> str:
    p = pathlib.Path(path)
    if not p.exists():
        sys.exit(f"❌ 找不到输入文件：{path}")
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        sys.exit(f"❌ 输入文件是空的：{path}")
    return text


def _daily_dir(category: str, date: str | None = None) -> pathlib.Path:
    """返回 output/daily/<日期>/<分类>/，不存在则创建。"""
    day = date or datetime.date.today().isoformat()
    d = OUTPUT_DIR / "daily" / day / category
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write(category: str, slug: str, suffix: str, content: str, date=None) -> pathlib.Path:
    out = _daily_dir(category, date) / f"{slug}-{suffix}.md"
    out.write_text(content, encoding="utf-8")
    return out


def cmd_tailor(args):
    profile = load_profile()
    jd = _read(args.input)
    print("🔍 正在分析岗位并定制简历……", file=sys.stderr)
    result = tailor.run(jd, profile)
    md = render.render_tailor(result, _slug(args.input))
    out = _write(CAT_TAILORED, _slug(args.input), "tailored", md, args.date)
    print(f"✅ 已生成：{out}  （匹配度 {result.match_score}/100）")


def cmd_outreach(args):
    profile = load_profile()
    notes = _read(args.input)
    brief = ""
    if args.research:
        print("🌐 正在联网检索公司近期动态……", file=sys.stderr)
        brief = outreach.research_company(notes)
    print("✍️  正在撰写创始人触达……", file=sys.stderr)
    result = outreach.run(notes, profile, research_brief=brief)
    md = render.render_outreach(result, _slug(args.input))
    out = _write(CAT_APPLICATIONS, _slug(args.input), "outreach", md, args.date)
    print(f"✅ 已生成：{out}")


def cmd_discover(args):
    profile = load_profile()
    print("🛰️  正在联网搜对口岗位并打分排序……", file=sys.stderr)
    result = discover.run(profile, focus=args.focus or "")
    day = args.date or datetime.date.today().isoformat()
    md = render.render_discover(result, day)
    out = _write(CAT_JOB_SCAN, "job-push", "推送", md, args.date)
    strong = sum(1 for x in result.leads if x.match_score >= 75)
    print(f"✅ 已生成：{out}  （{len(result.leads)} 个岗位，{strong} 个强投）")


def main():
    parser = argparse.ArgumentParser(description="求职 Copilot：岗位发现 + 定制 + 触达")
    sub = parser.add_subparsers(dest="command", required=True)

    p_disc = sub.add_parser("discover", help="联网搜对口岗位 → 打分排序的推送清单")
    p_disc.add_argument("focus", nargs="?", default="", help="可选：这次重点找什么，例如 'AI 视频 远程' 或 '华人创始'")
    p_disc.add_argument("--date", help="归档日期 YYYY-MM-DD，默认今天", default=None)
    p_disc.set_defaults(func=cmd_discover)

    p_tailor = sub.add_parser("tailor", help="JD → 匹配度 + 定制简历 + 求职信")
    p_tailor.add_argument("input", help="JD 文件路径，例如 jobs/example-job.md")
    p_tailor.add_argument("--date", help="归档日期 YYYY-MM-DD，默认今天", default=None)
    p_tailor.set_defaults(func=cmd_tailor)

    p_out = sub.add_parser("outreach", help="公司+创始人信息 → 个性化触达")
    p_out.add_argument("input", help="公司信息文件路径，例如 companies/example-company.md")
    p_out.add_argument(
        "--no-research",
        dest="research",
        action="store_false",
        help="关闭联网检索，只用你手填的信息",
    )
    p_out.add_argument("--date", help="归档日期 YYYY-MM-DD，默认今天", default=None)
    p_out.set_defaults(func=cmd_outreach, research=True)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
