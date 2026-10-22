# StoryOS

StoryOS 是一个最小可运行的 AI 结构化推理 Demo。用户输入分析对象后，应用调用 DeepSeek API，按照 StoryOS 的核心链路生成结构化 JSON 分析。核心关注主体在特定系统中的选择空间、能动性、选择及其代价如何形成下一轮情境，而非普通人物简介。

## 环境与运行

要求 Python 3.10+ 和 DeepSeek API Key。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
streamlit run app.py
```

Windows PowerShell：`$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"`。

## 实验一：一般模型 vs StoryOS

### 研究问题

在相同模型和相同输入下，加入 StoryOS 规范化分析框架，是否能提升对主体情境、选择空间、能动性、选择机制、代价及选择轨迹的分析质量？

### 对照设计

- **A 组 General**：不传入 system prompt；用户消息就是分析对象本身，例如 `杨康`。
- **B 组 StoryOS**：使用项目中的 `prompts/storyos_prompt.py` 作为 system prompt；用户消息仍是完全相同的分析对象。
- 两组使用相同的 DeepSeek 模型、temperature=0.2 和 API。
- 两组均不启用 JSON response mode，避免额外格式约束影响 A 组。StoryOS 依靠自身 Prompt 要求输出 JSON；如输出不合法，结果仍会保存并记录。
- 每个对象调用两次 API。脚本不自动判定哪组更好，也不自动生成结论。

### 运行

单个对象：

```bash
python evaluation/experiment.py "杨康"
```

多个对象（每个对象各调用两次 API）：

```bash
python evaluation/experiment.py "杨康" "令狐冲" "桑维翰"
```

脚本会在 `evaluation/outputs/` 下保存带 UTC 时间标记的 JSON 原始结果和 CSV 人工评分模板，不会覆盖同一对象之前的结果。输出目录是运行产物，不应提交到 Git。

### 人工评分

对同一个对象的 General 和 StoryOS 输出分别评分。每项 1–5 分，并摘录支持评分的具体文本；没有证据支持的判断应扣分。建议使用以下九个维度：

| 维度 | 评分关注点 |
|---|---|
| 情境准确性 | 是否还原主体在关键节点实际面对的局面，而非只复述背景 |
| 选择空间 | 是否识别当时真实可行的选项，并说明可行条件与限制 |
| 能动性 | 是否区分主体可控制、不可控制的因素及实际行动空间 |
| 选择机制 | 是否解释主体为何这样选择，而非只贴人格标签 |
| 代价分析 | 是否说明选择获得与失去的东西，并区分结果与代价 |
| 因果链 | 是否解释前序选择如何改变后续情境与选择条件 |
| 证据可靠性 | 是否区分可核验事实、推断与假设，避免虚构细节 |
| 选择空间变化 | 是否解释选择空间如何扩大、收缩、转移或保持不变 |
| 分析边界遵守度 | 是否避免无依据的心理、可行选项、因果和剧情补全 |

总分可按九项平均分或总分（满分 45）呈现；报告中需注明采用的口径。不要把输出更长、格式更规整直接视为质量更高。StoryOS 输出结构更复杂是设计结果，评分应聚焦分析质量和证据，而非字段数量。

### 实验边界

- 这是提示词框架的初步对照，不等于证明 StoryOS 对所有模型、任务或领域普遍更优。
- 模型输出可能有随机波动；重要案例可在相同条件下重复 2–3 次。
- 事实、来源、历史剧情需独立核验；模型生成的 evidence 字段本身不等于可靠来源。
- 旧版 V0.2.2 vs V0.3 属于不同的迭代实验，不应与本实验混用。
- 原始输出、人工评分和事实核验记录应分开保存，以便复核。

## 测试

```bash
pip install pytest
pytest -q
``
