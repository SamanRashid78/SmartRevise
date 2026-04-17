# SmartRevise 
An AI-powered web application that transforms study material into structured learning content, summaries, key concepts, and quiz questions.
# Features
Summarization:
Paste your notes and get a concise, structured summary
Key Concepts:
Automatically extracts important terms and definitions
MCQ Generator:
Creates multiple-choice questions to test your understanding
Export:
Download your study set as a text file
# How to run it
1. Clone the repo
2. Install dependencies:
pip install -r requirements.txt
3. Create a .env file and add your Anthropic API key:
ANTHROPIC_API_KEY=your_key_here
4. Run the app:
python app.py
Go to http://localhost:5000 in your browser
# Tech used
Python / Flask (backend)
HTML, CSS, JavaScript (frontend)
Anthropic Claude API (for AI processing)
# Project structure
smart-revise/
├── app.py
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/main.js
# Notes
This project is still in progress
PDF upload not implemented yet
Tested on Chrome 
