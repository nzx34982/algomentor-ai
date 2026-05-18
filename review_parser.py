def parse_review_text(review_text):
    """
    解析大模型返回的复盘文本。

    当前版本先不做复杂解析，只把原始文本包装成字典。
    以后可以在这里拆分：
    - 问题本质
    - 我的代码问题
    - 正确解法思路
    - 可改进代码
    - 算法模型总结

    输入：
        review_text: str，大模型返回的原始复盘文本

    输出：
        review_result: dict，结构化后的复盘结果
    """
    review_result = {
        "raw_text": review_text
    }

    return review_result