from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape
from typing import List, Tuple

import gradio as gr


@dataclass
class KnowledgeNode:
    title: str
    summary: str
    domain: str
    review: str


# ===== 隐私安全：所有个人标识已替换为比赛占位符 =====
COMPETITION_TAG = "OPC 2026 · 数字文化赛道"
TEAM_NAME = "Nova"
DEMO_VERSION = "v1.0 比赛演示版（本地规则引擎，无需 API）"

AGENT_COPY = {
    "Star 情绪搭子": "我们先把学习启动成本降下来。今天不用完美，只要完成一个能继续积累的小动作。",
    "Ask 追问导师": "先别急着背答案。你能用一个生活例子说明这个概念吗？如果换成考试作文，它对应哪一句？",
    "Mem 记忆管家": "这个节点适合今天复习。先遮住解释复述一次，再看原文校准，最后安排 D3 复现。",
    "Data 弱点分析": "当前薄弱点集中在段落逻辑，而不是单词量。优先处理 topic sentence 到 supporting idea 的连接。",
}

DEFAULT_MATERIAL = (
    "In academic writing, coherence means ideas are logically connected. "
    "A clear topic sentence helps the reader understand the paragraph's main point, "
    "while linking words show relationships between ideas such as cause-effect or contrast."
)


def infer_nodes(text: str) -> List[KnowledgeNode]:
    normalized = text.lower()
    nodes: List[KnowledgeNode] = []
    if "coherence" in normalized or "逻辑" in normalized:
        nodes.append(
            KnowledgeNode(
                "Coherence（连贯性）",
                "观点之间形成清晰、可追踪的逻辑链。",
                "学术写作",
                "D1 / D3 / D7",
            )
        )
    if "topic sentence" in normalized or "主题句" in normalized:
        nodes.append(
            KnowledgeNode(
                "Topic Sentence（主题句）",
                "段首句负责告诉读者这一段要证明什么。",
                "段落结构",
                "D1 / D3 / D7",
            )
        )
    if "linking" in normalized or "连接" in normalized:
        nodes.append(
            KnowledgeNode(
                "Linking Words（连接词）",
                "连接词显式标记因果、转折、递进等关系。",
                "语言表达",
                "D1 / D3 / D7",
            )
        )
    if "argument" in normalized or "论点" in normalized:
        nodes.append(
            KnowledgeNode(
                "Argument Structure（论点结构）",
                "主论点 + 支撑论据 + 反驳预判。",
                "逻辑构建",
                "D1 / D3",
            )
        )
    if not nodes:
        chunks = [item.strip() for item in text.replace("。", ".").split(".") if len(item.strip()) > 6]
        for idx, chunk in enumerate(chunks[:3], start=1):
            nodes.append(
                KnowledgeNode(
                    f"知识节点 {idx}",
                    chunk[:46] + ("..." if len(chunk) > 46 else ""),
                    "通用学习",
                    "D1 / D3",
                )
            )
    return nodes


def node_cards(nodes: List[KnowledgeNode]) -> str:
    cards = []
    for node in nodes:
        cards.append(
            f"""
            <article class="node-card">
              <div class="node-top">
                <span>{escape(node.domain)}</span>
                <strong>{escape(node.review)}</strong>
              </div>
              <h3>{escape(node.title)}</h3>
              <p>{escape(node.summary)}</p>
            </article>
            """
        )
    return '<div class="node-grid">' + "\n".join(cards) + "</div>"


def graph_html(nodes: List[KnowledgeNode]) -> str:
    titles = [node.title for node in nodes] or ["Coherence", "Topic Sentence", "Linking Words", "Argument", "Review Cue"]
    while len(titles) < 5:
        titles.append(["Paragraph Logic", "Error Pattern", "Review Cue", "Concept Map", "Knowledge Link"][len(titles) % 5])
    safe = [escape(title) for title in titles[:5]]
    return f"""
    <div class="graph-panel">
      <svg viewBox="0 0 760 420" class="graph-lines">
        <path d="M130 250 C250 110 430 130 570 210"></path>
        <path d="M210 320 C350 260 450 278 620 325"></path>
        <path d="M360 108 C405 200 420 260 475 330"></path>
      </svg>
      <button class="map-node n1">{safe[0]}</button>
      <button class="map-node n2">{safe[1]}</button>
      <button class="map-node n3">{safe[2]}</button>
      <button class="map-node n4">{safe[3]}</button>
      <button class="map-node n5">{safe[4]}</button>
    </div>
    """


def score_answer(answer: str) -> Tuple[str, str]:
    answer = answer.strip()
    if not answer:
        return (
            "💡 Ask：先写一个你自己的例子。标准答案不急，先看你怎么理解。",
            "67%",
        )
    length_score = min(40, len(answer) // 3)
    keyword_score = 30 if any(word in answer.lower() for word in ["logic", "逻辑", "connect", "连接", "段落", "结构"]) else 12
    example_score = 24 if any(word in answer for word in ["比如", "例如", "like", "for example", "假设"]) else 10
    total = min(96, length_score + keyword_score + example_score)
    feedback = (
        f"✅ Ask：你的解释已经有 {total}/100 的可用度。\n"
        f"🔍 下一步别补定义，先补一个“错误例子”：如果没有 coherence，读者会在哪里迷路？"
    )
    return feedback, f"{total}%"


def chat(agent: str, message: str, history: List[dict]) -> Tuple[List[dict], str]:
    message = message.strip()
    if not message:
        return history, ""
    history = history + [{"role": "user", "content": message}]
    
    # 智能路由回复（仍为本地规则，但更贴近真实对话）
    reply = AGENT_COPY.get(agent, AGENT_COPY["Star 情绪搭子"])
    lower_msg = message.lower()
    
    if any(w in lower_msg for w in ["焦虑", "摆烂", "累", "不想学", "放弃"]):
        reply = "🌟 Star：我们先不把状态当敌人。摆 5 分钟也可以，但回来后只做一道小题。"
    elif any(w in lower_msg for w in ["为什么", "解释", "不懂", "卡住"]):
        reply = AGENT_COPY["Ask 追问导师"]
    elif any(w in lower_msg for w in ["忘", "复习", "记不住", "遗忘"]):
        reply = AGENT_COPY["Mem 记忆管家"]
    elif any(w in lower_msg for w in ["错题", "薄弱", "错误", "错因"]):
        reply = AGENT_COPY["Data 弱点分析"]
    elif any(w in lower_msg for w in ["材料", "解析", "笔记", "文章"]):
        reply = "📄 Cut：请把材料粘贴到「资料解析」Tab，我会自动提取知识节点。"
    else:
        reply = f"{agent.split()[0]}：我收到了。下一步先做一件小事：把这个问题写成一句可复习的知识节点。"
        
    history.append({"role": "assistant", "content": reply})
    return history, ""


def analyze_material(text: str) -> Tuple[str, str, str, str]:
    text = text.strip() or DEFAULT_MATERIAL
    nodes = infer_nodes(text)
    quiz = (
        "📝 生成练习题：\n"
        "下面哪一句最能体现 coherence？\n\n"
        "A. I like technology. The weather is sunny.\n"
        "B. Online learning is flexible because students can control their schedule.\n"
        "C. Some people disagree. Many things happen.\n\n"
        "✅ 推荐答案：B。它用 because 明确展示因果关系，符合 coherence 定义。"
    )
    review = (
        "📅 间隔复习计划：\n"
        "• 今天（D1）：遮住解释，口头复述每个节点\n"
        "• 3 天后（D3）：用一个新例子解释 coherence\n"
        "• 7 天后（D7）：把 Topic Sentence 和 Linking Words 连成一段"
    )
    return node_cards(nodes), graph_html(nodes), quiz, review


def make_daily_brief() -> str:
    today = datetime.now().strftime("%m 月 %d 日")
    return f"""
    <section class="brief-card">
      <span class="brief-kicker">今日学习闭环 · {today}</span>
      <h2>先拿下一个能带来反馈的小任务</h2>
      <div class="brief-list">
        <div><strong>01</strong><span>完成 coherence 今日挑战</span></div>
        <div><strong>02</strong><span>复习 Topic Sentence 与 Linking Words</span></div>
        <div><strong>03</strong><span>分析 1 道段落逻辑错题</span></div>
      </div>
    </section>
    """


CSS = """
.gradio-container {
  background:
    radial-gradient(circle at 12% 8%, rgba(238, 106, 87, .18), transparent 25%),
    radial-gradient(circle at 86% 12%, rgba(15, 143, 131, .2), transparent 28%),
    linear-gradient(145deg, #f8fbf8 0%, #edf6f4 54%, #f7efe2 100%) !important;
  color: #182523;
  font-family: Avenir Next, Gill Sans, Trebuchet MS, sans-serif;
}
.demo-banner {
  text-align: center;
  padding: 12px;
  background: linear-gradient(90deg, #0c5f59, #0f8f83);
  color: white;
  font-weight: 800;
  border-radius: 16px;
  margin-bottom: 16px;
  font-size: 14px;
}
.main-title {
  padding: 26px 28px;
  border-radius: 28px;
  background: rgba(255,255,255,.72);
  border: 1px solid rgba(24,37,35,.1);
  box-shadow: 0 24px 80px rgba(26,58,55,.13);
}
.main-title h1 {
  font-size: clamp(36px, 6vw, 72px);
  line-height: .9;
  margin: 0 0 14px;
  letter-spacing: 0;
}
.main-title p {
  max-width: 900px;
  color: #697875;
  font-weight: 700;
  font-size: 16px;
}
.brief-card {
  min-height: 300px;
  padding: 32px;
  border-radius: 28px;
  color: #fff;
  background: linear-gradient(145deg, #182523, #0c5f59);
  box-shadow: 0 24px 80px rgba(26,58,55,.22);
}
.brief-kicker {
  display: inline-flex;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,.12);
  color: #d8f3e6;
  font-weight: 900;
  font-size: 13px;
}
.brief-card h2 {
  margin: 26px 0;
  font-size: clamp(28px, 4.5vw, 54px);
  line-height: .95;
}
.brief-list {
  display: grid;
  gap: 12px;
}
.brief-list div {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid rgba(255,255,255,.14);
}
.brief-list strong {
  color: #ee6a57;
  font-size: 18px;
}
.node-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}
.node-card {
  padding: 18px;
  border-radius: 22px;
  background: #fff;
  border: 1px solid rgba(24,37,35,.08);
  box-shadow: 0 16px 42px rgba(26,58,55,.1);
  transition: transform 0.2s ease;
}
.node-card:hover {
  transform: translateY(-4px);
}
.node-top {
  display: flex;
  justify-content: space-between;
  color: #0c5f59;
  font-size: 12px;
  font-weight: 900;
}
.node-card h3 {
  margin: 18px 0 8px;
  font-size: 22px;
}
.node-card p {
  color: #697875;
  font-weight: 700;
  line-height: 1.5;
}
.graph-panel {
  height: 400px;
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  background:
    radial-gradient(circle at 20% 24%, rgba(238,106,87,.16), transparent 24%),
    radial-gradient(circle at 78% 62%, rgba(15,143,131,.18), transparent 28%),
    linear-gradient(145deg, #fff, #edf6f4);
  border: 1px solid rgba(24,37,35,.08);
}
.graph-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.graph-lines path {
  fill: none;
  stroke: rgba(12,95,89,.28);
  stroke-width: 4;
  stroke-linecap: round;
}
.map-node {
  position: absolute;
  border: 0;
  border-radius: 999px;
  background: #fff;
  color: #182523;
  padding: 13px 17px;
  font-weight: 900;
  box-shadow: 0 16px 36px rgba(26,58,55,.14);
  cursor: default;
  transition: transform 0.2s;
}
.map-node:hover {
  transform: scale(1.08);
}
.map-node:before {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 8px;
  border-radius: 50%;
  background: #ee6a57;
}
.n1 { left: 7%; top: 52%; }
.n2 { left: 36%; top: 17%; }
.n3 { right: 11%; top: 40%; }
.n4 { left: 49%; bottom: 17%; }
.n5 { right: 7%; bottom: 12%; }
footer { display: none !important; }
"""


with gr.Blocks(title="LearnMate AI 备考学习搭子", css=CSS) as demo:
    gr.HTML(f'<div class="demo-banner">🏆 {DEMO_VERSION} · {COMPETITION_TAG} · {TEAM_NAME}</div>')
    
    gr.HTML(
        f"""
        <div class="main-title">
          <p>{COMPETITION_TAG} · {TEAM_NAME}</p>
          <h1>LearnMate AI 备考学习搭子</h1>
          <p>一个面向长期备考人群的 AI 学习工作台：用多 Agent 协作、资料解析、知识节点、错题分析与间隔复习，把每天的学习变成可执行闭环。</p>
        </div>
        """
    )

    with gr.Tab("📅 今日闭环"):
        gr.Markdown("**演示指引**：提交今日挑战回答，体验 Ask 苏格拉底式追问。无需 API，本地即时反馈。")
        with gr.Row():
            gr.HTML(make_daily_brief())
            with gr.Column():
                answer = gr.Textbox(
                    label="今日挑战",
                    lines=5,
                    placeholder="如果你要向 12 岁学生解释 coherence，你会怎么举例？",
                )
                answer_btn = gr.Button("提交给 Ask 追问", variant="primary")
                feedback = gr.Textbox(label="Ask 反馈", interactive=False, lines=3)
                score = gr.Textbox(label="当前可用度", value="67%", interactive=False)
        answer_btn.click(score_answer, inputs=answer, outputs=[feedback, score])

    with gr.Tab("🤖 多 Agent 对话"):
        gr.Markdown("**演示指引**：切换不同 Agent 角色，输入学习卡点，体验多角色协作流程。")
        with gr.Row():
            agent = gr.Radio(
                list(AGENT_COPY.keys()),
                value="Star 情绪搭子",
                label="选择学习搭子",
            )
            agent_note = gr.Markdown(
                "🌟 Star 接住情绪 → 💡 Ask 负责追问 → 📚 Mem 管复习 → 📊 Data 看弱点"
            )
        chatbot = gr.Chatbot(
            label="学习对话",
            value=[{"role": "assistant", "content": "🌟 Star：今天状态不用完美。你最想先解决写作结构还是口语表达？"}],
            height=380,
        )
        with gr.Row():
            user_msg = gr.Textbox(
                label="输入你的学习卡点",
                placeholder="比如：我总是忘记怎么写 topic sentence",
                scale=5,
            )
            send = gr.Button("发送", variant="primary", scale=1)
        send.click(chat, inputs=[agent, user_msg, chatbot], outputs=[chatbot, user_msg])

    with gr.Tab("📄 资料解析"):
        gr.Markdown("**演示指引**：粘贴任意学习材料，系统自动提取知识节点、生成练习题、安排复习计划、更新知识图谱。")
        material = gr.Textbox(
            label="学习材料",
            value=DEFAULT_MATERIAL,
            lines=7,
        )
        analyze = gr.Button("解析为知识节点", variant="primary")
        with gr.Row():
            nodes_html = gr.HTML(label="知识节点卡片")
            with gr.Column():
                quiz_box = gr.Textbox(label="生成练习题", lines=8, interactive=False)
                review_box = gr.Textbox(label="间隔复习计划", lines=6, interactive=False)
        graph = gr.HTML(label="个人知识图谱")
        analyze.click(analyze_material, inputs=material, outputs=[nodes_html, graph, quiz_box, review_box])

    with gr.Tab("📊 评测与说明"):
        gr.Markdown(
            f"""
            ## 🏆 OPC 2026 比赛演示评测指标
            
            | 指标 | 目标值 | 说明 |
            |------|--------|------|
            | 首次上手时间 | ≤90 秒 | 完成一次今日挑战或资料解析 |
            | 每日任务完成率 | ≥1 个/天 | 平均完成 1 个以上任务 |
            | 知识节点准确性 | ≥4/5 分 | 人工抽检节点质量 |
            | 追问质量 | 推动理解 | Ask 一次只问一个问题，不直接给答案 |
            | 闭环完整度 | 4 项齐全 | 节点+练习+复习+图谱 |
            | 降级可用性 | 无需 API | 静态 demo 可完整演示 |
            
            ## 🛡️ 隐私与安全
            - 本演示完全本地运行，不收集任何用户数据
            - 无外部 API 调用，无网络请求
            - 所有回复由本地规则引擎生成，适合比赛安全评审
            
            ## 📦 提交信息
            - 赛道：数字文化
            - 团队：{TEAM_NAME}
            - 版本：{DEMO_VERSION}
            """
        )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
