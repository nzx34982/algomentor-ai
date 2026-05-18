# AlgoMentor AI

AlgoMentor AI 是一个面向 LeetCode 学习的代码复盘助手。

当前版本目标：用户输入题目、题目描述、自己的 Python 代码和困惑，程序生成一份结构化复盘结果，并保存到本地 JSON 文件。

---

## 当前版本：V0.1

V0.1 已完成最小闭环：

1. 从终端收集 LeetCode 题目信息
2. 根据用户输入构造 AI Prompt
3. 调用大模型 API，或使用 mock 模式模拟 AI 回复
4. 对 AI 回复进行简单包装
5. 将复盘记录保存到 `data/reviews.json`

---

## 项目结构

```text
algomentor-ai/
├── main.py
├── llm_client.py
├── prompt_builder.py
├── review_parser.py
├── storage.py
├── data/
│   └── reviews.json
└── README.md