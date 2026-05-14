from flask import Flask, render_template, request, jsonify
import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# setup anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_text():
    data = request.get_json()
    text = data.get("text", "")
    mode = data.get("mode", "all")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # basic validation
    if len(text) < 50:
        return jsonify({"error": "Please enter more text (at least 50 characters)"}), 400

    # build prompt based on what the user wants
    if mode == "summary":
        prompt = f"""Summarize the following study material in around 150-200 words. Use bullet points if it helps.

Text:
{text}

Reply ONLY with a JSON object like this (no extra text or markdown):
{{"summary": "your summary here"}}"""

    elif mode == "concepts":
        prompt = f"""Extract 5 to 7 key terms and their definitions from the text below.

Text:
{text}

Reply ONLY with a JSON object like this (no extra text):
{{"concepts": [{{"term": "term here", "definition": "definition here"}}]}}"""

    elif mode == "quiz":
        prompt = f"""Make 5 multiple choice questions based on the text below.
Each question needs 4 options (A B C D), one correct answer, and a short explanation.

Text:
{text}

Reply ONLY with a JSON object like this (no extra text):
{{"questions": [{{"question": "question here", "options": {{"A": "option", "B": "option", "C": "option", "D": "option"}}, "answer": "A", "explanation": "why A is correct"}}]}}"""

    else:
        # default: generate everything
        prompt = f"""Analyze the study material below and return:
1. A summary (150-200 words)
2. 5 to 7 key concepts with definitions
3. 5 multiple choice questions with 4 options, correct answer, and explanation

Text:
{text}

Reply ONLY with a JSON object (no markdown, no extra text):
{{
  "summary": "summary here",
  "concepts": [{{"term": "term", "definition": "definition"}}],
  "questions": [{{"question": "q", "options": {{"A": "a", "B": "b", "C": "c", "D": "d"}}, "answer": "A", "explanation": "explanation"}}]
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        raw = response.content[0].text

        # sometimes the model wraps in markdown code blocks, strip that
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw.strip())
        return jsonify({"success": True, "data": result})

    except json.JSONDecodeError:
        return jsonify({"error": "Couldnt parse the response, try again"}), 500
    except Exception as e:
        print("something went wrong:", e)
        return jsonify({"error": "Something went wrong on the server"}), 500


if __name__ == "__main__":
    app.run(debug=True)
