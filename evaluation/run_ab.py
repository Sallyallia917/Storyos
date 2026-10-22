"""Run a same-input A/B comparison of StoryOS baseline and v0.3 prompts.

Usage:
    python evaluation/run_ab.py "杨康"

Each run calls the model twice and saves both raw JSON results to
 evaluation/outputs/ab_latest.json. This script does not assign quality scores.
"""
import json
import os
from pathlib import Path

from core.reasoning import analyze_object

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evaluation" / "outputs" / "ab_latest.json"


def run_version(subject: str, version: str) -> dict:
    os.environ["STORYOS_PROMPT_VERSION"] = version
    return analyze_object(subject)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Compare StoryOS baseline vs v0.3")
    parser.add_argument("subject", help="同一分析对象，例如：杨康")
    args = parser.parse_args()
    subject = args.subject.strip()
    if not subject:
        parser.error("分析对象不能为空")

    original_version = os.environ.get("STORYOS_PROMPT_VERSION")
    try:
        baseline = run_version(subject, "baseline")
        v03 = run_version(subject, "v03")
    finally:
        if original_version is None:
            os.environ.pop("STORYOS_PROMPT_VERSION", None)
        else:
            os.environ["STORYOS_PROMPT_VERSION"] = original_version

    payload = {
        "subject": subject,
        "comparison": "same subject; baseline prompt vs StoryOS v0.3 addendum",
        "model": "deepseek-chat",
        "temperature": 0.2,
        "baseline": baseline,
        "v03": v03,
        "scoring_note": "本文件只保存原始输出，不代表自动评分；请按 evaluation/README.md 统一量表人工复核。",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"对比结果已保存：{OUTPUT}")
    print("输出版本：baseline、v03；请按 evaluation/README.md 逐项评分。")


if __name__ == "__main__":
    main()
