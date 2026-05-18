def build_review_prompt(review_data):
    """
    根据用户提交的 LeetCode 复盘信息，构造发给大模型的 prompt。

    输入：
        review_data: dict，包含题目标题、题目描述、用户代码、困惑信息

    输出：
        prompt: str，发给大模型的完整提示词
    """
    problem_title = review_data["problem_title"]
    problem_description = review_data["problem_description"]
    user_code = review_data["user_code"]
    confusion = review_data["confusion"]

    prompt = f"""
你是我的 LeetCode 代码复盘教练。

请你根据我提供的题目、代码和困惑，帮我进行一次结构化复盘。
你的目标不是直接给我灌输答案，而是帮我理解：
1. 这道题的本质是什么
2. 我的代码哪里有问题
3. 正确思路是怎么来的
4. 我应该沉淀什么算法模型

请使用中文回答，并尽量用适合大二计算机学生理解的方式解释。

【题目标题】
{problem_title}

【题目描述】
{problem_description}

【我的 Python 代码】
```python
{user_code}

【我的困惑 / 报错信息】
{confusion}

请按照下面结构输出：

1. 问题本质
2. 我的代码问题
3. 正确解法思路
4. 可改进的 Python 代码
5. 我应该记住的算法模型
6. 下次遇到类似题目的思考步骤

"""
    return prompt.strip()