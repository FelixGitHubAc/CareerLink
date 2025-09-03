# CareerLink: Your personal Career Coach Chatbot

## My Project
This project is a Python + Flask web application that provides a simple career-coaching chatbot experience. It uses spaCy for lightweight natural language processing to detect user intents and extract keywords, and integrates with an external Job API (Adzuna) to fetch real-time job postings and a Job Training API to fetch real-time trainings near user's location. If no API keys are provided, the app falls back to demo data. The frontend is a clean, chat interface built with JavaScript.

## Features
* Python + Flask backend with REST endpoints and chat interface
* spaCy NLP for intent detection and entity extraction
* Jobs API integration: supports Adzuna
* Job Training API Integreation: supports CareerOneStop 
* Fallback demo mode if no API keys are provided
* Frontend UI: lightweight single-page chat built in JavaScript.

## How to run locally
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env  # if you would like to add your keys I also included demo data
python app.py
# open http://localhost:5000

## Configure APIs
- **CareerOneStop Training**: set `CAREERONESTOP_USER_ID` and `CAREERONESTOP_API_KEY`. API regisitration: `https://www.careeronestop.org/Developers/WebAPI/registration.aspx?utm_source=chatgpt.com`
- **Adzuna**: set `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`. Endpoint: `https://api.adzuna.com/v1/api/jobs/{country}/search/1`. API registration: `https://developer.adzuna.com/overview`





