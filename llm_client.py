import os

from openai import OpenAI, RateLimitError, APIError


def call_llm(prompt):
    """
    调用大模型 API，返回模型生成的文本。

    支持三种模式：
    1. mock：不调用真实 API，返回模拟结果
    2. deepseek：调用 DeepSeek API
    3. openai：调用 OpenAI API
    """
    if get_config_value("ALGOMENTOR_MOCK_LLM", "0") == "1":
        return mock_llm_response()

    provider = get_config_value("ALGOMENTOR_LLM_PROVIDER", "deepseek").lower()
    if provider == "deepseek":
        return call_deepseek(prompt)

    if provider == "openai":
        return call_openai(prompt)

    raise ValueError(f"不支持的 LLM provider: {provider}")
def get_config_value(name, default=None):
    """
    优先从环境变量读取配置；
    如果没有，再尝试从 Streamlit secrets 读取。
    """
    value = os.getenv(name)

    if value:
        return value

    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]

    except Exception:
        pass

    return default

def call_deepseek(prompt):
    """
    调用 DeepSeek API。

    输入：
        prompt: str，发给模型的提示词

    输出：
        模型返回的文本
    """
    api_key = get_config_value("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("没有找到 DEEPSEEK_API_KEY，请先设置 DeepSeek API Key。")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    except RateLimitError as error:
        raise RuntimeError(
            "DeepSeek API 当前可能额度不足、请求过多，或账户计费不可用。"
        ) from error

    except APIError as error:
        raise RuntimeError(
            f"DeepSeek API 调用失败：{error}"
        ) from error


def call_openai(prompt):
    """
    调用 OpenAI API。

    输入：
        prompt: str，发给模型的提示词

    输出：
        模型返回的文本
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("没有找到 OPENAI_API_KEY，请先设置 OpenAI API Key。")

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    except RateLimitError as error:
        raise RuntimeError(
            "OpenAI API 当前没有可用额度，或计费尚未开通。"
        ) from error

    except APIError as error:
        raise RuntimeError(
            f"OpenAI API 调用失败：{error}"
        ) from error


def mock_llm_response():
    """
    返回模拟的 AI 复盘结果。

    用于没有 API Key 或没有额度时继续开发项目。
    """
    return """
## 1. 问题本质

这里是模拟的 AI 复盘结果。真实 API 暂时没有调用。

## 2. 我的代码问题

这里会分析你的代码可能存在的问题。

## 3. 正确解法思路

这里会解释更好的算法思路。

## 4. 可改进的 Python 代码

这里未来会给出改进代码。

## 5. 我应该记住的算法模型

这里会总结对应的算法模型。

## 6. 下次遇到类似题目的思考步骤

这里会给出下一次做题的思考流程。
""".strip()