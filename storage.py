import json
from datetime import datetime
from pathlib import Path


def save_review(review_data, review_result, file_path="data/reviews.json"):
    """
    保存一次 LeetCode 复盘记录。

    输入：
        review_data: dict，用户原始输入信息
        review_text: str，AI 返回的复盘结果
        file_path: str，保存路径，默认是 data/reviews.json

    输出：
        review_record: dict，本次保存的完整复盘记录
    """
    path = Path(file_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        with path.open("r", encoding="utf-8-sig") as file:
            reviews = json.load(file)
    else:
        reviews = []

    review_record = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "problem_title": review_data["problem_title"],
        "problem_description": review_data["problem_description"],
        "user_code": review_data["user_code"],
        "confusion": review_data["confusion"],
        "review": review_result,
    }

    reviews.append(review_record)

    with path.open("w", encoding="utf-8") as file:
        json.dump(reviews, file, ensure_ascii=False, indent=2)

    return review_record