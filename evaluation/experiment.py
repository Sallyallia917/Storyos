"""Experiment 1: compare a no-prompt general model with StoryOS.

The only intended experimental variable is the presence of the StoryOS system prompt.
Both arms use the same model, temperature, API, and exact user input. Neither arm
uses JSON response mode, because that would constrain the no-prompt baseline.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import APIError, OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompts.storyos_prompt import SYSTEM_PROMPT  # noqa: E402

MODEL = "deepseek-chat"
TEMPERATURE = 0.2
OUTPUT_DIR = ROOT / "evaluation" / "outputs"
RUBRIC = [
    ("情境准确性", "是否还原主体在关键节点实际面对的局面，而非只复述背景？"),
    ("选择空间", "是否识别当时真实可行的选项，并说明可行条件与限制？"),
    ("能动性", "是否区分主体可控制、不可控制的因素及实际行动空间？"),
    ("选择机制", "是否解释主体为何这样选择，而非只贴人格标签？"),
    ("代价分析", "是否说明选择获得与失去的东西，并区分结果与代价？"),
    ("因果链", "是否解释前序选择如何改变后续情境与选择条件？"),
    ("证据可靠性", "是否区分可核验事实、推断与假设，避免虚构细节？"),
    ("选择空间变化", "是否解释选择空间如何扩大、收缩、转移或保持不变？"),
    ("分析边界遵守度", "是否避免无依据的心理、可行选项、因果和剧情补全？"),
]


def build_messages(subject: str, use_storyos: bool) -> list[dict[str, str]]:
    """Build the exact experimental inputs; baseline has no system prompt."""
    messages = []
    if use_storyos:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": subject})
    return messages


def call_model(client: OpenAI, subject: str, use_storyos: bool) -> dict[str, Any]:
    messages = build_messages(subject, use_storyos)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
        )
    except APIError as error:
        arm = "StoryOS" if use_storyos else "General"
        raise RuntimeError(f"{arm} 组 API 调用失败：{error}") from error

    content = response.choices[0].message.content or ""
    parsed_json = None
    json_valid = False
    if use_storyos:
        try:
            parsed_json = json.loads(content)
            json_valid = isinstance(parsed_json, dict)
        except json.JSONDecodeError:
            pass

    return {
        "arm": "storyos" if use_storyos else "general",
        "system_prompt_used": use_storyos,
        "user_input": subject,
        "messages": messages,
        "raw_output": content,
        "json_valid_object": json_valid if use_storyos else None,
        "parsed_output": parsed_json,
    }


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^\\w一-鿿-]+", "_", value, flags=re.UNICODE).strip("_")
    return slug[:60] or "subject"


def write_scoring_template(path: Path, subject: str) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["subject", "arm", "dimension", "score_1_to_5", "evidence_or_reason"])
        for arm in ("general", "storyos"):
            for dimension, _ in RUBRIC:
                writer.writerow([subject, arm, dimension, "", ""])


def run_subject(client: OpenAI, subject: str, run_id: str) -> Path:
    # Call the general model first, then StoryOS; preserve raw outputs for review.
    general = call_model(client, subject, use_storyos=False)
    storyos = call_model(client, subject, use_storyos=True)
    payload = {
        "experiment": "E1_general_model_vs_storyos",
        "run_id": run_id,
        "subject": subject,
        "controls": {
            "provider": "DeepSeek",
            "model": MODEL,
            "temperature": TEMPERATURE,
            "user_input_identical": True,
            "json_response_mode": False,
            "experimental_variable": "StoryOS system prompt absent vs present",
        },
        "prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest(),
        "general": general,
        "storyos": storyos,
        "interpretation_note": (
            "General 组没有 system prompt，也没有 JSON mode；StoryOS 组仅增加 StoryOS system prompt。"
            "请人工按同一量表评分。模型输出不是事实核验结果，评分应记录具体证据片段。"
        ),
    }
    output_path = OUTPUT_DIR / f"{safe_slug(subject)}_{run_id}.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    scoring_path = OUTPUT_DIR / f"{safe_slug(subject)}_{run_id}_scoring.csv"
    write_scoring_template(scoring_path, subject)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="实验一：无专属提示词的一般模型 vs StoryOS 结构化分析"
    )
    parser.add_argument(
        "subjects",
        nargs="+",
        help='一个或多个分析对象，例如："杨康" "令狐冲"',
    )
    args = parser.parse_args()
    subjects = [subject.strip() for subject in args.subjects if subject.strip()]
    if not subjects:
        parser.error("至少提供一个非空分析对象")
    if not os.getenv("DEEPSEEK_API_KEY"):
        parser.error("请先设置 DEEPSEEK_API_KEY 环境变量")

    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for subject in subjects:
        output_path = run_subject(client, subject, run_id)
        print(f"完成：{subject}")
        print(f"原始结果：{output_path}")
        print(f"评分模板：{output_path.with_name(output_path.stem + '_scoring.csv')}")


if __name__ == "__main__":
    main()
