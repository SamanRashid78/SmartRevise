// main.js —frontend logic

let selectedMode = "all";
let currentData = null;  

document.querySelectorAll(".mode-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    selectedMode = btn.dataset.mode;
  });
});

const textArea = document.getElementById("studyText");
const charCount = document.getElementById("charCount");

textArea.addEventListener("input", () => {
  const len = textArea.value.length;
  charCount.textContent = `${len.toLocaleString()} / 10,000 characters`;
  charCount.style.color = len > 9000 ? "#e05c5c" : "";
});

const loadingMessages = [
  "Analyzing your notes...",
  "Extracting key ideas...",
  "Generating questions...",
  "Almost done..."
];
let loadingTimer = null;

function showLoading() {
  const overlay = document.getElementById("loadingOverlay");
  const msg = document.getElementById("loadingMsg");
  overlay.classList.remove("hidden");
  msg.textContent = loadingMessages[0];

  let i = 1;
  loadingTimer = setInterval(() => {
    if (i < loadingMessages.length) {
      msg.textContent = loadingMessages[i++];
    }
  }, 1800);
}

function hideLoading() {
  clearInterval(loadingTimer);
  document.getElementById("loadingOverlay").classList.add("hidden");
}

async function processText() {
  const text = textArea.value.trim();
  const errorBox = document.getElementById("errorBox");

  
  errorBox.classList.add("hidden");
  document.getElementById("outputArea").classList.add("hidden");

  if (!text) {
    showError("Please paste some study material first.");
    return;
  }

  const btn = document.getElementById("processBtn");
  btn.disabled = true;

  showLoading();

  try {
    const res = await fetch("/api/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, mode: selectedMode })
    });

    const json = await res.json();

    if (!res.ok || !json.success) {
      throw new Error(json.error || "Unknown error occurred.");
    }

    currentData = json.data;
    renderOutput(json.data, json.mode);

  } catch (err) {
    showError(err.message || "Something went wrong. Please try again.");
    console.error(err);
  } finally {
    hideLoading();
    btn.disabled = false;
  }
}

function renderOutput(data, mode) {
  const outputArea = document.getElementById("outputArea");
  outputArea.classList.remove("hidden");

  hide("summarySection");
  hide("conceptsSection");
  hide("quizSection");

  if (data.summary) renderSummary(data.summary);
  if (data.concepts) renderConcepts(data.concepts);
  if (data.questions) renderQuiz(data.questions);

  // Smooth scroll to results
  outputArea.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderSummary(summary) {
  document.getElementById("summaryContent").textContent = summary;
  show("summarySection");
}

function renderConcepts(concepts) {
  const container = document.getElementById("conceptsContent");
  container.innerHTML = "";

  concepts.forEach(c => {
    const card = document.createElement("div");
    card.className = "concept-card";
    card.innerHTML = `
      <div class="concept-term">${escapeHTML(c.term)}</div>
      <div class="concept-def">${escapeHTML(c.definition)}</div>
    `;
    container.appendChild(card);
  });

  show("conceptsSection");
}

function renderQuiz(questions) {
  const container = document.getElementById("quizContent");
  container.innerHTML = "";

  // Reset score display
  document.getElementById("quizScore").classList.add("hidden");

  questions.forEach((q, idx) => {
    const qDiv = document.createElement("div");
    qDiv.className = "quiz-question";
    qDiv.dataset.answer = q.answer;
    qDiv.dataset.qid = idx;

    const optionsHTML = Object.entries(q.options).map(([key, val]) => `
      <label class="option-item" data-key="${key}">
        <input type="radio" name="q${idx}" value="${key}" />
        <span class="option-label"><span class="opt-key">${key}.</span> ${escapeHTML(val)}</span>
      </label>
    `).join("");

    qDiv.innerHTML = `
      <div class="question-text">
        <span class="question-num">Q${idx + 1}.</span> ${escapeHTML(q.question)}
      </div>
      <div class="options-list">${optionsHTML}</div>
      <div class="explanation">${escapeHTML(q.explanation || "")}</div>
    `;

    container.appendChild(qDiv);
  });

  show("quizSection");
}

function checkAnswers() {
  const questions = document.querySelectorAll(".quiz-question");
  let correct = 0;
  let answered = 0;

  questions.forEach(qDiv => {
    const correctAnswer = qDiv.dataset.answer;
    const selected = qDiv.querySelector("input[type='radio']:checked");
    const explanation = qDiv.querySelector(".explanation");

    if (!selected) return;
    answered++;

    const selectedKey = selected.value;
    const options = qDiv.querySelectorAll(".option-item");

    options.forEach(opt => {
      const key = opt.dataset.key;
      if (key === correctAnswer) opt.classList.add("correct");
      else if (key === selectedKey && selectedKey !== correctAnswer) opt.classList.add("wrong");
    });

    if (selectedKey === correctAnswer) correct++;

    explanation.classList.add("show");

    qDiv.querySelectorAll("input[type='radio']").forEach(r => r.disabled = true);
  });

  if (answered === 0) {
    alert("Please answer at least one question first.");
    return;
  }

  const scoreEl = document.getElementById("quizScore");
  scoreEl.textContent = `Score: ${correct} / ${answered}`;
  scoreEl.classList.remove("hidden");
}

function exportContent() {
  if (!currentData) return;

  let output = "SMART STUDY ASSISTANT — STUDY SET\n";
  output += "=".repeat(40) + "\n\n";

  if (currentData.summary) {
    output += "SUMMARY\n" + "-".repeat(30) + "\n";
    output += currentData.summary + "\n\n";
  }

  if (currentData.concepts) {
    output += " KEY CONCEPTS\n" + "-".repeat(30) + "\n";
    currentData.concepts.forEach(c => {
      output += `• ${c.term}: ${c.definition}\n`;
    });
    output += "\n";
  }

  if (currentData.questions) {
    output += " QUIZ QUESTIONS\n" + "-".repeat(30) + "\n";
    currentData.questions.forEach((q, i) => {
      output += `\nQ${i + 1}. ${q.question}\n`;
      Object.entries(q.options).forEach(([k, v]) => {
        output += `   ${k}. ${v}\n`;
      });
      output += `Answer: ${q.answer}\n`;
      if (q.explanation) output += `Explanation: ${q.explanation}\n`;
    });
  }

  const blob = new Blob([output], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "study-set.txt";
  a.click();
  URL.revokeObjectURL(url);
}

function showError(msg) {
  const box = document.getElementById("errorBox");
  box.textContent = msg;
  box.classList.remove("hidden");
}

function show(id) { document.getElementById(id).classList.remove("hidden"); }
function hide(id) { document.getElementById(id).classList.add("hidden"); }

function escapeHTML(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
