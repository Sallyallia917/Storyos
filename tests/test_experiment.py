from evaluation.experiment import build_messages, safe_slug


def test_general_arm_has_no_system_prompt():
    assert build_messages("杨康", use_storyos=False) == [
        {"role": "user", "content": "杨康"}
    ]


def test_storyos_arm_only_adds_system_prompt():
    messages = build_messages("杨康", use_storyos=True)
    assert messages[0]["role"] == "system"
    assert "StoryOS Reasoning Engine" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "杨康"}


def test_both_arms_keep_exact_same_user_input():
    general = build_messages("令狐冲", use_storyos=False)
    storyos = build_messages("令狐冲", use_storyos=True)
    assert general[-1]["content"] == storyos[-1]["content"]


def test_safe_slug():
    assert safe_slug("杨康") == "杨康"
    assert safe_slug("../杨康/") == "杨康"
