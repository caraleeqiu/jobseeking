"""对 Claude API 的薄封装。

- 用 messages.parse 直接拿到结构化结果（Pydantic 校验）
- system 自带 prompt 缓存（在 profile.py 里打的断点）
- 默认 Opus 4.8 + 自适应思考，质量优先
"""

import os
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-8"

_client = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not os.getenv("ANTHROPIC_API_KEY"):
            sys.exit(
                "❌ 没找到 ANTHROPIC_API_KEY。\n"
                "   请把 .env.example 复制为 .env 并填入你的 API Key。"
            )
        _client = anthropic.Anthropic()
    return _client


def research(query: str, max_tokens: int = 4000) -> str:
    """联网检索公司/创始人近期动态，返回一段事实摘要（纯文本）。

    用 Claude 的服务端 web_search 工具；处理 pause_turn 续跑。
    失败时由调用方兜底（这里不抛网络异常给用户看）。
    """
    tools = [{"type": "web_search_20260209", "name": "web_search"}]
    messages = [{"role": "user", "content": query}]
    chunks: list[str] = []
    for _ in range(5):  # 服务端工具可能 pause_turn，最多续 5 次
        resp = client().messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            tools=tools,
            messages=messages,
        )
        for block in resp.content:
            if block.type == "text":
                chunks.append(block.text)
        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            continue
        break
    return "\n".join(chunks).strip()


def generate(system_blocks: list[dict], user_text: str, schema, max_tokens: int = 16000):
    """跑一次结构化生成，返回 schema 类型的实例。"""
    resp = client().messages.parse(
        model=MODEL,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        system=system_blocks,
        messages=[{"role": "user", "content": user_text}],
        output_format=schema,
    )
    if resp.parsed_output is None:
        raise RuntimeError(
            "模型没有返回符合格式的结果（可能命中安全拒答或被截断）。"
            f" stop_reason={resp.stop_reason}"
        )
    # 顺手打印缓存命中情况，方便你确认省了多少
    u = resp.usage
    cached = getattr(u, "cache_read_input_tokens", 0) or 0
    if cached:
        print(f"   （缓存命中 {cached} tokens，已省钱）", file=sys.stderr)
    return resp.parsed_output
