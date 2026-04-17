from flask import Flask, render_template, request, jsonify
import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Anthropic client
# Make sure ANTHROPIC_API_KEY is set in your .env file
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-20250514"


def build_prompt(text, mode):
    """Build different prompts based on the requested mode."""

    if mode == "summary":
        return f"""You are a study assistant. Read the following study material and produce a concise, 
well-structured summary. Use clear headings and bullet points where helpful. 
Keep it to 150-250 words.

Study material:
{text}

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{{
  "summary": "Your summary here with \\n for line breaks"
}}"""

    elif mode == "concepts":
        return f"""You are a study assistant. Extract the key concepts, terms, and definitions from the 
following study material. List 5-8 of the most important ones.

Study material:
{text}

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{{
  "concepts": [
    {{"term": "Term 1", "definition": "Definition of term 1"}},
    {{"term": "Term 2", "definition": "Definition of term 2"}}
  ]
}}"""

    elif mode == "quiz":
        return f"""You are a study assistant. Generate 5 multiple choice questions based on the following 
study material. Each question should have 4 options (A, B, C, D) with one correct answer.

Study material:
{text}

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "answer": "A",
      "explanation": "Brief explanation of why A is correct"
    }}
  ]
}}"""

    elif mode == "all":
        return f"""You are a study assistant. Analyze the following study material and produce:
1. A concise summary (150-200 words)
2. 5-7 key concepts with definitions
3. 5 multiple choice questions

Study material:
{text}

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{{
  "summary": "Your summary here",
  "concepts": [
    {{"term": "Term", "definition": "Definition"}}
  ],
  "questions": [
    {{
      "question": "Question?",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "answer": "A",
      "explanation": "Why A is correct"
    }}
  ]
}}"""

    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_text():
    data = request.get_json()

    text = data.get("text", "").strip()
    mode = data.get("mode", "all")  # summary | concepts | quiz | all

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if len(text) < 50:
        return jsonify({"error": "Text is too short. Please provide more content."}), 400

    if len(text) > 10000:
        return jsonify({"error": "Text is too long. Please keep it under 10,000 characters."}), 400

    prompt = build_prompt(text, mode)
    if not prompt:
        return jsonify({"error": "Invalid mode selected"}), 400

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Strip markdown code fences if present (Claude sometimes adds them)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        result = json.loads(response_text)
        return jsonify({"success": True, "data": result, "mode": mode})

    except json.JSONDecodeError as e:
        # TODO: add retry logic here — Claude occasionally returns malformed JSON
        print(f"JSON parse error: {e}")
        print(f"Raw response: {response_text}")
        return jsonify({"error": "Failed to parse AI response. Try again."}), 500

    except anthropic.APIError as e:
        print(f"Anthropic API error: {e}")
        return jsonify({"error": "AI service error. Check your API key."}), 503

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "model": MODEL})


if __name__ == "__main__":
    # Debug mode ON for development — turn off before any real deployment
    app.run(debug=True, port=5000)
