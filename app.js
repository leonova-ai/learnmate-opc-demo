const state = {
  agent: "Star",
  nodes: [
    { title: "Coherence", summary: "观点之间要有清晰逻辑关系。", domain: "雅思写作" },
    { title: "Topic Sentence", summary: "段首句表达段落主旨。", domain: "段落结构" },
    { title: "Linking Words", summary: "连接词展示观点之间的关系。", domain: "语言表达" }
  ]
};

const agentReplies = {
  star: "Star：我们先不追求全做完。你现在只需要完成一个 15 分钟动作，先把注意力放回桌面。",
  ask: "Ask：如果不用“逻辑清楚”这四个字，你会怎样让别人看出 coherence 的作用？",
  mem: "Mem：这个点适合今天复习。先遮住解释，用自己的例子复述一次，再看原文。",
  data: "Data：你的薄弱点不是词汇量，而是段落关系表达。建议优先练 topic sentence 到 supporting idea 的连接。"
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

$("#todayDate").textContent = new Intl.DateTimeFormat("zh-CN", {
  month: "long",
  day: "numeric",
  weekday: "long"
}).format(new Date());

$$(".rail-btn").forEach((button) => {
  button.addEventListener("click", () => {
    $$(".rail-btn").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    $$(".view").forEach((view) => view.classList.remove("view-active"));
    $(`#${button.dataset.view}`).classList.add("view-active");
  });
});

$("#submitAnswer").addEventListener("click", () => {
  const answer = $("#answerInput").value.trim();
  const feedback = answer
    ? `Ask：你用了"${answer.slice(0, 18)}${answer.length > 18 ? "..." : ""}"。如果要让例子更像雅思写作，你会补哪一个连接词？`
    : "Ask：先写一个你自己的例子。标准答案不急，先看你怎么理解。";
  $("#aiFeedback").textContent = feedback;
  $("#aiFeedback").style.color = "#0c5f59";
  $("#aiFeedback").style.fontWeight = "800";
  
  // 更新完成度动画
  const rate = $("#completionRate");
  let current = parseInt(rate.textContent) || 67;
  const target = answer ? 78 : 67;
  animateProgress(rate, current, target);
  
  // 标记任务完成
  const tasks = $$(".task-list li");
  if (answer && tasks[0]) {
    tasks[0].classList.add("done");
  }
});

function animateProgress(element, from, to) {
  let current = from;
  const step = current < to ? 1 : -1;
  const timer = setInterval(() => {
    current += step;
    element.textContent = current + "%";
    if (current === to) clearInterval(timer);
  }, 20);
}

$$(".agent-card").forEach((card) => {
  card.addEventListener("click", () => {
    $$(".agent-card").forEach((item) => item.classList.remove("active-agent"));
    card.classList.add("active-agent");
    state.agent = card.querySelector("h2").textContent;
    appendBubble(agentReplies[card.dataset.agent], "ai");
  });
});

$("#chatForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = $("#chatInput");
  const text = input.value.trim();
  if (!text) return;
  appendBubble(text, "user");
  input.value = "";
  
  // 模拟 AI 思考延迟
  const thinking = appendBubble("...", "ai");
  window.setTimeout(() => {
    thinking.remove();
    const reply = state.agent === "Ask"
      ? "Ask：你说卡住了。是定义不清、例子不够，还是不知道如何迁移到题目里？"
      : state.agent === "Star"
      ? "Star：我们先不把状态当敌人。摆 5 分钟也可以，但回来后只做一道小题。"
      : state.agent === "Mem"
      ? "Mem：这个节点今天该复习了。先遮住解释，用自己的例子复述一次。"
      : "Data：你的薄弱点不是词汇量，而是段落关系表达。建议优先练 topic sentence。";
    appendBubble(reply, "ai");
  }, 600);
});

$("#analyzeMaterial").addEventListener("click", () => {
  const text = $("#materialText").value.trim();
  
  // 显示加载状态
  $("#nodeResult").innerHTML = '<p class="empty" style="color: #0c5f59; font-weight: 800;">正在解析知识节点...</p>';
  
  window.setTimeout(() => {
    const concepts = buildNodes(text);
    state.nodes = concepts;
    $("#nodeResult").innerHTML = concepts.map((node, idx) => `
      <article class="mini-node" style="animation: rise 360ms ${idx * 100}ms ease both;">
        <h4>${node.title}</h4>
        <p>${node.summary}</p>
        <small>${node.domain} · 已安排 D1 / D3 / D7 复习</small>
      </article>
    `).join("") + `
      <article class="mini-node" style="animation: rise 360ms 400ms ease both; border-left: 5px solid #0f8f83;">
        <h4>📝 生成练习题</h4>
        <p>下面哪一句最能体现 coherence？<br>A. I like technology. The weather is sunny.<br>B. Online learning is flexible because students can control their schedule.</p>
        <small style="color: #0f8f83;">推荐答案：B（明确因果关系）</small>
      </article>
    `;
  }, 800);
});

function appendBubble(text, type) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${type}`;
  bubble.textContent = text;
  $("#chatLog").appendChild(bubble);
  bubble.scrollIntoView({ behavior: "smooth", block: "end" });
}

function buildNodes(text) {
  const lower = text.toLowerCase();
  const nodes = [];
  if (lower.includes("coherence")) {
    nodes.push({ title: "Coherence", summary: "段落和观点要形成清晰逻辑链。", domain: "雅思写作" });
  }
  if (lower.includes("topic sentence")) {
    nodes.push({ title: "Topic Sentence", summary: "段首句承担段落主旨定位。", domain: "段落结构" });
  }
  if (lower.includes("linking")) {
    nodes.push({ title: "Linking Words", summary: "连接词让因果、转折、递进关系可见。", domain: "语言表达" });
  }
  if (!nodes.length) {
    nodes.push(
      { title: "核心概念", summary: "从材料中提炼出的主要学习对象。", domain: "通用" },
      { title: "易错条件", summary: "需要额外注意的限制或混淆点。", domain: "通用" }
    );
  }
  return nodes;
}
