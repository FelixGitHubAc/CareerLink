import os
import requests
from typing import List, Dict, Any
from urllib.parse import quote

CAREERONESTOP_USER_ID = os.environ.get("CAREERONESTOP_USER_ID")  
CAREERONESTOP_API_KEY = os.environ.get("CAREERONESTOP_API_KEY")  

def _format_courses(items) -> List[Dict[str, Any]]:
    out = []
    for c in items:
        out.append({
            "name": c.get("ProgramName") or "Training Program",
            "provider": c.get("SchoolName") or "",
            "city": c.get("City") or "",
            "state": c.get("StateAbbr") or "",
            "url": c.get("SchoolUrl") or "",
        })
    return out

def search_training(keyword: str, location: str, limit: int = 5, radius_miles: int = 50) -> List[Dict[str, Any]]:
    """Use CareerOneStop Training API (if keys present). Returns empty if not configured."""
    if not CAREERONESTOP_API_KEY or not CAREERONESTOP_USER_ID:
        return []
    try:
        # CareerOneStop Training API route template:
        # /v1/training/{userId}/{keyword}/{location}/{radius}/{occupation}/{programName}/{programLength}/{state}/{region}/{sortColumns}/{sortDirections}/{startRecord}/{limitRecord}
        path = f"/v1/training/{quote(CAREERONESTOP_USER_ID)}/{quote(keyword)}/{quote(location)}/{radius_miles}/0/0/0/0/0/0/0/0/{limit}"
        url = "https://api.careeronestop.org" + path
        headers = {"Authorization": f"Bearer {CAREERONESTOP_API_KEY}"}
        r = requests.get(url, headers=headers, timeout=12)
        if r.ok:
            data = r.json()
            items = data.get("SchoolPrograms", [])[:limit]
            return _format_courses(items)
    except Exception:
        pass
    return []
