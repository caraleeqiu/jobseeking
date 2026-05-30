"""对 Google Gemini API 的薄封装。

- 用 response_schema 直接拿到结构化结果（Pydantic 校验）
- 联网检索用 Google Search grounding
- 默认 gemini-2.5-flash（性价比高）；可用环境变量 GEMINI_MODEL 改成 gemini-2.5-pro
"""

import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_client = None


def client() -> "genai.Client":
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            sys.exit(
                "❌ 没找到 GEMINI_API_KEY。\n"
                "   请把 .env.example 复制为 .env 并填入你的 Google API Key。"
            )
        _client = genai.Client(api_key=key)
    return _client


def research(query: str, max_output_tokens: int = 4000) -> str:
    """用 Google Search grounding 联网检索，返回一段事实摘要（纯文本）。"""
    resp = client().models.generate_content(
        model=MODEL,
        contents=query,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            max_output_tokens=max_output_tokens,
        ),
    )
    return (resp.text or "").strip()


def generate(system_text: str, user_text: str, schema, max_output_tokens: int = 16000):
    """跑一次结构化生成，返回 schema 类型的实例。"""
    resp = client().models.generate_content(
        model=MODEL,
        contents=user_text,
        config=types.GenerateContentConfig(
            system_instruction=system_text,
            response_mime_type="application/json",
            response_schema=schema,
            max_output_tokens=max_output_tokens,
        ),
    )
    parsed = resp.parsed
    if parsed is None:
        raise RuntimeError(
            "模型没有返回符合格式的结果（可能被截断或命中安全过滤）。"
            f" finish_reason={getattr(resp.candidates[0], 'finish_reason', '?') if resp.candidates else '?'}"
        )
    return parsed
