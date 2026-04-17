from flask import Flask, render_template, request, jsonify
import anthropic
import json
import os
from dotenv import load_dotenv
 
load_dotenv()
 
app = Flask(__name__)
 
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
 
    if len(text) < 50:
        return jsonify({"error": "Please provide more text"}), 400

    if mode == "summary":
        prompt = f"""Summarize the following study material in 150-200 words. Use bullet points where useful.
 
Text:
{text}
 
Reply ONLY with a JSON object like this (no extra text):
{{"summary": "your summary here"}}"""
 
    elif mode == "concepts":
        prompt = f"""Extract 5-7 key terms and definitions from the following text.
 
Text:
{text}
 
Reply ONLY with a JSON object like this (no extra text):
{{"concepts": [{{"term": "term here", "definition": "definition here"}}]}}"""
 
    elif mode == "quiz":
        prompt = f"""Create 5 multiple choice questions from the following study material.
Each question should have 4 options (A B C D) and one correct answer.
 
Text:
{text}
 
Reply ONLY with a JSON object like this (no extra text):
{{"questions": [{{"question": "question here", "options": {{"A": "option", "B": "option", "C": "option", "D": "option"}}, "answer": "A", "explanation": "why A is correct"}}]}}"""
 
    else:
        prompt = f"""Analyze the following study material and give me:
1. A summary (150-200 words)
2. 5-7 key concepts with definitions
3. 5 multiple choice questions with answers
 
Text:
{text}
 
Reply ONLY with a JSON object (no extra text, no markdown):
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
 
        response_text = response.content[0].text
        
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
 
        result = json.loads(response_text.strip())
        return jsonify({"success": True, "data": result})
 
    except json.JSONDecodeError:

        return jsonify({"error": "Failed to parse response, try again"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong"}), 500
 
 
if __name__ == "__main__":
    app.run(debug=True)
