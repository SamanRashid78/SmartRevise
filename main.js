// main.js — SmartRevise frontend logic

var selectedMode = "all";
var lastResult = null;

// mode button switching
document.querySelectorAll(".mode-btn").forEach(function(btn) {
  btn.addEventListener("click", function() {
    document.querySelectorAll(".mode-btn").forEach(function(b) {
      b.classList.remove("active");
    });
    btn.classList.add("active");
    selectedMode = btn.dataset.mode;
  });
});

// character counter
document.getElementById("studyText").addEventListener("input", function() {
  var len = this.value.length;
  document.getElementById("charCount").textContent = len + " characters";
});


async function processText() {
  var text = document.getElementById("studyText").value.trim();

  document.getElementById("errorMsg").classList.add("hidden");
  document.getElementById("results").classList.add("hidden");

  if (text === "") {
    showError("Please paste some text first.");
    return;
  }

  document.getElementById("generateBtn").disabled = true;
  document.getElementById("loading").classList.remove("hidden");

  try {
    var response = await fetch("/api/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, mode: selectedMode })
    });

    var json = await response.json();

    if (!json.success) {
      throw new Error(json.error || "Unknown error");
    }

    lastResult = json.data;
    showResults(json.data);

  } catch (err) {
    showError(err.message || "Something went wrong, please try again.");
  }

  document.getElementById("generateBtn").disabled = false;
  document.getElementById("loading").classList.add("hidden");
}


function showError(msg) {
  var el = document.getElementById("errorMsg");
  el.textContent = msg;
  el.classList.remove("hidden");
}


function showResults(data) {
  document.getElementById("summaryBox").classList.add("hidden");
  document.getElementById("conceptsBox").classList.add("hidden");
  document.getElementById("quizBox").classList.add("hidden");

  // summary
  if (data.summary) {
    document.getElementById("summaryText").textContent = data.summary;
    document.getElementById("summaryBox").classList.remove("hidden");
  }

  // key concepts
  if (data.concepts && data.concepts.length > 0) {
    var html = "";
    for (var i = 0; i < data.concepts.length; i++) {
      var c = data.concepts[i];
      html += '<div class="concept-item">';
      html += '<div class="term">' + c.term + '</div>';
      html += '<div class="definition">' + c.definition + '</div>';
      html += '</div>';
    }
    document.getElementById("conceptsList").innerHTML = html;
    document.getElementById("conceptsBox").classList.remove("hidden");
  }

  // quiz
  if (data.questions && data.questions.length > 0) {
    document.getElementById("score").classList.add("hidden");

    var quizHtml = "";
    for (var i = 0; i < data.questions.length; i++) {
      var q = data.questions[i];
      quizHtml += '<div class="question-block" data-answer="' + q.answer + '" data-qid="' + i + '">';
      quizHtml += '<p>Q' + (i + 1) + '. ' + q.question + '</p>';

      var opts = ["A", "B", "C", "D"];
      for (var j = 0; j < opts.length; j++) {
        var key = opts[j];
        quizHtml += '<label class="option" data-key="' + key + '">';
        quizHtml += '<input type="radio" name="q' + i + '" value="' + key + '" />';
        quizHtml += ' ' + key + '. ' + q.options[key];
        quizHtml += '</label>';
      }

      quizHtml += '<div class="explanation-text">' + (q.explanation || "") + '</div>';
      quizHtml += '</div>';
    }

    document.getElementById("quizList").innerHTML = quizHtml;
    document.getElementById("quizBox").classList.remove("hidden");
  }

  document.getElementById("results").classList.remove("hidden");
  document.getElementById("results").scrollIntoView({ behavior: "smooth" });
}


function checkAnswers() {
  var questions = document.querySelectorAll(".question-block");
  var correct = 0;
  var answered = 0;

  questions.forEach(function(qDiv) {
    var correctAnswer = qDiv.dataset.answer;
    var selected = qDiv.querySelector("input:checked");

    if (!selected) return;
    answered++;

    var selectedVal = selected.value;

    qDiv.querySelectorAll(".option").forEach(function(opt) {
      if (opt.dataset.key === correctAnswer) {
        opt.classList.add("correct");
      } else if (opt.dataset.key === selectedVal) {
        opt.classList.add("wrong");
      }
      var inp = opt.querySelector("input");
      if (inp) inp.disabled = true;
    });

    if (selectedVal === correctAnswer) correct++;
    qDiv.querySelector(".explanation-text").classList.add("show");
  });

  if (answered === 0) {
    alert("Answer at least one question first!");
    return;
  }

  var scoreEl = document.getElementById("score");
  scoreEl.textContent = "Score: " + correct + " / " + answered;
  scoreEl.classList.remove("hidden");
}


function exportText() {
  if (!lastResult) return;

  var output = "SMARTREVISE — STUDY SET\n";
  output += "========================\n\n";

  if (lastResult.summary) {
    output += "SUMMARY\n-------\n";
    output += lastResult.summary + "\n\n";
  }

  if (lastResult.concepts) {
    output += "KEY CONCEPTS\n------------\n";
    lastResult.concepts.forEach(function(c) {
      output += "- " + c.term + ": " + c.definition + "\n";
    });
    output += "\n";
  }

  if (lastResult.questions) {
    output += "QUIZ\n----\n";
    lastResult.questions.forEach(function(q, i) {
      output += "\nQ" + (i + 1) + ". " + q.question + "\n";
      output += "A. " + q.options.A + "\n";
      output += "B. " + q.options.B + "\n";
      output += "C. " + q.options.C + "\n";
      output += "D. " + q.options.D + "\n";
      output += "Answer: " + q.answer + "\n";
    });
  }

  var blob = new Blob([output], { type: "text/plain" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "study-set.txt";
  a.click();
}
