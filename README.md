# Career Coach Chatbot (Flask + spaCy)

A resume‑worthy demo: a career‑coaching chatbot that extracts intent/keywords with spaCy, calls external APIs to fetch **job postings** and **training programs**, and serves an interactive web UI with Flask. Ready for deployment on **Heroku**.

## Features
- **Python + Flask** web app with a clean chat UI
- **spaCy** for lightweight NLP: intent keywords + entity extraction
- **Jobs API**: JSearch (RapidAPI) or Adzuna (configure either)
- **Training API**: CareerOneStop “Training Finder” for local courses/programs
- **Heroku-ready**: `Procfile`, `runtime.txt`, and `gunicorn`

## Quickstart (Local)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# (Recommended) Download spaCy model ahead of time to avoid first-run download
python -m spacy download en_core_web_sm
cp .env.example .env  # add your keys (optional, app runs with demo data)
python app.py
# open http://localhost:5000
```

## Configure APIs (optional but recommended)
- **JSearch (RapidAPI)**: set `RAPIDAPI_KEY`. The app will call `https://jsearch.p.rapidapi.com/search`.
- **Adzuna**: set `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`. Endpoint: `https://api.adzuna.com/v1/api/jobs/{country}/search/1`.
- **CareerOneStop Training**: set `CAREERONESTOP_USER_ID` and `CAREERONESTOP_API_KEY` (Bearer token).

If an API isn’t configured, the app falls back to safe demo data for jobs and skips training results.

## Deploy to Heroku
```bash
heroku login
heroku create your-career-coach --stack heroku-24
heroku buildpacks # Python buildpack auto-detected from requirements.txt
# Set config vars (replace values):
heroku config:set SECRET_KEY=prod-secret \
  RAPIDAPI_KEY=your_rapidapi_key \
  ADZUNA_APP_ID=your_adzuna_id ADZUNA_APP_KEY=your_adzuna_key \
  CAREERONESTOP_USER_ID=your_user_id CAREERONESTOP_API_KEY=your_token
git init && git add . && git commit -m "Initial deploy"
git branch -M main
heroku git:remote -a your-career-coach
git push heroku main
heroku open
```
> Note: Heroku no longer offers a free tier. Use **Eco** or **Basic** dynos for hobby deployments.

## How it works
- `app.py` loads spaCy (`en_core_web_sm`) to extract simple entities and keywords.
- The app detects coarse **intents** via keyword heuristics.
- For job search, it hits **JSearch** (RapidAPI) if `RAPIDAPI_KEY` is present; otherwise **Adzuna** if keys exist; otherwise shows demo roles.
- For training, it queries **CareerOneStop**'s Training API when keys are present.
- The frontend (`templates/index.html`) is a single‑page chat with vanilla JS.

## Resume bullets you can copy
- Developed and deployed a career‑coaching chatbot using Python, Flask, and spaCy.
- Integrated JSearch/Adzuna Jobs and CareerOneStop Training APIs to recommend relevant job postings and local training programs.
- Deployed on Heroku with a responsive, interactive Flask frontend and session‑based conversation context.

## Project structure
```
career-coach-bot/
├── app.py
├── services/
│   ├── jobs_api.py
│   └── training_api.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── requirements.txt
├── Procfile
├── runtime.txt
└── .env.example
```

## Extending ideas
- Add a tiny intent classifier (spaCy TextCategorizer) trained on your phrases.
- Store conversations in SQLite or Postgres (enable on Heroku) for analytics.
- Add filters in the UI (remote only, experience level, salary).
- Include a resume parser (e.g., upload PDF, extract skills).

---

**Security tip:** Never commit real API keys; keep them in `.env` (local) or Heroku Config Vars.
