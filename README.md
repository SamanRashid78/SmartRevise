# SmartRevise — AI Study Assistant

A web-based study tool that transforms your notes or uploaded documents into structured learning content. Paste text or upload a PDF/Word file, pick what you want, and get a summary, key concepts, and a scored quiz in seconds — powered by the Claude API.

---

## What It Does

- **Paste or Upload** — paste notes directly or upload a PDF, DOCX, or TXT file
- **Summary** — concise 150-200 word breakdown of the material
- **Key Concepts** — 5-7 important terms with definitions extracted automatically
- **Quiz** — 5 multiple choice questions with answers and explanations
- **Export** — download your full study set as a .txt file

---

## How It Works

1. User pastes text or uploads a document
2. Backend extracts text from the file (PDF via PyPDF2, DOCX via python-docx)
3. Extracted text is sent to Claude API with a structured prompt
4. Claude returns a JSON response with summary, concepts, and quiz questions
5. Frontend renders results in a clean, interactive UI

---

# Files
```
SmartRevise/
├── app.py              ← Flask backend, file extraction, Claude API calls
├── requirements.txt    ← dependencies
├── .gitignore
├── templates/
│   └── index.html      ← frontend UI
└── static/
├── css/
│   └── style.css   ← styling
└── js/
└── main.js     ← frontend logic
```
---

## How to Run

```bash
# 1. Clone the repo
git clone https://github.com/SamanRashid78/SmartRevise.git
cd SmartRevise

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a .env file with your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 4. Run the app
python app.py

# 5. Open in browser
# Go to http://localhost:5000
```

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python · Flask |
| AI | Anthropic Claude API (claude-sonnet-4) |
| PDF parsing | PyPDF2 |
| DOCX parsing | python-docx |
| Frontend | HTML · CSS · Vanilla JavaScript |

---

## Notes

- Scanned PDF images won't work — text-based PDFs only
- Documents are truncated at 8000 characters to stay within API limits
- Requires an Anthropic API key to run

## What I Learned

- Building a full-stack web app with a Python/Flask backend
- Integrating a third-party LLM API with structured prompt engineering
- Extracting and processing text from different file formats (PDF, DOCX)
- Designing a clean API contract between frontend and backend using JSON
