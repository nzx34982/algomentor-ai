import streamlit as st

from prompt_builder import build_review_prompt
from llm_client import call_llm
from review_parser import parse_review_text
from storage import save_review


def build_review_data(problem_ref, user_code, user_request):
    """
    根据前端输入构造 review_data。

    输入：
        problem_ref: LeetCode 题号或题名
        user_code: 用户代码
        user_request: 用户希望 AI 重点看的内容，可以为空

    输出：
        review_data: dict
    """
    if not user_request.strip():
        user_request = "请整体复盘我的代码，包括题意推断、思路、复杂度、潜在问题和改进建议。"

    review_data = {
        "problem_title": problem_ref.strip(),
        "problem_description": "用户未提供完整题目描述，只提供了 LeetCode 题号或题名。请结合题号、题名和代码进行合理推断；如果题目信息不足，请明确指出你的假设。",
        "user_code": user_code.strip(),
        "confusion": user_request.strip(),
    }

    return review_data


def main():
    st.set_page_config(
        page_title="AlgoMentor AI",
        page_icon="🧠",
        layout="centered",
    )

    inject_custom_css()
    st.title("AlgoMentor AI")
    st.caption("LeetCode 代码复盘助手 · V0.2")

    st.markdown(
        """
        <div class="intro-card">
        把你的 LeetCode 题目、代码和困惑贴进来。<br>
        我会帮你生成一份结构化复盘：包括问题本质、代码问题、正确思路、可优化点和下次思考步骤。
        </div>
        """,
        unsafe_allow_html=True,
    )

    problem_ref = st.text_input(
        "LeetCode 题号或题名",
        placeholder="例如：1 / Two Sum / 322 Coin Change / 198 House Robber",
    )

    user_code = st.text_area(
        "你的 Python 代码",
        placeholder="把你的 Python 解法粘贴到这里。",
        height=300,
    )

    user_request = st.text_area(
        "你想让 AI 重点看什么？可选",
        placeholder="例如：帮我看看为什么超时 / 思路是否正确 / 代码还能不能优化 / 直接整体复盘。",
        height=120,
    )

    submitted = st.button("生成复盘", type="primary")

    if submitted:
        if not problem_ref.strip():
            st.error("请至少输入 LeetCode 题号或题名。")
            return

        if not user_code.strip():
            st.error("请粘贴你的 Python 代码。")
            return

        review_data = build_review_data(
            problem_ref=problem_ref,
            user_code=user_code,
            user_request=user_request,
        )
        review_prompt = build_review_prompt(review_data)

        with st.spinner("正在调用大模型生成复盘..."):
            review_text = call_llm(review_prompt)

        review_result = parse_review_text(review_text)

        saved_record = save_review(review_data, review_result)

        st.success("复盘已生成并保存。")

        st.subheader("AI 复盘结果")
        st.markdown(review_result["raw_text"])

        with st.expander("查看本次保存的数据"):
            st.json(saved_record)
def inject_custom_css():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 860px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        h1 {
            text-align: center;
            font-size: 2.4rem;
            margin-bottom: 0.2rem;
        }

        [data-testid="stCaptionContainer"] {
            text-align: center;
        }

        .intro-card {
            background: #f8f9fa;
            padding: 1.1rem 1.3rem;
            border-radius: 16px;
            border: 1px solid #e9ecef;
            margin: 1.5rem 0 1.8rem 0;
            line-height: 1.7;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 1.2rem;
            margin-bottom: 0.4rem;
        }

        textarea {
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
        }

        .stButton > button {
            width: 100%;
            border-radius: 999px;
            height: 3rem;
            font-weight: 700;
            font-size: 1rem;
        }

        .result-card {
            background: #ffffff;
            padding: 1.2rem 1.4rem;
            border-radius: 16px;
            border: 1px solid #e9ecef;
            margin-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()