import requests

BASE = "http://127.0.0.1:5001"

payload = {
    "student": {
        "stream": "Physical Science",
        "subjects": [
            "Combined Mathematics",
            "Physics",
            "Information & Communication Technology",
        ],
        "zscore": None,
        "interests": "software engineering",
    },
    "district": "Colombo",
    "max_results": 100,
    "above_score_count": 50,
}

try:
    resp = requests.post(f"{BASE}/recommend", json=payload, timeout=60)
    data = resp.json()

    print(f"Total courses: {len(data)}")
    for c in data[:10]:
        print(
            f"[{c['course_code']}] {c['course_name']} - Eligible: {c.get('eligibility')} - Score: {c.get('score')}"
        )
except Exception as e:
    print(f"Error connecting to server: {e}")
