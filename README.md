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
main.py 是命令行版本的程序入口。

它先通过 collect_review_data() 收集用户输入，
生成 review_data 字典。

review_data 里包含：
- problem_title
- problem_description
- user_code
- confusion

然后 main.py 调用 build_review_prompt(review_data)，
把这些结构化数据转换成适合发给大模型的 prompt。

接着调用 call_llm(review_prompt)，
由 llm_client.py 负责请求大模型并返回 review_text。

之后调用 parse_review_text(review_text)，
由 review_parser.py 把大模型原始输出包装成 review_result。

最后调用 save_review(review_data, review_result)，
由 storage.py 把本次输入和复盘结果保存到 data/reviews.json。

5.19日：
    storage.py 现在负责复盘记录的读写。
save_review 用来保存新记录：
它读取旧 reviews 列表，append 新 review_record，再写回 JSON 文件。
load_reviews 用来读取历史记录：
它把 reviews.json 读成 Python 列表，供 app.py 展示侧边栏历史复盘。
app.py 负责前端展示，所以侧边栏历史记录逻辑放在 app.py。
llm_client.py 的调用流程没有因为历史记录展示而改变。

format_created_at：
把保存时的 ISO 时间字符串转换成适合展示的短时间格式。

shorten_text：
避免历史记录标题太长，撑乱侧边栏。

build_history_label：
把一条 record 转换成侧边栏里可读的选项文本。

render_recent_reviews：
读取历史记录，取最近 8 条，生成 label 和 record 的映射关系，
让用户在侧边栏选择，并返回 selected_record。

render_selected_review：
接收 selected_record，在主页面展示这条历史复盘的完整内容。