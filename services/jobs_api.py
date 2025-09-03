import os
import requests
from typing import List, Dict

ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")  # for JSearch (RapidAPI)

def _format_jobs(items) -> List[Dict]:
    out = []
    for j in items:
        title = j.get("title") or j.get("job_title") or j.get("position")
        company = (j.get("company", {}) or {}).get("display_name") or j.get("employer_name")
        loc = None
        if "location" in j and isinstance(j.get("location"), dict):
            loc = j["location"].get("display_name") or j["location"].get("city")
        elif j.get("job_city") or j.get("job_country"):
            loc = ", ".join([p for p in [j.get("job_city"), j.get("job_state"), j.get("job_country")] if p])
        url = j.get("redirect_url") or j.get("job_apply_link") or j.get("job_google_link") or j.get("job_post_url")
        out.append({
            "title": title or "Job",
            "company": company or "Company",
            "location": loc or j.get("location", ""),
            "url": url or "#"
        })
    return out

def search_jobs(query: str, location: str = "", limit: int = 5) -> List[Dict]:
    """Search jobs using JSearch if RAPIDAPI_KEY set, otherwise Adzuna, otherwise demo data."""
    # Prefer JSearch (RapidAPI)
    if RAPIDAPI_KEY:
        try:
            params = {
                "query": f"{query} {location}".strip(),
                "page": "1",
                "num_pages": "1"
            }
            headers = {
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            r = requests.get("https://jsearch.p.rapidapi.com/search", headers=headers, params=params, timeout=12)
            if r.ok:
                data = r.json()
                items = data.get("data", [])[:limit]
                return _format_jobs(items)
        except Exception:
            pass

    # Fallback: Adzuna (requires app id/key)
    if ADZUNA_APP_ID and ADZUNA_APP_KEY:
        try:
            country = os.environ.get("ADZUNA_COUNTRY", "us")
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "results_per_page": limit,
                "what": query,
                "where": location
            }
            r = requests.get(url, params=params, timeout=12)
            if r.ok:
                data = r.json()
                items = data.get("results", [])
                return _format_jobs(items)
        except Exception:
            pass
        
        # ...existing code...
    print("ADZUNA_APP_ID:", ADZUNA_APP_ID)
    print("ADZUNA_APP_KEY:", ADZUNA_APP_KEY)
    # ...existing code...

    # Last resort: demo data
    return [
        {"title": "Data Analyst (Entry Level)", "company": "Acme Corp", "location": "Remote (US)", "url": "#"},
        {"title": "Business Analyst", "company": "Globex", "location": "New York, NY", "url": "#"},
    ][:limit]
# what is limit? 