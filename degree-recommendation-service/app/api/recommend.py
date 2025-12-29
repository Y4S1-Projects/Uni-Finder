# app/api/recommend.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    """
    Simple ping endpoint to verify routing works.
    """
    return {"message": "Degree Recommendation API is reachable"}
