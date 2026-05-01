from scholarship_loan_matcher_ml.prediction.predict import run_prediction, _json_safe
from scholarship_loan_matcher_ml.pipeline.get_stats import get_dataset_stats
from scholarship_loan_matcher_ml.pipeline.update_pipeline import run_full_update
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure the project root (which contains the scholarship_loan_matcher_ml package)
# is on sys.path so this file works both when run as a script and as a module.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


class MatchRequest(BaseModel):
    profile: Dict[str, Any]
    top_n: int = 5
    match_type: Optional[str] = None


def _build_allowed_origins() -> List[str]:
    default_origins = ",".join(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    origins_str = os.getenv("CORS_ORIGINS") or default_origins
    return [o.strip() for o in origins_str.split(",") if o.strip()]


app = FastAPI(
    title="Scholarship & Loan Matcher Service",
    version="1.0.0",
    description="FastAPI wrapper around scholarship_loan_matcher_ml match engine.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "scholarship-loan-matcher"}


@app.post("/match")
def match_scholarships_and_loans(req: MatchRequest) -> Dict[str, Any]:
    profile = req.profile or {}
    if not profile:
        raise HTTPException(
            status_code=400, detail="Student profile payload is required.")

    top_n = req.top_n or 5
    if top_n <= 0:
        top_n = 5

    try:
        raw_results = run_prediction(profile, top_n=top_n)
    except ValueError as e:
        # Validation-type errors (e.g. empty profile text)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    combined = raw_results.get("combined") or raw_results.get("results") or []
    scholarships = raw_results.get("scholarships") or []
    loans = raw_results.get("loans") or []

    # Normalise match_type (can come from payload or request envelope)
    match_type = (req.match_type or profile.get(
        "match_type") or "").strip().lower()
    if match_type.endswith("s"):
        match_type = match_type[:-1]

    if match_type == "scholarship":
        matches = scholarships or [
            rec for rec in combined if (rec.get("record_type") in (None, "", "scholarship"))
        ]
    elif match_type == "loan":
        matches = loans or [
            rec for rec in combined if rec.get("record_type") == "loan"]
    else:
        # No type filter – return the top combined list (or fallback to concatenated lists)
        matches = combined or (scholarships + loans)

    safe_matches = _json_safe(matches)
    return {"matches": safe_matches, "count": len(safe_matches)}


@app.get("/matcher/update-datasets/stats")
def dataset_stats() -> Dict[str, Any]:
    """Return dataset statistics (scholarships/loans counts, last_updated) for the public and admin UI."""
    stats = get_dataset_stats()
    return {"success": True, **_json_safe(stats)}


@app.post("/matcher/update-datasets")
def trigger_dataset_update() -> Dict[str, Any]:
    """Run the full update pipeline (scrapers → cleaners) and return summary."""
    try:
        summary = run_full_update()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset update failed: {e}")
    updated_at = (summary.get("completed_at") or summary.get("last_update")) if summary else None
    if not updated_at:
        from datetime import datetime
        updated_at = datetime.now().isoformat()
    return {
        "success": True,
        "updated_at": updated_at,
        "summary": _json_safe(summary) if summary else {},
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "5005"))
    # Important: keep reload disabled for long-running update jobs.
    # The dataset pipeline writes files under this project; with reload enabled,
    # those file changes can trigger a server restart mid-request and the browser
    # sees a network/CORS-style failure even though the update actually finished.
    reload_enabled = os.getenv("UVICORN_RELOAD", "false").lower() == "true"
    # Use the fully-qualified module path so this works when run as
    # `python -m scholarship_loan_matcher_ml.api_service`.
    uvicorn.run("scholarship_loan_matcher_ml.api_service:app",
                host="0.0.0.0", port=port, reload=reload_enabled)
