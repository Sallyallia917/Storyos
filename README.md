# StoryOS

StoryOS 是一个最小可运行的 AI 结构化推理 Demo。用户输入分析对象后，应用调用 DeepSeek API，按照 StoryOS 的核心链路生成结构化 JSON 分析。分析对象可以是 Character、Organization 或 Social Event；核心关注主体在系统中的选择空间、能动性、选择及其代价如何形成下一轮情境，而非普通人物简介。

## 环境要求

- Python 3.10+
- DeepSeek API Key

## 安装与运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
streamlit run app.py
```

Windows PowerShell 可使用 `$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"` 设置环境变量。

## 使用方式

在页面中输入一个分析对象，例如“杨康”，点击“开始分析”。分析结果会按固定字段以 JSON 展示，并可下载为 JSON 文件。每轮决策都描述当时可执行的选择及其因果后果，系统分析覆盖时代背景、制度规则、组织结构、权力资源关系和社会约束。

模型默认使用 `deepseek-chat`，API 地址为 `https://api.deepseek.com`。API Key 通过 `DEEPSEEK_API_KEY` 环境变量读取，不要提交密钥。
