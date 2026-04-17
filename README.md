# SmartRevise 
An AI-powered web application that transforms study material into structured learning content, summaries, key concepts, and quiz questions.
# Features
Summarization – Paste your notes and get a concise, structured summary
Key Concepts – Automatically extracts important terms and definitions
MCQ Generator – Creates multiple-choice questions to test your understanding
Export – Download your study set as a text file

# Tech Stack
Frontend: HTML, CSS, JavaScript 
Backend: Python 

# Project Structure
```
smart-study-assistant/
│
├── app.py                  # Flask backend + API routes
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md
│
├── templates/
│   └── index.html          # Main UI
│
└── static/
    ├── css/
    │   └── style.css       # Styling
    └── js/
        └── main.js         # Frontend logic
```
# Setup & Installation
1. Clone the repo
```bash
git clone https://github.com/yourusername/smartrevise.git
cd smartrevise
```
2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Run the app
```bash
python app.py
```

# Future Improvements
Add PDF/DOCX file upload support
User accounts + saved study sessions
Flashcard mode
Spaced repetition scheduling

