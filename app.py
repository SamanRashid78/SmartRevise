from flask import Flask, render_template, request, jsonify
import anthropic
import json
import os
from dotenv import load_dotenv
import PyPDF2
import docx
import io

load_dotenv()

app = Flask(__name__)

# 16MB max upload size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# setup anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


def extract_text_from_pdf(file_bytes):
    """Extract text from a PDF file."""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print("PDF extraction error:", e)
        return None


def extract_text_from_docx(file_bytes):
    """Extract text from a Word document."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()
    except Exception as e:
        print("DOCX extraction error:", e)
        return None


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Handle file upload and extract text from PDF or DOCX."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = file.filename.lower()
    file_bytes = file.read()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
        if not text:
            return jsonify({"error": "Could not extract text from PDF. Make sure it is not a scanned image."}), 400

    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
        if not text:
            return jsonify({"error": "Could not extract text from Word document."}), 400

    elif filename.endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8").strip()
        except Exception:
            return jsonify({"error": "Could not read text file."}), 400

    else:
        return jsonify({"error": "Unsupported file type. Please upload a PDF, DOCX, or TXT file."}), 400

    if len(text) < 50:
        return jsonify({"error": "Not enough text found in the file. Try a different file."}), 400

    # truncate if too long to avoid token overflow
    if len(text) > 8000:
        text = text[:8000] + "\n\n[Document truncated to first 8000 characters]"

    return jsonify({"success": True, "text": text})


@app.route("/api/process", methods=["POST"])
def process_text():
    data = request.get_json()
    text = data.get("text", "")
    mode = data.get("mode", "all")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if len(text) < 50:
        return jsonify({"error": "Please enter more text (at least 50 characters)"}), 400

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
