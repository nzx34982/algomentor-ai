import json
from prompt_builder import build_review_prompt
from llm_client import call_llm
from storage import save_review
from review_parser import parse_review_text

def read_multiline_input(prompt_text):
    """
    读取多行输入。

    输入：
        prompt_text: 提示用户输入什么内容

    输出：
        用户输入的多行文本，类型是 str

    结束方式：
        用户单独输入 END 后结束
    """
    print(prompt_text)
    print("输入完成后，单独输入 END 并回车。")

    lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        lines.append(line)

    return "\n".join(lines)


def collect_review_data():
    """
    收集一次 LeetCode 代码复盘所需的信息。

    输入：
        无，直接从终端读取用户输入

    输出：
        review_data 字典
    """
    problem_title = input("请输入 LeetCode 题目标题：").strip()

    problem_description = read_multiline_input("\n请输入题目描述：")

    user_code = read_multiline_input("\n请输入你的 Python 代码：")

    confusion = read_multiline_input("\n请输入你的困惑 / 报错信息：")

    review_data = {
        "problem_title": problem_title,
        "problem_description": problem_description,
        "user_code": user_code,
        "confusion": confusion,
    }

    return review_data


def main():
    """
    程序入口。
    当前版本负责：
    1. 收集用户输入
    2. 构造 prompt
    3. 调用大模型 API 或 mock 模式
    4. 打印模型返回的复盘文本
    5. 保存复盘记录到本地 JSON 文件
    """
    review_data = collect_review_data()

    print("\n=== 原始 review 数据 ===")
    print(json.dumps(review_data, ensure_ascii=False, indent=2))

    review_prompt = build_review_prompt(review_data)

    print("\n=== 正在调用大模型生成复盘 ===")

    review_text = call_llm(review_prompt)

    print("\n=== AI 复盘结果 ===")
    print(review_text)

    review_result = parse_review_text(review_text)

    saved_record = save_review(review_data, review_result)

    print("\n=== 已保存复盘记录 ===")
    print(f"题目：{saved_record['problem_title']}")
    print(f"时间：{saved_record['created_at']}")
    print("保存位置：data/reviews.json")


if __name__ == "__main__":
    main()