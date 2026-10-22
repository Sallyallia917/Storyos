from core.reasoning import OUTPUT_SCHEMA, _get_system_prompt, _validate_result, StoryOSReasoningError
from prompts.storyos_prompt import BASELINE_SYSTEM_PROMPT, SYSTEM_PROMPT_V03


def minimal_valid_result():
    return {
        "object": "测试对象",
        "object_type": "Character",
        "system": {
            "era_context": None,
            "institutions_rules": [],
            "organization_structure": [],
            "power_resource_relations": [],
            "social_constraints": [],
        },
        "decision_cycles": [
            {
                "context": "证据不足",
                "constraints": [],
                "choice_space": [],
                "agency": {
                    "level": None,
                    "can_control": [],
                    "cannot_control": [],
                    "actual_use": None,
                },
                "desire": [],
                "fear": [],
                "choice": None,
                "choice_reason": None,
                "cost": [],
                "new_context": None,
                "choice_space_change": {"direction": None, "reason": None},
            }
        ],
        "overall_trajectory": None,
        "evidence": [],
    }


def test_v03_prompt_adds_evidence_guardrails():
    assert len(SYSTEM_PROMPT_V03) > len(BASELINE_SYSTEM_PROMPT)
    assert "可行性结论" in SYSTEM_PROMPT_V03
    assert "事实、推断、假设" in SYSTEM_PROMPT_V03


def test_prompt_version_switch():
    import os
    os.environ["STORYOS_PROMPT_VERSION"] = "baseline"
    assert _get_system_prompt() == BASELINE_SYSTEM_PROMPT
    os.environ["STORYOS_PROMPT_VERSION"] = "v03"
    assert _get_system_prompt() == SYSTEM_PROMPT_V03
    os.environ.pop("STORYOS_PROMPT_VERSION", None)


def test_schema_allows_unknown_nulls_and_empty_choice_space():
    _validate_result(minimal_valid_result())


def test_schema_rejects_wrong_type():
    data = minimal_valid_result()
    data["decision_cycles"] = "not-a-list"
    try:
        _validate_result(data)
    except StoryOSReasoningError:
        return
    raise AssertionError("Expected invalid result to be rejected")
