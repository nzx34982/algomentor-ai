from datetime import datetime

import streamlit as st
from prompt_builder import build_review_prompt
from llm_client import call_llm
from review_parser import parse_review_text
from storage import save_review, load_reviews


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
def format_created_at(created_at):
    """
    把 ISO 时间字符串转换成更适合展示的格式。

    例如：
        2026-05-18T18:22:13 -> 05/18 18:22
    """
    try:
        dt = datetime.fromisoformat(created_at)
        return dt.strftime("%m/%d %H:%M")
    except (TypeError, ValueError):
        return "未知时间"


def shorten_text(text, max_length=12):
    """
    缩短过长的标题，避免侧边栏显示成两行。
    """
    text = str(text).strip()

    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


def build_history_label(record, index):
    """
    构造侧边栏里的历史记录显示文本。
    """
    problem_title = record.get("problem_title", "未知题目")
    created_at = record.get("created_at", "")

    short_title = shorten_text(problem_title, max_length=12)
    display_time = format_created_at(created_at)

    return f"{index}. {short_title} · {display_time}"


def render_recent_reviews():
    """
    在侧边栏展示最近几条历史复盘记录，并返回用户选中的记录。

    输出：
        selected_record: dict 或 None
    """
    st.sidebar.title("历史复盘")

    reviews = load_reviews()

    if not reviews:
        st.sidebar.caption("暂无历史复盘记录。")
        return None

    recent_reviews = list(reversed(reviews[-8:]))

    options = ["new"]
    record_id_to_record = {}

    label_by_id = {
        "new": "＋ 新建复盘"
    }

    for index, record in enumerate(recent_reviews, start=1):
        record_id = record.get("id")

        if not record_id:
            record_id = f"legacy-{index}"

        record_id_to_record[record_id] = record
        options.append(record_id)
        label_by_id[record_id] = build_history_label(record, index)

    selected_id = st.sidebar.selectbox(
        "选择模式",
        options,
        index=0,
        format_func=lambda option_id: label_by_id.get(option_id, "未知记录"),
        key="history_selector",
    )

    if selected_id == "new":
        return None

    return record_id_to_record[selected_id]



def render_selected_review(selected_record):
    """
    在主页面展示用户选中的历史复盘记录。
    """
    if selected_record is None:
        return

    problem_title = selected_record.get("problem_title", "未知题目")
    created_at = selected_record.get("created_at", "未知时间")
    display_time = format_created_at(created_at)

    user_code = selected_record.get("user_code", "")
    confusion = selected_record.get("confusion", "")

    review = selected_record.get("review", {})
    raw_text = review.get("raw_text", "")

    st.subheader(problem_title)
    st.caption(f"历史复盘 · {display_time}")

    if confusion:
        st.markdown("**当时的复盘需求**")
        st.info(confusion)

    if user_code:
        with st.expander("查看当时提交的代码"):
            st.code(user_code, language="python")

    st.markdown("### 完整复盘内容")

    if raw_text:
        st.markdown(raw_text)
    else:
        st.warning("这条记录没有找到完整复盘内容。")

    st.divider()

def main():
    st.set_page_config(
        page_title="AlgoMentor AI",
        page_icon="🧠",
        layout="centered",
    )

    inject_custom_css()
    selected_record = render_recent_reviews()
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

    if selected_record is not None:
        render_selected_review(selected_record)
        return

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
'''
$env:ALGOMENTOR_MOCK_LLM = "0"
$env:ALGOMENTOR_LLM_PROVIDER = "deepseek"
$env:DEEPSEEK_API_KEY = "sk-7b1dd104153a48eb88d3969491105db8"
'''