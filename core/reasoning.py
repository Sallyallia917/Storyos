import json
import os
from typing import Any

from openai import APIError, OpenAI

from prompts.storyos_prompt import SYSTEM_PROMPT


OUTPUT_SCHEMA = {
    "object": str,
    "object_type": str,
    "system": {
        "era_context": str,
        "institutions_rules": [str],
        "organization_structure": [str],
        "power_resource_relations": [str],
        "social_constraints": [str],
    },
    "decision_cycles": [
        {
            "context": str,
            "constraints": [str],
            "choice_space": [
                {
                    "option": str,
                    "why_possible": str,
                    "risk": str,
                    "cost": str,
                }
            ],
            "agency": {
                "level": str,
                "can_control": [str],
                "cannot_control": [str],
                "actual_use": str,
            },
            "desire": [str],
            "fear": [str],
            "choice": str,
            "choice_reason": str,
            "cost": [str],
            "new_context": str,
            "choice_space_change": {
                "direction": str,
                "reason": str,
            },
        }
    ],
    "overall_trajectory": str,
    "evidence": [
        {
            "fact": str,
            "source": str,
            "supports": str,
        }
    ],
}


class StoryOSReasoningError(Exception):
    """Raised when the model call or its structured response fails."""


def analyze_story(subject: str) -> dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise StoryOSReasoningError("未设置 DEEPSEEK_API_KEY 环境变量。")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请分析以下对象：{subject}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    except APIError as error:
        raise StoryOSReasoningError(f"DeepSeek API 调用失败：{error}") from error

    content = response.choices[0].message.content
    if not content:
        raise StoryOSReasoningError("模型未返回内容，请稍后重试。")

    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise StoryOSReasoningError("模型返回的内容不是有效 JSON。") from error

    _validate_result(result)
    return result


analyze_object = analyze_story


def _validate_result(result: Any) -> None:
    _validate_value(result, OUTPUT_SCHEMA, "顶层")


def _validate_value(value: Any, schema: Any, path: str) -> None:
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            raise StoryOSReasoningError(f"模型返回字段类型不正确：{path} 必须是对象。")

        expected_fields = schema.keys()
        missing_fields = expected_fields - value.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise StoryOSReasoningError(f"模型返回缺少必要字段：{path}.{fields}")

        extra_fields = value.keys() - expected_fields
        if extra_fields:
            fields = ", ".join(sorted(extra_fields))
            raise StoryOSReasoningError(f"模型返回了未定义字段：{path}.{fields}")

        for field, field_schema in schema.items():
            _validate_value(value[field], field_schema, f"{path}.{field}")
        return

    if isinstance(schema, list):
        if not isinstance(value, list):
            raise StoryOSReasoningError(f"模型返回字段类型不正确：{path} 必须是数组。")

        item_schema = schema[0]
        for index, item in enumerate(value):
            _validate_value(item, item_schema, f"{path}[{index}]")
        return

    if not isinstance(value, schema):
        expected_type = schema.__name__
        raise StoryOSReasoningError(
            f"模型返回字段类型不正确：{path} 必须是 {expected_type}。"
        )