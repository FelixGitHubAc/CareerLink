import os
import re
from typing import List, Dict, Any
from flask import Flask, render_template, request, jsonify, session
import requests

# Load environment variables if .env is present (local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# --- NLP (spaCy) ---
import spacy

def load_nlp():
    """Try to load en_core_web_sm; if missing, download once at runtime."""
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        # Fallback: try to download model at runtime (works on local + most PaaS)
        try:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=False)
            return spacy.load("en_core_web_sm")
        except Exception:
            # Last resort: blank English pipeline (no NER), still functional
            return spacy.blank("en")

nlp = load_nlp()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "keysecretdefault")

# -------- Intent detection helpers ---------
INTENT_KEYWORDS = {
    "job_search": ["job", "opening", "role", "position", "hiring", "jobs", "vacancy"],
    "courses": ["course", "certificate", "training", "bootcamp", "class", "learn"],
    "skills": ["skill", "upskill", "improve", "strengths", "weakness"],
    "resume": ["resume", "cv", "curriculum vitae"],
    "interview": ["interview", "behavioral", "star method", "offer", "negotiat"],
    "salary": ["salary", "compensation", "pay", "band", "range"],
}

def detect_intent(text: str) -> str:
    t = text.lower()
    scores = {k: 0 for k in INTENT_KEYWORDS}
    #what is this line doing?
    for intent, kws in INTENT_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                scores[intent] += 1
    # choose the best nonzero score; default to generic coaching
    intent = max(scores, key=scores.get)
    return intent if scores[intent] > 0 else "coach"

def extract_entities(text: str) -> Dict[str, Any]:
    """Very light extraction of title/skills/location using spaCy entities + heuristics."""
    doc = nlp(text)
    location = None
    skills_or_title: List[str] = []

    # Use named entities for locations (GPE/LOC)
    for ent in getattr(doc, "ents", []):
        # where did gpe and loc come from?
        if ent.label_ in ("GPE", "LOC"):
            location = ent.text

    # Simple heuristic: collect NOUN/PROPN tokens as potential titles/skills
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop and len(token.text) > 2:
            skills_or_title.append(token.text)

    # clean duplicates
    clean = []
    seen = set()
    for w in skills_or_title:
        lw = w.lower()
        if lw not in seen:
            seen.add(lw)
            clean.append(w)

    return {
        "location": location,
        "keywords": clean[:6],
        "raw": text
    }

# -------- External services wrappers ---------
from services.jobs_api import search_jobs
from services.training_api import search_training

# -------- Core responder ---------
def respond(user_text: str) -> Dict[str, Any]:
    intent = detect_intent(user_text)
    entities = extract_entities(user_text)

    reply_lines: List[str] = []
    payload: Dict[str, Any] = {"jobs": [], "courses": []}

    if intent == "resume":
        reply_lines.append("Here’s a quick resume tune‑up checklist:\n"
                           "• Use a sharp, specific title (e.g., 'Data Analyst — SQL, Python, Excel').\n"
                           "• Lead bullets with strong verbs, quantify impact (%, $, time).\n"
                           "• Mirror the job description keywords.\n"
                           "• Keep to 1 page (early career) or 2 (experienced).\n"
                           "• Add a skills block with tools relevant to your target role.")
    elif intent == "interview":
        reply_lines.append("Use the STAR method for behavioral answers:\n"
                           "• Situation — set the context\n"
                           "• Task — what you had to achieve\n"
                           "• Action — what you did (focus on you)\n"
                           "• Result — numbers and outcomes\n"
                           "Tip: build a 5–7 story bank you can flex across questions.")
    elif intent == "salary":
        reply_lines.append("For salary research, triangulate:\n"
                           "• Public ranges in job posts\n"
                           "• Aggregators (levels.fyi/Glassdoor/OW) for your city\n"
                           "• Your unique value-add. Practice a script like:\n"
                           "“Based on market data for {role} in {city} and my experience with {skills}, "
                           "I’m targeting a base of $X–$Y. How does that align with your range?”")
    if intent in ("job_search", "coach"):
        q = " ".join(entities["keywords"]) or user_text
        loc = entities["location"] or os.environ.get("DEFAULT_LOCATION", "")
        if q.strip():
            jobs = search_jobs(query=q, location=loc, limit=5)
            if jobs:
                payload["jobs"] = jobs
                reply_lines.append(f"I pulled a few {q} roles{(' near ' + loc) if loc else ''}. "
                                   "Want me to refine by experience level or remote only?")
            else:
                reply_lines.append("I couldn’t find roles from the API right now. Try a different title or add a city.")
    if intent in ("courses", "skills", "coach"):
        skill = (entities["keywords"][0] if entities["keywords"] else None)
        loc = entities["location"] or os.environ.get("DEFAULT_LOCATION", "Boston, MA")
        key = skill or "career"
        courses = search_training(keyword=key, location=loc, limit=5, radius_miles=50)
        if courses:
            payload["courses"] = courses
            reply_lines.append(f"Here are some nearby training options related to “{key}”.")
        else:
            reply_lines.append("I couldn’t fetch training resources right now, but I can suggest online courses if you tell me a skill.")

    if not reply_lines:
        reply_lines.append("Tell me your target role, skills, and location—I'll fetch jobs and training to match.")

    return {"reply": "\n\n".join(reply_lines), **payload}

# -------- Routes ---------
@app.route("/", methods=["GET"])
# when is this route called?
def index():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html")

@app.route("/api/message", methods=["POST"])
def message():
    data = request.get_json(force=True)
    user_text = (data.get("message") or "").strip()
    if not user_text:
        return jsonify({"reply": "Say something like: “entry-level data analyst roles in Austin”"}), 200

    bot = respond(user_text)
    # save brief history
    hist_item = {"user": user_text, "bot": bot.get("reply", "")}
    session.setdefault("history", []).append(hist_item)
    session.modified = True

    return jsonify(bot), 200

# Health check
@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
