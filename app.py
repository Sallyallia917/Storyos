import json
import os

import streamlit as st

from core.reasoning import StoryOSReasoningError, analyze_object


st.set_page_config(page_title="StoryOS", page_icon="S", layout="centered")
st.title("StoryOS")
st.caption("AI 结构化推理 Demo")

subject = st.text_input("分析对象", placeholder="例如：杨康")

if st.button("开始分析", type="primary", disabled=not subject.strip()):
    if not os.getenv("DEEPSEEK_API_KEY"):
        st.error("请先设置 DEEPSEEK_API_KEY 环境变量。")
    else:
        with st.spinner("正在分析..."):
            try:
                result = analyze_object(subject.strip())
            except StoryOSReasoningError as error:
                st.error(str(error))
            else:
                st.subheader("结构化分析")
                st.json(result)
                st.download_button(
                    "下载 JSON",
                    data=json.dumps(result, ensure_ascii=False, indent=2),
                    file_name="storyos-analysis.json",
                    mime="application/json",
                )
